#!/usr/bin/env python3
"""
Debug YC scraping to see what's happening.
"""
import asyncio
import requests
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

load_dotenv()

async def debug_yc_scraping():
    try:
        print("🔍 Debugging YC scraping...")
        
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
        
        # Test YC directory
        print("🌐 Testing YC directory...")
        yc_url = "https://www.ycombinator.com/companies"
        await page.goto(yc_url, timeout=30000)
        await asyncio.sleep(3)
        
        title = await page.title()
        print(f"✅ Page title: {title}")
        
        # Look for company links
        company_links = await page.query_selector_all("a[href^='/companies/']")
        print(f"📊 Found {len(company_links)} company links")
        
        if company_links:
            # Show first few links
            for i, link in enumerate(company_links[:5]):
                href = await link.get_attribute("href")
                print(f"  {i+1}. {href}")
            
            # Test first company
            first_link = company_links[0]
            href = await first_link.get_attribute("href")
            full_url = f"https://www.ycombinator.com{href}"
            print(f"\n🔗 Testing first company: {full_url}")
            
            await page.goto(full_url, timeout=30000)
            await asyncio.sleep(2)
            
            profile_title = await page.title()
            print(f"✅ Profile title: {profile_title}")
            
            # Look for external website links
            all_links = await page.query_selector_all("a[href^='http']")
            external_links = []
            for link in all_links:
                href = await link.get_attribute("href")
                if href and "ycombinator.com" not in href and not href.startswith("https://www.linkedin.com") and not href.startswith("https://twitter.com"):
                    external_links.append(href)
            
            print(f"🔗 Found {len(external_links)} external links:")
            for i, link in enumerate(external_links[:3]):
                print(f"  {i+1}. {link}")
            
            if external_links:
                website_url = external_links[0]
                print(f"\n🌐 Testing external website: {website_url}")
                await page.goto(website_url, timeout=30000)
                await asyncio.sleep(2)
                
                website_title = await page.title()
                print(f"✅ Website title: {website_title}")
                
                # Test content extraction
                try:
                    h1_element = await page.query_selector("h1")
                    hero = await h1_element.inner_text() if h1_element else ""
                    print(f"✅ Hero text: {hero[:100]}...")
                except Exception as e:
                    print(f"❌ Hero extraction error: {e}")
                
                try:
                    button_element = await page.query_selector("button")
                    cta = await button_element.inner_text() if button_element else ""
                    print(f"✅ CTA text: {cta}")
                except Exception as e:
                    print(f"❌ CTA extraction error: {e}")
        else:
            print("❌ No company links found!")
        
        await browser.close()
        await playwright.stop()
        print("\n✅ YC debug completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_yc_scraping())

