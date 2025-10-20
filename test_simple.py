#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

print("🧪 Testing simple Playwright + Browserbase...")

try:
    from app import browserbase_client as bb
    print("1. Creating Browserbase session...")
    sess = bb.create_session({})
    print(f"   ✅ Session: {sess.get('id')}")
    
    print("2. Getting connection URL...")
    ws = bb.connect_url(sess)
    print(f"   ✅ URL: {ws[:50]}...")
    
    print("3. Connecting Playwright...")
    with sync_playwright():
        pw = sync_playwright().start()
        browser = pw.chromium.connect_over_cdp(ws, timeout=30000)
        print("   ✅ Connected to browser")
        
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()
        print("   ✅ Got page")
        
        print("4. Testing navigation...")
        page.goto("https://example.com", wait_until="domcontentloaded")
        print("   ✅ Page loaded")
        
        title = page.title()
        print(f"   ✅ Title: {title}")
        
        browser.close()
        pw.stop()
        print("   ✅ Cleanup complete")
        
    print("\n🎉 All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
