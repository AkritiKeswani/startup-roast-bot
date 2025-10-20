#!/usr/bin/env python3
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_roast():
    print("🧪 Testing Async Playwright + Browserbase + Grok")
    print("=" * 50)
    
    try:
        # Test API keys
        print("1. Checking API keys...")
        if not os.environ.get("BROWSERBASE_API_KEY"):
            raise RuntimeError("BROWSERBASE_API_KEY not set")
        if not os.environ.get("GROK_API_KEY"):
            raise RuntimeError("GROK_API_KEY not set")
        print("   ✅ API keys found")
        
        # Test Browserbase connection
        print("2. Creating Browserbase session...")
        from app import browserbase_client as bb
        sess = bb.create_session({})
        print(f"   ✅ Session: {sess.get('id')}")
        
        ws = bb.connect_url(sess)
        print(f"   ✅ Connection URL: {ws[:50]}...")
        
        # Test Playwright + Browserbase
        print("3. Connecting Playwright to Browserbase...")
        from app.playwright_bridge import PW
        
        async with PW(ws) as pw:
            print("   ✅ Connected to remote browser")
            
            # Test navigation
            print("4. Testing navigation...")
            await pw.goto("https://example.com")
            print("   ✅ Page loaded")
            
            # Test content extraction
            print("5. Extracting content...")
            summary = await pw.grab_summary()
            print(f"   ✅ Title: {summary['title']}")
            print(f"   ✅ Hero: {summary['hero']}")
            print(f"   ✅ CTA: {summary['cta']}")
            
            # Test screenshot
            print("6. Taking screenshot...")
            await pw.screenshot("/tmp/test_screenshot.png")
            print("   ✅ Screenshot saved")
            
            # Test Grok roast
            print("7. Generating roast...")
            from app.llm_client import generate_roast
            roast = generate_roast(summary, "spicy")
            print(f"   ✅ Roast: {roast}")
        
        print("\n🎉 All tests passed! The async setup is working!")
        print("🚀 Ready to roast some startups!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_roast())
