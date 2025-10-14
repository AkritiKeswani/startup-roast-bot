#!/usr/bin/env python3
"""
Example usage script for the Startup Roast Bot.
Demonstrates how to interact with the API programmatically.
"""

import asyncio
import json
import requests
import websockets
from typing import Dict, Any


class RoastBotClient:
    """Client for interacting with the Startup Roast Bot API."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    def start_roast(self, startup_url: str, roast_style: str = "savage") -> Dict[str, Any]:
        """Start a new roast session."""
        response = requests.post(
            f"{self.base_url}/run",
            json={
                "startup_url": startup_url,
                "roast_style": roast_style,
                "focus_areas": ["design", "copy", "ux", "value_prop"]
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session status and results."""
        response = requests.get(f"{self.base_url}/runs/{session_id}")
        response.raise_for_status()
        return response.json()
    
    def list_sessions(self) -> list:
        """List all roast sessions."""
        response = requests.get(f"{self.base_url}/runs")
        response.raise_for_status()
        return response.json()
    
    async def stream_updates(self, session_id: str, callback=None):
        """Stream real-time updates for a session."""
        uri = f"wss://{self.base_url.replace('https://', '').replace('http://', '')}/stream/{session_id}"
        
        async with websockets.connect(uri) as websocket:
            async for message in websocket:
                data = json.loads(message)
                if callback:
                    callback(data)
                else:
                    print(f"Update: {data}")


def print_update(data: Dict[str, Any]):
    """Print function for streaming updates."""
    if data.get("type") == "step":
        step = data.get("step", {})
        timestamp = step.get("timestamp", "")
        message = step.get("message", "")
        step_type = step.get("step_type", "")
        
        emoji = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️"
        }.get(step_type, "📝")
        
        print(f"{emoji} [{timestamp}] {message}")


async def main():
    """Main example function."""
    # Initialize client (replace with your actual Cerebrium deployment URL)
    client = RoastBotClient("https://api.aws.us-east-1.cerebrium.ai/v4/YOUR-PROJECT-ID/startup-roast-bot")
    
    print("🔥 Startup Roast Bot - Example Usage")
    print("=" * 50)
    
    # Example 1: Start a roast session
    print("\n1. Starting roast session...")
    startup_url = "https://example.com"  # Replace with actual startup URL
    
    try:
        result = client.start_roast(startup_url, roast_style="savage")
        session_id = result["session_id"]
        print(f"✅ Session started: {session_id}")
        
        # Example 2: Stream real-time updates
        print("\n2. Streaming updates...")
        print("Press Ctrl+C to stop streaming")
        
        await client.stream_updates(session_id, print_update)
        
    except KeyboardInterrupt:
        print("\n\n3. Checking final results...")
        
        # Example 3: Get final results
        session = client.get_session(session_id)
        print(f"Status: {session['status']}")
        
        if session.get("final_roast"):
            print(f"\n🔥 Final Roast:")
            print("-" * 30)
            print(session["final_roast"])
        
        if session.get("s3_screenshot_url"):
            print(f"\n📸 Screenshot: {session['s3_screenshot_url']}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def batch_roast_example():
    """Example of batch roasting multiple startups."""
    client = RoastBotClient("https://api.aws.us-east-1.cerebrium.ai/v4/YOUR-PROJECT-ID/startup-roast-bot")
    
    # List of startup URLs to roast
    startup_urls = [
        "https://example1.com",
        "https://example2.com",
        "https://example3.com"
    ]
    
    print("🔥 Batch Roast Example")
    print("=" * 30)
    
    session_ids = []
    
    for url in startup_urls:
        try:
            result = client.start_roast(url)
            session_id = result["session_id"]
            session_ids.append(session_id)
            print(f"✅ Started roast for {url}: {session_id}")
        except Exception as e:
            print(f"❌ Failed to start roast for {url}: {e}")
    
    print(f"\n📊 Started {len(session_ids)} roast sessions")
    print("Check the Cerebrium dashboard for real-time progress!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        batch_roast_example()
    else:
        asyncio.run(main())
