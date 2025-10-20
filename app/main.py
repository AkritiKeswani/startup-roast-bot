import os, signal, uuid, threading, time
from typing import Dict, List
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from .models import RunRequest, CompanyResult
from .logutil import jlog
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

RUNS: Dict[str, List[CompanyResult]] = {}
CLIENTS: Dict[str, List[WebSocket]] = {}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

shutdown = False
def _sigterm(*_): 
    global shutdown; shutdown = True
signal.signal(signal.SIGTERM, _sigterm)

@app.get("/health")
def health(): return {"ok": True}
@app.get("/ready")
def ready(): return {"ready": True}

@app.post("/run")
def start(req: RunRequest):
    run_id = f"rk_{uuid.uuid4().hex[:8]}"
    RUNS[run_id] = []
    threading.Thread(target=_runner, args=(run_id, req), daemon=True).start()
    return {"run_id": run_id, "status":"running", "stream_url": f"/stream/{run_id}"}

@app.get("/runs/{run_id}")
def get_run(run_id:str):
    return [r.model_dump() for r in RUNS.get(run_id, [])]

@app.websocket("/stream/{run_id}")
async def ws_stream(ws: WebSocket, run_id: str):
    await ws.accept()
    CLIENTS.setdefault(run_id, []).append(ws)
    try:
        while True:
            await ws.receive_text()  # keepalive pings from client are okay
    except Exception:
        pass
    finally:
        CLIENTS[run_id].remove(ws)

def emit(run_id:str, payload:dict):
    for ws in list(CLIENTS.get(run_id, [])):
        try: 
            import asyncio
            # Schedule the coroutine to run in the event loop
            asyncio.get_event_loop().call_soon_threadsafe(
                lambda: asyncio.create_task(ws.send_json(payload))
            )
        except: 
            pass

def _runner(run_id: str, req: RunRequest):
    import asyncio
    from . import browserbase_client as bb
    from .playwright_bridge import PW
    from .llm_client import generate_roast

    async def async_runner():
        try:
            jlog(message="Starting browser session", run_id=run_id)
            
            # Test API keys first
            if not os.environ.get("BROWSERBASE_API_KEY"):
                raise RuntimeError("BROWSERBASE_API_KEY not set")
            if not os.environ.get("BROWSERBASE_PROJECT_ID"):
                raise RuntimeError("BROWSERBASE_PROJECT_ID not set")
            if not os.environ.get("GROK_API_KEY"):
                raise RuntimeError("GROK_API_KEY not set")
                
            jlog(message="API keys validated")
            
            sess = bb.create_session({})
            jlog(message="Browserbase session created", session_id=sess.get("id"))
            
            ws = bb.connect_url(sess)
            jlog(message="Got connection URL", connect_url=ws[:50] + "...")
            
            async with PW(ws) as pw:
                jlog(message="Playwright connected to browser")
                
                # collect targets
                urls = []
                if req.source == "yc":
                    jlog(message="Scraping YC companies", batch=req.yc.batch, limit=req.yc.limit)
                    from .yc_scraper import list_profiles, profile_to_external
                    profs = await list_profiles(pw.page, req.yc.batch, req.yc.limit)
                    jlog(message="Found profiles", count=len(profs))
                    for purl in profs:
                        name, site = await profile_to_external(pw.page, purl)
                        if site: 
                            urls.append((name, site))
                            jlog(message="Found external site", name=name, site=site)
                else:
                    jlog(message="Using custom URLs", count=len(req.custom.urls))
                    for u in req.custom.urls:
                        urls.append((u.split("//")[-1], u))

                jlog(message="Starting to process sites", total=len(urls))
                results = []
                for i, (name, site) in enumerate(urls):
                    if shutdown: break
                    jlog(message="Processing site", index=i+1, name=name, site=site)
                    try:
                        await pw.goto(site)
                        jlog(message="Page loaded", site=site)
                        
                        summary = await pw.grab_summary()
                        jlog(message="Extracted summary", title=summary["title"][:50], hero=summary["hero"][:50])
                        
                        shot_path = f"/tmp/{run_id}_{uuid.uuid4().hex[:6]}.png"
                        await pw.screenshot(shot_path)
                        jlog(message="Screenshot taken", path=shot_path)
                        
                        with open(shot_path, "rb") as f: 
                            png = f.read()
                        # Convert to base64 data URL for immediate use
                        import base64
                        b64 = base64.b64encode(png).decode()
                        screenshot_url = f"data:image/png;base64,{b64}"
                        
                        jlog(message="Generating roast", style=req.style)
                        roast = generate_roast(summary, req.style)
                        jlog(message="Roast generated", roast=roast[:100])
                        
                        item = CompanyResult(
                            name=name, website=site, title=summary["title"],
                            hero=summary["hero"], cta=summary["cta"],
                            roast=roast, screenshot_url=screenshot_url
                        )
                        results.append(item)
                        RUNS[run_id].append(item)
                        emit(run_id, {"company":{"name":name,"website":site},
                                      "roast":roast, "screenshot_url":screenshot_url, "status":"done"})
                        jlog(message="Result emitted", name=name)
                    except Exception as e:
                        jlog(message="Error processing site", name=name, error=str(e))
                        item = CompanyResult(name=name, website=site, status="skipped", reason=str(e))
                        results.append(item)
                        RUNS[run_id].append(item)
                        emit(run_id, {"company":{"name":name,"website":site},
                                      "status":"skipped","reason":str(e)})
                    await asyncio.sleep(0.2)

                jlog(message="Run completed", total_results=len(results))
                emit(run_id, {"status":"finished"})
        except Exception as e:
            jlog(message="Fatal error in runner", error=str(e), run_id=run_id)
            emit(run_id, {"status":"error","error":str(e)})
    
    # Run the async function in a new event loop
    asyncio.run(async_runner())