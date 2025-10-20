#!/usr/bin/env python3
"""
Debug hero text extraction specifically.
"""
import asyncio
import requests
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

load_dotenv()

async def debug_hero_extraction():
    try:
        print("🔍 Debugging hero text extraction...")
        
        # Get credentials
        api_key = os.getenv('BROWSERBASE_API_KEY')
        project_id = os.getenv('BROWSERBASE_PROJECT_ID')
        
        # Create session
        headers = {'x-bb-api-key': api_key, 'Content-Type': 'application/json'}
        payload = {'projectId': project_id}
        
        response = requests.post('https://api.browserbase.com/v1/sessions', headers=headers, json=payload)
        session_data = response.json()
        connect_url = session_data['connectUrl']
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.connect_over_cdp(connect_url)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = context.pages[0] if context.pages else await context.new_page()
        
        # Test with Stripe specifically
        test_url = "https://stripe.com"
        print(f"🌐 Testing {test_url}...")
        
        await page.goto(test_url, timeout=30000)
        await asyncio.sleep(3)  # Wait for page to load
        
        # Debug hero extraction step by step
        print("\n🔍 Step-by-step hero extraction:")
        
        # Step 1: Check if page loaded
        title = await page.title()
        print(f"✅ Page title: {title}")
        
        # Step 2: Look for h1 elements
        h1_elements = await page.query_selector_all("h1")
        print(f"📊 Found {len(h1_elements)} h1 elements")
        
        for i, h1 in enumerate(h1_elements):
            try:
                text = await h1.inner_text()
                print(f"  h1[{i}]: '{text[:100]}...'")
            except Exception as e:
                print(f"  h1[{i}]: Error - {e}")
        
        # Step 3: Try different hero selectors
        hero_selectors = [
            "h1",
            "h1 span", 
            "[data-test=hero]",
            ".hero-title",
            ".main-title",
            ".hero h1",
            ".hero h2",
            ".banner h1",
            ".banner h2",
            "[class*='hero'] h1",
            "[class*='hero'] h2",
            ".jumbotron h1",
            ".jumbotron h2"
        ]
        
        print(f"\n🔍 Testing hero selectors:")
        for selector in hero_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    if text and text.strip():
                        print(f"  ✅ {selector}: '{text[:100]}...'")
                    else:
                        print(f"  ⚠️  {selector}: Found but empty")
                else:
                    print(f"  ❌ {selector}: Not found")
            except Exception as e:
                print(f"  ❌ {selector}: Error - {e}")
        
        # Step 4: Look for largest text elements
        print(f"\n🔍 Looking for largest text elements:")
        try:
            all_text_elements = await page.query_selector_all("h1, h2, .title, .headline")
            print(f"📊 Found {len(all_text_elements)} text elements")
            
            largest_text = ""
            for element in all_text_elements:
                try:
                    text = await element.inner_text()
                    if text and len(text.strip()) > len(largest_text):
                        largest_text = text.strip()
                except:
                    pass
            
            print(f"📝 Largest text found: '{largest_text[:200]}...'")
        except Exception as e:
            print(f"❌ Error finding largest text: {e}")
        
        # Step 5: Check page content
        print(f"\n🔍 Page content analysis:")
        try:
            body_text = await page.inner_text("body")
            print(f"📄 Body text length: {len(body_text)} characters")
            print(f"📄 First 200 chars: '{body_text[:200]}...'")
        except Exception as e:
            print(f"❌ Error getting body text: {e}")
        
        await browser.close()
        await playwright.stop()
        print("\n✅ Hero extraction debug completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_hero_extraction())

