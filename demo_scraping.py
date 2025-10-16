#!/usr/bin/env python3
"""
Demo of the scraping flow - shows how it works without external APIs
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from playwright.async_api import async_playwright
from app.logutil import setup_logger

logger = setup_logger(__name__)


async def demo_scraping_flow():
    """Demo the scraping flow with a real website."""
    
    print("🔍 Demo: How the Scraping Flow Works")
    print("=" * 50)
    
    # Step 1: Show YC directory scraping concept
    print("\n1️⃣ YC Directory Scraping:")
    print("   - Goes to https://www.ycombinator.com/companies")
    print("   - Scrolls to load company cards")
    print("   - Extracts profile URLs like '/companies/company-name'")
    print("   - Example URLs found:")
    print("     • https://www.ycombinator.com/companies/stripe")
    print("     • https://www.ycombinator.com/companies/airbnb")
    print("     • https://www.ycombinator.com/companies/dropbox")
    
    # Step 2: Show YC profile analysis
    print("\n2️⃣ YC Profile Analysis:")
    print("   - Visits each company's YC profile")
    print("   - Looks for website links using multiple strategies:")
    print("     • 'Website' text with nearby link")
    print("     • External links (not ycombinator.com)")
    print("     • Common selectors like .website-link")
    print("   - Example: Stripe profile → https://stripe.com")
    
    # Step 3: Demo actual website scraping
    print("\n3️⃣ Website Analysis (Live Demo):")
    print("   - Visiting a real website to show the process...")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Visit a real website
            test_url = "https://stripe.com"
            print(f"   🌐 Visiting: {test_url}")
            
            await page.goto(test_url, timeout=10000)
            await asyncio.sleep(1)
            
            # Extract page data
            title = await page.title()
            print(f"   📄 Title: {title}")
            
            # Try to find hero text
            try:
                hero_element = await page.query_selector("h1")
                if hero_element:
                    hero_text = await hero_element.inner_text()
                    print(f"   🎯 Hero: {hero_text[:100]}...")
                else:
                    print("   🎯 Hero: Not found")
            except:
                print("   🎯 Hero: Error extracting")
            
            # Try to find CTA button
            try:
                cta_element = await page.get_by_role("button").first
                if cta_element:
                    cta_text = await cta_element.inner_text()
                    print(f"   🔘 CTA: {cta_text}")
                else:
                    print("   🔘 CTA: Not found")
            except:
                print("   🔘 CTA: Error extracting")
            
            # Take screenshot
            screenshot = await page.screenshot()
            print(f"   📸 Screenshot: {len(screenshot)} bytes captured")
            
            await browser.close()
            
    except Exception as e:
        print(f"   ❌ Demo failed: {e}")
        print("   (This is expected if Playwright isn't fully set up)")
    
    # Step 4: Show AI roasting
    print("\n4️⃣ AI Roasting:")
    print("   - Sends page summary to Grok LLM")
    print("   - Uses the provided prompt for witty roasts")
    print("   - Example roast: 'Your hero says AI, your CTA says Free, and my brain says confusion.'")
    
    # Step 5: Show Cerebrium integration
    print("\n5️⃣ Cerebrium Integration:")
    print("   - Real-time WebSocket streaming of results")
    print("   - Built-in storage for screenshots (no AWS needed)")
    print("   - Serverless scaling for multiple concurrent runs")
    print("   - Long-running task support (30-90 second workflows)")
    
    print("\n✅ Complete Flow:")
    print("   YC Directory → Company Profiles → Website URLs → Website Analysis → AI Roasts")
    print("   All powered by Cerebrium's platform capabilities!")


if __name__ == "__main__":
    asyncio.run(demo_scraping_flow())
