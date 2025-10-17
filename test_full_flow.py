#!/usr/bin/env python3
"""
Test the full scraping flow without logging issues.
"""
import asyncio
import requests
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv
import json

load_dotenv()

async def test_full_flow():
    try:
        print("🚀 Testing full scraping flow...")
        
        # Get credentials
        api_key = os.getenv('BROWSERBASE_API_KEY')
        project_id = os.getenv('BROWSERBASE_PROJECT_ID')
        
        print(f"✅ API Key: {api_key[:10]}...")
        print(f"✅ Project ID: {project_id}")
        
        # Create session
        headers = {'x-bb-api-key': api_key, 'Content-Type': 'application/json'}
        payload = {'projectId': project_id}
        
        print("📡 Creating Browserbase session...")
        response = requests.post('https://api.browserbase.com/v1/sessions', headers=headers, json=payload)
        print(f"✅ Session created: {response.status_code}")
        
        session_data = response.json()
        connect_url = session_data['connectUrl']
        print(f"✅ Connect URL: {connect_url[:50]}...")
        
        # Test Playwright connection
        print("🎭 Connecting with Playwright...")
        playwright = await async_playwright().start()
        browser = await playwright.chromium.connect_over_cdp(connect_url)
        print("✅ Playwright connected")
        
        # Use default context and page as recommended
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = context.pages[0] if context.pages else await context.new_page()
        
        # Test with a real website
        test_url = "https://example.com"
        print(f"🌐 Testing navigation to {test_url}...")
        await page.goto(test_url, timeout=30000)
        title = await page.title()
        print(f"✅ Page loaded: {title}")
        
        # Extract page content
        print("📄 Extracting page content...")
        
        # Get title
        title = await page.title()
        
        # Get hero text (first h1)
        hero = ""
        try:
            hero_element = await page.query_selector("h1")
            if hero_element:
                hero = await hero_element.text_content()
        except:
            pass
        
        # Get first CTA button
        cta = ""
        try:
            cta_element = await page.query_selector("a, button")
            if cta_element:
                cta = await cta_element.text_content()
        except:
            pass
        
        print(f"✅ Title: {title}")
        print(f"✅ Hero: {hero}")
        print(f"✅ CTA: {cta}")
        
        # Test screenshot
        print("📸 Taking screenshot...")
        screenshot = await page.screenshot()
        print(f"✅ Screenshot taken: {len(screenshot)} bytes")
        
        # Test Grok API
        print("🤖 Testing Grok API...")
        grok_api_key = os.getenv('GROK_API_KEY')
        if grok_api_key:
            summary = {
                "title": title,
                "hero": hero,
                "cta": cta
            }
            
            payload = {
                "model": "grok-3",
                "temperature": 0.9,
                "max_tokens": 80,
                "messages": [
                    {"role": "system", "content": "You are a witty startup critic. Generate a single, tasteful roast of a landing page in 1 sentence (max 180 chars). Focus on the value proposition, design, or messaging. Be clever but not mean."},
                    {"role": "user", "content": f"Roast this landing page: {json.dumps(summary)}"}
                ],
            }
            
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {grok_api_key}"},
                json=payload, timeout=60
            )
            
            if response.status_code == 200:
                roast = response.json()["choices"][0]["message"]["content"].strip()
                print(f"✅ Grok roast: {roast}")
            else:
                print(f"❌ Grok API error: {response.status_code} - {response.text}")
        else:
            print("⚠️ No Grok API key found")
        
        await browser.close()
        await playwright.stop()
        print("🎉 Full flow test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_flow())
