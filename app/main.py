"""
Startup Roast Bot - FastAPI Backend
A production-grade agent that roasts startup websites using Browserbase + Playwright + Grok.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from models import (
    RunRequest, RunResponse, RunStatus, CompanyResult, 
    WebSocketMessage, HealthResponse
)
from browserbase_client import browserbase_client
from playwright_bridge import PlaywrightBridge
from yc_scraper import YCScraper
from llm_client import generate_roast
from storage import storage
from logutil import setup_logger

logger = setup_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, run_id: str):
        await websocket.accept()
        self.active_connections[run_id] = websocket
        logger.info("WebSocket connected", run_id=run_id)
    
    def disconnect(self, run_id: str):
        if run_id in self.active_connections:
            del self.active_connections[run_id]
            logger.info("WebSocket disconnected", run_id=run_id)
    
    async def send_message(self, run_id: str, message: dict):
        if run_id in self.active_connections:
            try:
                await self.active_connections[run_id].send_text(json.dumps(message))
            except Exception as e:
                logger.warning("Failed to send WebSocket message", run_id=run_id, error=str(e))
                self.disconnect(run_id)


# Global instances
connection_manager = ConnectionManager()
runs: Dict[str, RunStatus] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management - showcasing Cerebrium's orchestration."""
    logger.info("🚀 Startup Roast Bot starting on Cerebrium...")
    logger.info("🔥 Leveraging Cerebrium's platform capabilities:")
    logger.info("   - Custom runtime with WebSocket support")
    logger.info("   - Built-in storage (no AWS S3 needed)")
    logger.info("   - Serverless scaling for concurrent runs")
    logger.info("   - Long-running task support (30-90s workflows)")
    yield
    logger.info("👋 Graceful shutdown complete - Cerebrium handles cleanup!")


app = FastAPI(
    title="Startup Roast Bot",
    description="AI-powered startup website analyzer and roaster",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint for Cerebrium load balancer."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow()
    )


@app.get("/ready", response_model=HealthResponse)
async def ready():
    """Ready check endpoint for Cerebrium load balancer."""
    return HealthResponse(
        status="ready",
        timestamp=datetime.utcnow()
    )


@app.post("/run", response_model=RunResponse)
async def run_roast(request: RunRequest):
    """Start a new roast run."""
    run_id = str(uuid.uuid4())
    
    # Create run status
    run_status = RunStatus(
        run_id=run_id,
        status="running",
        created_at=datetime.utcnow()
    )
    runs[run_id] = run_status
    
    # Start roast process in background
    asyncio.create_task(execute_roast(run_id, request))
    
    logger.info("Started roast run", extra={'run_id': run_id, 'source': request.source})
    
    return RunResponse(
        run_id=run_id,
        status="running",
        stream_url=f"/stream/{run_id}"
    )


@app.get("/runs/{run_id}", response_model=RunStatus)
async def get_run(run_id: str):
    """Get the status and results of a specific run."""
    if run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return runs[run_id]


@app.websocket("/stream/{run_id}")
async def stream_run_updates(websocket: WebSocket, run_id: str):
    """WebSocket endpoint for real-time run updates."""
    await connection_manager.connect(websocket, run_id)
    
    try:
        while True:
            await asyncio.sleep(1)
            
            if run_id in runs:
                run = runs[run_id]
                
                # Send current status
                await connection_manager.send_message(run_id, {
                    "status": run.status,
                    "total_companies": run.total_companies,
                    "processed_companies": run.processed_companies
                })
                
                # Close connection if run is complete
                if run.status in ["completed", "failed"]:
                    break
                    
    except WebSocketDisconnect:
        connection_manager.disconnect(run_id)


async def execute_roast(run_id: str, request: RunRequest):
    """Execute the roast process."""
    run = runs[run_id]
    
    try:
        # Create Browserbase session
        logger.info("Creating Browserbase session", extra={'run_id': run_id})
        session_data = browserbase_client.create_session()
        session_id = session_data["id"]
        playwright_endpoint = session_data["playwrightWsEndpoint"]
        
        # Initialize Playwright bridge
        playwright_bridge = PlaywrightBridge(playwright_endpoint)
        await playwright_bridge.connect()
        
        # Get company URLs based on source
        company_urls = []
        if request.source == "yc":
            # YC Mode: Scrape YC directory → get profile URLs → extract website URLs
            yc_scraper = YCScraper(playwright_endpoint)
            await yc_scraper.connect()
            
            yc_params = request.yc or {}
            batch = yc_params.get("batch")
            limit = yc_params.get("limit", 24)
            
            logger.info("Scraping YC directory for company profiles", batch=batch, limit=limit)
            profile_urls = await yc_scraper.scrape_company_urls(batch, limit)
            logger.info(f"Found {len(profile_urls)} YC profile URLs")
            
            await yc_scraper.close()
            
            # Now extract website URLs from each YC profile
            logger.info("Extracting website URLs from YC profiles")
            for i, profile_url in enumerate(profile_urls):
                logger.info(f"Processing YC profile {i+1}/{len(profile_urls)}: {profile_url}")
                
                if await playwright_bridge.goto(profile_url):
                    website_url = await playwright_bridge.extract_website_url(profile_url)
                    if website_url:
                        company_urls.append(website_url)
                        logger.info(f"✅ Extracted website: {website_url}")
                    else:
                        logger.warning(f"⚠️ No website URL found for: {profile_url}")
                else:
                    logger.error(f"❌ Failed to load YC profile: {profile_url}")
            
            logger.info(f"Successfully extracted {len(company_urls)} website URLs from YC profiles")
            
        elif request.source == "custom":
            # Custom Mode: Use provided URLs directly
            custom_params = request.custom or {}
            company_urls = custom_params.get("urls", [])
            logger.info(f"Using {len(company_urls)} custom URLs")
        
        run.total_companies = len(company_urls)
        logger.info("Found companies to process", run_id=run_id, count=len(company_urls))
        
        # Process each company
        for i, website_url in enumerate(company_urls):
            try:
                company_slug = website_url.replace("https://", "").replace("http://", "").split("/")[0]
                
                # Navigate to website
                if not await playwright_bridge.goto(website_url):
                    await send_company_result(run_id, {
                        "company": {"name": company_slug, "website": website_url},
                        "status": "skipped",
                        "error_reason": "Failed to load website"
                    })
                    continue
                
                # Extract page summary
                summary = await playwright_bridge.extract_summary()
                
                # Take screenshot
                screenshot_data = await playwright_bridge.screenshot()
                screenshot_url = None
                if screenshot_data:
                    screenshot_url = storage.put_screenshot(run_id, company_slug, 1, screenshot_data)
                
                # Generate roast
                roast = generate_roast(summary, request.style)
                
                # Save trace data
                trace_data = {
                    "url": website_url,
                    "summary": summary,
                    "timestamp": datetime.utcnow().isoformat()
                }
                storage.put_trace(run_id, company_slug, trace_data)
                
                # Create company result
                company_result = CompanyResult(
                    name=summary.get("title", company_slug),
                    website=website_url,
                    roast=roast,
                    screenshot_url=screenshot_url,
                    status="done",
                    summary=summary
                )
                
                run.results.append(company_result)
                run.processed_companies += 1
                
                # Send WebSocket update
                await send_company_result(run_id, {
                    "company": {"name": company_result.name, "website": company_result.website},
                    "roast": company_result.roast,
                    "screenshot_url": company_result.screenshot_url,
                    "status": "done"
                })
                
                logger.info("Processed company", 
                           run_id=run_id, 
                           company=company_slug, 
                           progress=f"{i+1}/{len(company_urls)}")
                
            except Exception as e:
                logger.error("Failed to process company", 
                           run_id=run_id, 
                           website=website_url, 
                           error=str(e))
                
                await send_company_result(run_id, {
                    "company": {"name": website_url, "website": website_url},
                    "status": "error",
                    "error_reason": str(e)
                })
        
        # Mark run as completed
        run.status = "completed"
        run.completed_at = datetime.utcnow()
        
        await connection_manager.send_message(run_id, {"status": "finished"})
        logger.info("Completed roast run", extra={'run_id': run_id})
        
    except Exception as e:
        run.status = "failed"
        run.error_message = str(e)
        logger.error("Failed roast run", extra={'run_id': run_id, 'error': str(e)})
        
        await connection_manager.send_message(run_id, {
            "status": "failed",
            "error_reason": str(e)
        })
    
    finally:
        # Clean up Browserbase session
        try:
            browserbase_client.close_session(session_id)
        except:
            pass


async def send_company_result(run_id: str, result: dict):
    """Send company result via WebSocket."""
    await connection_manager.send_message(run_id, result)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
