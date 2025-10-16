#!/usr/bin/env python3
"""
Test the scraping flow using direct Playwright (without Browserbase)
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from playwright.async_api import async_playwright
from app.logutil import setup_logger

logger = setup_logger(__name__)


async def test_direct_scraping():
    """Test the scraping flow using direct Playwright."""
    
    print("🔍 Testing Direct Playwright Scraping")
    print("=" * 45)
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Test 1: YC Directory Scraping
            print("1. Testing YC Directory Scraping...")
            await page.goto("https://www.ycombinator.com/companies")
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(2000)  # Wait for content to load
            
            # Look for company links
            company_links = await page.query_selector_all('a[href*="/companies/"]')
            print(f"   ✅ Found {len(company_links)} company links")
            
            if len(company_links) > 0:
                # Test 2: Visit a company profile
                first_link = await company_links[0].get_attribute('href')
                print(f"   📄 Testing profile: {first_link}")
                
                await page.goto(f"https://www.ycombinator.com{first_link}")
                await page.wait_for_load_state("domcontentloaded")
                
                # Look for website links
                website_links = await page.query_selector_all('a[href^="http"]')
                external_links = []
                for link in website_links:
                    href = await link.get_attribute('href')
                    if href and 'ycombinator.com' not in href:
                        external_links.append(href)
                
                print(f"   ✅ Found {len(external_links)} external website links")
                
                if len(external_links) > 0:
                    # Test 3: Visit the actual website
                    website_url = external_links[0]
                    print(f"   🌐 Testing website: {website_url}")
                    
                    await page.goto(website_url)
                    await page.wait_for_load_state("domcontentloaded")
                    
                    # Extract page data
                    title = await page.title()
                    print(f"   📄 Title: {title}")
                    
                    # Try to find hero text
                    try:
                        hero_element = await page.query_selector("h1")
                        if hero_element:
                            hero_text = await hero_element.inner_text()
                            print(f"   🎯 Hero: {hero_text[:100]}...")
                    except:
                        print("   🎯 Hero: Not found")
                    
                    # Try to find CTA button
                    try:
                        cta_element = await page.get_by_role("button").first
                        if cta_element:
                            cta_text = await cta_element.inner_text()
                            print(f"   🔘 CTA: {cta_text}")
                    except:
                        print("   🔘 CTA: Not found")
                    
                    # Take screenshot
                    screenshot = await page.screenshot()
                    print(f"   📸 Screenshot: {len(screenshot)} bytes")
                    
                    print("   ✅ Complete scraping flow successful!")
            
            await browser.close()
            print("\n✅ Direct Playwright scraping works!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_direct_scraping())
