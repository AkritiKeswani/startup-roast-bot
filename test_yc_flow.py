#!/usr/bin/env python3
"""
Test YC scraping flow to see what's actually being extracted.
"""
import asyncio
import requests
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv
import json

load_dotenv()

async def test_yc_flow():
    try:
        print("🚀 Testing YC scraping flow...")
        
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
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.connect_over_cdp(connect_url)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = context.pages[0] if context.pages else await context.new_page()
        
        # Test YC directory scraping
        print("\n🌐 Testing YC directory...")
        yc_url = "https://www.ycombinator.com/companies"
        await page.goto(yc_url, timeout=30000)
        await asyncio.sleep(3)  # Wait for page to load
        
        # Check what we can see
        title = await page.title()
        print(f"✅ YC Page Title: {title}")
        
        # Look for company links
        company_links = await page.query_selector_all("a[href^='/companies/']")
        print(f"📊 Found {len(company_links)} company links")
        
        if company_links:
            # Test first company link
            first_link = company_links[0]
            href = await first_link.get_attribute("href")
            full_url = f"https://www.ycombinator.com{href}"
            print(f"🔗 First company URL: {full_url}")
            
            # Navigate to company profile
            print(f"\n🌐 Testing company profile: {full_url}")
            await page.goto(full_url, timeout=30000)
            await asyncio.sleep(2)
            
            profile_title = await page.title()
            print(f"✅ Profile Title: {profile_title}")
            
            # Look for website links
            website_links = await page.query_selector_all("a[href^='http']")
            external_links = []
            for link in website_links:
                href = await link.get_attribute("href")
                if href and "ycombinator.com" not in href and not href.startswith("https://www.linkedin.com"):
                    external_links.append(href)
            
            print(f"🔗 Found {len(external_links)} external links:")
            for i, link in enumerate(external_links[:5]):  # Show first 5
                print(f"  {i+1}. {link}")
            
            if external_links:
                # Test the first external website
                website_url = external_links[0]
                print(f"\n🌐 Testing external website: {website_url}")
                await page.goto(website_url, timeout=30000)
                await asyncio.sleep(2)
                
                website_title = await page.title()
                print(f"✅ Website Title: {website_title}")
                
                # Extract basic content
                try:
                    hero_element = await page.query_selector("h1")
                    hero = await hero_element.inner_text() if hero_element else ""
                    print(f"✅ Hero: {hero[:100]}...")
                except:
                    print("❌ Hero extraction failed")
                
                try:
                    button_element = await page.query_selector("button")
                    cta = await button_element.inner_text() if button_element else ""
                    print(f"✅ CTA: {cta}")
                except:
                    print("❌ CTA extraction failed")
                
                # Take screenshot
                try:
                    screenshot = await page.screenshot()
                    print(f"📸 Screenshot: {len(screenshot)} bytes")
                except:
                    print("❌ Screenshot failed")
        
        await browser.close()
        await playwright.stop()
        print("\n✅ YC flow test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_yc_flow())
