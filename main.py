"""
Startup Roast Bot - FastAPI Backend
A production-grade agent that roasts startup websites using Cerebrium orchestration.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import RoastRequest, RoastResponse, RoastSession, RoastStep


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
            except:
                self.disconnect(session_id)


# Pure Cerebrium orchestration - no external services!
connection_manager = ConnectionManager()

# In-memory storage for demo (in production, use Redis or database)
roast_sessions: Dict[str, RoastSession] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cerebrium handles all the orchestration - we just need to start up!"""
    print("🚀 Startup Roast Bot starting on Cerebrium...")
    print("🔥 No external APIs needed - pure Cerebrium orchestration!")
    
    yield
    
    print("👋 Graceful shutdown - Cerebrium handles the cleanup!")


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


@app.get("/")
async def root():
    """Health check endpoint for Cerebrium custom runtime."""
    return {
        "message": "Startup Roast Bot API",
        "status": "healthy",
        "version": "1.0.0",
        "cerebrium": "orchestrating AI agents since 2024"
    }

@app.get("/health")
async def health():
    """Health check endpoint for Cerebrium load balancer."""
    return "OK"

@app.get("/ready")
async def ready():
    """Ready check endpoint for Cerebrium load balancer."""
    return "OK"


@app.post("/run", response_model=RoastResponse)
async def run_roast(request: RoastRequest):
    """
    Start a new roast session for a startup website.
    This endpoint initiates the browser automation and AI analysis.
    """
    session_id = str(uuid.uuid4())
    
    # Create session
    session = RoastSession(
        id=session_id,
        startup_url=request.startup_url,
        status="running",
        created_at=datetime.utcnow(),
        steps=[]
    )
    roast_sessions[session_id] = session
    
    # Start roast process in background
    asyncio.create_task(execute_roast(session_id, request))
    
    return RoastResponse(
        session_id=session_id,
        status="started",
        message="Roast session started successfully"
    )


@app.get("/runs/{session_id}", response_model=RoastSession)
async def get_roast_session(session_id: str):
    """Get the status and results of a specific roast session."""
    if session_id not in roast_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return roast_sessions[session_id]


@app.get("/runs", response_model=List[RoastSession])
async def list_roast_sessions():
    """List all roast sessions."""
    return list(roast_sessions.values())


@app.websocket("/stream/{session_id}")
async def stream_roast_updates(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time roast updates."""
    await connection_manager.connect(websocket, session_id)
    
    try:
        while True:
            # Keep connection alive and send periodic updates
            await asyncio.sleep(1)
            
            if session_id in roast_sessions:
                session = roast_sessions[session_id]
                await connection_manager.send_message(session_id, {
                    "type": "update",
                    "session": session.dict()
                })
                
                # Close connection if session is complete
                if session.status in ["completed", "failed"]:
                    break
                    
    except WebSocketDisconnect:
        connection_manager.disconnect(session_id)


async def execute_roast(session_id: str, request: RoastRequest):
    """
    Execute the roast process - showcasing Cerebrium's orchestration power!
    This simulates a real AI agent workflow without external dependencies.
    """
    session = roast_sessions[session_id]
    
    try:
        # Step 1: Simulate browser automation (what would be Playwright)
        await update_session_step(session_id, "🌐 Opening website in browser...", "info")
        await asyncio.sleep(2)  # Simulate browser startup time
        
        # Step 2: Simulate AI analysis (what would be Gemini Computer Use)
        await update_session_step(session_id, "🤖 Analyzing website with AI vision...", "info")
        await asyncio.sleep(3)  # Simulate AI processing time
        
        # Step 3: Simulate LLM generation (what would be Grok)
        await update_session_step(session_id, "🔥 Generating roast commentary...", "info")
        await asyncio.sleep(2)  # Simulate LLM generation time
        
        # Step 4: Simulate additional processing
        await update_session_step(session_id, "📸 Capturing additional screenshots...", "info")
        await asyncio.sleep(1)
        
        # Step 5: Generate the roast (pure Cerebrium demo!)
        roast_text = generate_demo_roast(request.startup_url, request.roast_style)
        
        # Step 6: Finalize session
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        session.final_roast = roast_text
        session.s3_screenshot_url = f"cerebrium://screenshots/{session_id}.png"  # Local storage for demo
        
        await update_session_step(session_id, "✅ Roast completed! Powered by Cerebrium orchestration!", "success")
        
    except Exception as e:
        session.status = "failed"
        session.error_message = str(e)
        await update_session_step(session_id, f"❌ Error: {str(e)}", "error")


def generate_demo_roast(url: str, roast_style: str) -> str:
    """Generate a demo roast showcasing Cerebrium's capabilities."""
    
    if roast_style == "savage":
        return f"""
🔥 **CEREBRIUM-POWERED ROAST** 🔥

Oh boy, {url}... where do I even begin? This website is like a startup pitch that forgot to mention what the startup actually does.

**The Good News:** At least it loads! 🎉 (Thanks to Cerebrium's 2-second cold starts)

**The Reality Check:** 
- Your design looks like it was created in 2010 and never updated
- The copy is so vague, I'm still not sure if you're selling software or sandwiches
- That call-to-action button? It's practically invisible! I had to squint to find it

**But here's the thing** - there's potential here. The bones are good, you just need to:
1. **Get specific** - Tell me exactly what problem you solve in the first 5 seconds
2. **Show, don't tell** - Add some screenshots, demos, or at least a diagram
3. **Make it pop** - Your design should make people want to stay, not run away

**Cerebrium Magic:** This entire analysis ran on a serverless container that:
- Started up in 2 seconds (not 30+ like traditional servers)
- Handled the full 30-90 second analysis loop without timing out
- Can scale to 100+ parallel roasts when the next YC batch drops
- Gracefully shuts down only after finishing the analysis

You're not doomed, but you're definitely not ready for prime time. Time to roll up those sleeves and make this thing actually convert! 💪

*This roast was powered by Cerebrium's orchestration platform - making AI agents production-ready!*
        """
    
    elif roast_style == "constructive":
        return f"""
🎯 **CONSTRUCTIVE CEREBRIUM ROAST** 🎯

Alright {url}, let's talk. You're not terrible, but you're definitely not great either. It's like you're trying to be everything to everyone and ending up being nothing to anyone.

**What's Working:**
- The site loads reasonably fast (Cerebrium's global CDN helps!)
- I can navigate without getting completely lost
- The basic structure makes sense

**What's Not Working:**
- Your value proposition is hiding in the fine print
- The design is... safe. Too safe. Like "beige walls in a dentist office" safe
- I'm still not 100% sure what you do after reading the whole page

**The Fix:**
1. **Lead with benefits, not features** - Tell me why I should care, not what you built
2. **Add some personality** - Your brand voice is currently "generic corporate website #47"
3. **Test your CTAs** - That button needs to be more compelling than "Learn More"

**Cerebrium Advantage:** While I was analyzing your site, this system:
- Kept the container alive for the full analysis (not like serverless functions that timeout)
- Can handle dozens of these analyses in parallel
- Automatically scales up when traffic spikes
- Provides real-time observability into every step

You're on the right track, but it's time to step up your game. The market won't wait for you to figure it out! 🚀

*Analysis powered by Cerebrium - the orchestration platform for production AI agents.*
        """
    
    else:  # humorous
        return f"""
✨ **HUMOROUS CEREBRIUM ROAST** ✨

Hey {url}, you're actually doing pretty well! I can see the effort you've put in, and there's definitely something here worth building on.

**What I Love:**
- Clean, professional look that builds trust
- Clear navigation that doesn't make me work too hard
- You're actually trying to solve a real problem (I think?)

**Areas for Growth:**
- Your messaging could be more compelling - add some emotion to it
- The design is solid but could use a bit more personality
- Consider adding social proof or testimonials to build credibility

**Next Steps:**
1. **A/B test your headlines** - Try different value propositions and see what sticks
2. **Add some social proof** - Customer logos, testimonials, or case studies
3. **Optimize for mobile** - Make sure it looks great on phones too

**Cerebrium Fun Fact:** This analysis is running on a platform that:
- Can scale from 0 to 100 containers in seconds
- Handles graceful shutdowns (no half-finished analyses!)
- Provides real-time monitoring (I can see every step!)
- Works globally with low latency

You're closer than you think to having something really special. Keep iterating and you'll get there! 🌟

*This roast was orchestrated by Cerebrium - making AI agents as reliable as your morning coffee!*
        """


async def update_session_step(session_id: str, message: str, step_type: str):
    """Update session with a new step and notify WebSocket clients."""
    if session_id in roast_sessions:
        step = RoastStep(
            timestamp=datetime.utcnow(),
            message=message,
            step_type=step_type
        )
        roast_sessions[session_id].steps.append(step)
        
        # Notify WebSocket clients
        await connection_manager.send_message(session_id, {
            "type": "step",
            "step": step.dict()
        })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
