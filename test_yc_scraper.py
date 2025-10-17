#!/usr/bin/env python3
"""
Test YC scraper directly to see what's happening.
"""
import asyncio
import requests
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

load_dotenv()

async def test_yc_scraper():
    try:
        print("🧪 Testing YC scraper...")
        
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
        print(f"✅ Session created: {session_data['id']}")
        
        # Connect with Playwright
        playwright = await async_playwright().start()
        browser = await playwright.chromium.connect_over_cdp(connect_url)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = context.pages[0] if context.pages else await context.new_page()
        
        # Test YC directory
        print("🌐 Testing YC directory...")
        await page.goto('https://www.ycombinator.com/companies', timeout=30000)
        
        # Look for company links
        company_links = await page.query_selector_all('a[href*="/companies/"]')
        print(f"Found {len(company_links)} company links")
        
        if company_links:
            # Get the first few links
            for i, link in enumerate(company_links[:5]):
                href = await link.get_attribute('href')
                text = await link.text_content()
                print(f"  {i+1}. {text} -> {href}")
        
        await browser.close()
        await playwright.stop()
        print("✅ Test completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_yc_scraper())
