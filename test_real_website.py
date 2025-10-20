#!/usr/bin/env python3
"""
Test scraping a real startup website to see what data is actually extracted.
"""
import asyncio
import requests
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv
import json

load_dotenv()

async def test_real_website():
    try:
        print("🚀 Testing real website scraping...")
        
        # Get credentials
        api_key = os.getenv('BROWSERBASE_API_KEY')
        project_id = os.getenv('BROWSERBASE_PROJECT_ID')
        
        # Create session
        headers = {'x-bb-api-key': api_key, 'Content-Type': 'application/json'}
        payload = {'projectId': project_id}
        
        print("📡 Creating Browserbase session...")
        response = requests.post('https://api.browserbase.com/v1/sessions', headers=headers, json=payload)
        session_data = response.json()
        connect_url = session_data['connectUrl']
        
        # Test with a real startup website
        test_urls = [
            "https://stripe.com",
            "https://linear.app", 
            "https://vercel.com",
            "https://notion.so"
        ]
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.connect_over_cdp(connect_url)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = context.pages[0] if context.pages else await context.new_page()
        
        for test_url in test_urls:
            print(f"\n🌐 Testing {test_url}...")
            
            try:
                # Navigate to website
                await page.goto(test_url, timeout=30000)
                await asyncio.sleep(2)  # Wait for page to load
                
                # Get basic page info
                title = await page.title()
                print(f"✅ Title: {title}")
                
                # Try to extract hero text
                hero = ""
                try:
                    hero_element = await page.query_selector("h1")
                    if hero_element:
                        hero = await hero_element.inner_text()
                    print(f"✅ Hero (h1): {hero[:100]}...")
                except Exception as e:
                    print(f"❌ Hero extraction failed: {e}")
                
                # Try to extract CTA
                cta = ""
                try:
                    cta_element = await page.get_by_role("button").first
                    if cta_element:
                        cta = await cta_element.inner_text()
                    print(f"✅ CTA (first button): {cta}")
                except Exception as e:
                    print(f"❌ CTA extraction failed: {e}")
                
                # Check for common elements
                try:
                    # Look for common startup elements
                    headings = await page.query_selector_all("h1, h2, h3")
                    print(f"📊 Found {len(headings)} headings")
                    
                    buttons = await page.query_selector_all("button, a[class*='button'], a[class*='btn']")
                    print(f"📊 Found {len(buttons)} buttons/CTAs")
                    
                    # Check for common startup text patterns
                    page_text = await page.inner_text("body")
                    startup_keywords = ["start", "get", "try", "sign up", "learn more", "download", "free", "demo"]
                    found_keywords = [kw for kw in startup_keywords if kw.lower() in page_text.lower()]
                    print(f"🔍 Found keywords: {found_keywords[:5]}")
                    
                except Exception as e:
                    print(f"❌ Element analysis failed: {e}")
                
                # Take a screenshot to verify visual content
                try:
                    screenshot = await page.screenshot()
                    print(f"📸 Screenshot: {len(screenshot)} bytes")
                except Exception as e:
                    print(f"❌ Screenshot failed: {e}")
                
            except Exception as e:
                print(f"❌ Failed to process {test_url}: {e}")
        
        await browser.close()
        await playwright.stop()
        print("\n✅ Real website test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_website())
