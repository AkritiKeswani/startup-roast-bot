#!/usr/bin/env python3
"""
Test Playwright + Browserbase connection and basic functionality
"""

import os
import asyncio
import requests
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_browserbase_playwright():
    """Test Browserbase + Playwright connection and basic web scraping"""
    
    # Get credentials
    api_key = os.getenv("BROWSERBASE_API_KEY")
    project_id = os.getenv("BROWSERBASE_PROJECT_ID")
    
    print(f"🔑 API Key: {api_key[:10]}..." if api_key else "❌ No API key")
    print(f"🆔 Project ID: {project_id}" if project_id else "❌ No Project ID")
    
    if not api_key or not project_id:
        print("❌ Missing credentials!")
        return False
    
    # Step 1: Create Browserbase session
    print("\n🌐 Creating Browserbase session...")
    headers = {
        "x-bb-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "projectId": project_id,
        "region": "us-east-1"
    }
    
    try:
        response = requests.post(
            "https://api.browserbase.com/v1/sessions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Browserbase API failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        session_data = response.json()
        session_id = session_data.get("id")
        connect_url = session_data.get("connectUrl")
        
        print(f"✅ Browserbase session created: {session_id}")
        print(f"🔗 Connect URL: {connect_url[:50]}...")
        
    except Exception as e:
        print(f"❌ Browserbase error: {e}")
        return False
    
    # Step 2: Connect Playwright to Browserbase
    print("\n🎭 Connecting Playwright to Browserbase...")
    
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.connect_over_cdp(connect_url)
        
        # Get the default context and page
        context = browser.contexts[0]
        page = context.pages[0]
        
        print("✅ Playwright connected successfully!")
        
    except Exception as e:
        print(f"❌ Playwright connection failed: {e}")
        return False
    
    # Step 3: Test basic web navigation
    print("\n🌍 Testing web navigation...")
    
    try:
        # Navigate to a simple page
        await page.goto("https://example.com", wait_until="networkidle")
        
        # Get page title
        title = await page.title()
        print(f"✅ Page loaded: {title}")
        
        # Take a screenshot
        screenshot = await page.screenshot()
        print(f"✅ Screenshot taken: {len(screenshot)} bytes")
        
        # Extract some basic content
        content = await page.content()
        print(f"✅ Page content: {len(content)} characters")
        
        # Test YC companies page
        print("\n🏢 Testing YC companies page...")
        await page.goto("https://www.ycombinator.com/companies", wait_until="networkidle")
        
        yc_title = await page.title()
        print(f"✅ YC page loaded: {yc_title}")
        
        # Look for company links
        company_links = await page.query_selector_all("a[href^='/companies/']")
        print(f"✅ Found {len(company_links)} company links")
        
        if company_links:
            # Test clicking on first company
            first_link = company_links[0]
            href = await first_link.get_attribute("href")
            print(f"✅ First company link: {href}")
        
        # Clean up
        await browser.close()
        await playwright.stop()
        
        print("\n🎉 ALL TESTS PASSED! Playwright + Browserbase is working!")
        return True
        
    except Exception as e:
        print(f"❌ Web navigation failed: {e}")
        try:
            await browser.close()
            await playwright.stop()
        except:
            pass
        return False

if __name__ == "__main__":
    success = asyncio.run(test_browserbase_playwright())
    if success:
        print("\n✅ Ready to roast some landing pages!")
    else:
        print("\n❌ Something went wrong. Check the errors above.")
