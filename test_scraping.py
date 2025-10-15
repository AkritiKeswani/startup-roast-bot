#!/usr/bin/env python3
"""
Test script to verify the core scraping flow:
1. YC Directory → company profile URLs
2. YC Profile Pages → website URLs  
3. Company Websites → screenshots + data extraction
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.browserbase_client import browserbase_client
from app.yc_scraper import YCScraper
from app.playwright_bridge import PlaywrightBridge
from app.llm_client import generate_roast
from app.logutil import setup_logger

logger = setup_logger(__name__)


async def test_scraping_flow():
    """Test the complete scraping flow."""
    try:
        # Step 1: Create Browserbase session
        logger.info("🚀 Creating Browserbase session...")
        session_data = browserbase_client.create_session()
        session_id = session_data["id"]
        playwright_endpoint = session_data["playwrightWsEndpoint"]
        logger.info(f"✅ Created session: {session_id}")
        
        # Step 2: Test YC directory scraping
        logger.info("🔍 Testing YC directory scraping...")
        yc_scraper = YCScraper(playwright_endpoint)
        await yc_scraper.connect()
        
        # Scrape just 3 companies for testing
        profile_urls = await yc_scraper.scrape_company_urls(batch="F25", limit=3)
        logger.info(f"✅ Found {len(profile_urls)} YC profile URLs")
        
        for i, profile_url in enumerate(profile_urls):
            logger.info(f"📄 YC Profile {i+1}: {profile_url}")
        
        await yc_scraper.close()
        
        # Step 3: Test website URL extraction from YC profiles
        logger.info("🌐 Testing website URL extraction from YC profiles...")
        playwright_bridge = PlaywrightBridge(playwright_endpoint)
        await playwright_bridge.connect()
        
        website_urls = []
        for i, profile_url in enumerate(profile_urls):
            logger.info(f"🔗 Extracting website from YC profile {i+1}/{len(profile_urls)}")
            if await playwright_bridge.goto(profile_url):
                website_url = await playwright_bridge.extract_website_url(profile_url)
                if website_url:
                    website_urls.append(website_url)
                    logger.info(f"✅ Extracted website: {website_url}")
                else:
                    logger.warning(f"⚠️ No website URL found for: {profile_url}")
            else:
                logger.error(f"❌ Failed to load YC profile: {profile_url}")
        
        logger.info(f"✅ Successfully extracted {len(website_urls)} website URLs from YC profiles")
        
        # Step 4: Test website scraping and data extraction
        logger.info("🏠 Testing website scraping and roasting...")
        for i, website_url in enumerate(website_urls[:2]):  # Test first 2 websites
            logger.info(f"🌐 Testing website {i+1}/{len(website_urls)}: {website_url}")
            
            if await playwright_bridge.goto(website_url):
                # Extract page summary
                summary = await playwright_bridge.extract_summary()
                logger.info(f"📊 Page Summary:")
                logger.info(f"   Title: {summary.get('title', 'N/A')}")
                logger.info(f"   Hero: {summary.get('hero', 'N/A')}")
                logger.info(f"   CTA: {summary.get('cta', 'N/A')}")
                
                # Take screenshot
                screenshot_data = await playwright_bridge.screenshot()
                if screenshot_data:
                    logger.info(f"📸 Screenshot taken: {len(screenshot_data)} bytes")
                else:
                    logger.warning("⚠️ Screenshot failed")
                
                # Test Grok roast generation
                try:
                    roast = generate_roast(summary, "spicy")
                    logger.info(f"🔥 AI Roast: {roast}")
                except Exception as e:
                    logger.error(f"❌ Roast generation failed: {e}")
            else:
                logger.error(f"❌ Failed to load website: {website_url}")
        
        # Step 5: Test custom URL mode
        logger.info("🧪 Testing custom URL mode...")
        test_urls = ["https://stripe.com", "https://vercel.com"]
        for i, test_url in enumerate(test_urls):
            logger.info(f"🌐 Testing custom URL {i+1}: {test_url}")
            if await playwright_bridge.goto(test_url):
                summary = await playwright_bridge.extract_summary()
                try:
                    roast = generate_roast(summary, "kind")
                    logger.info(f"🔥 Custom URL Roast: {roast}")
                except Exception as e:
                    logger.error(f"❌ Custom roast failed: {e}")
            else:
                logger.error(f"❌ Failed to load custom URL: {test_url}")
        
        await playwright_bridge.close()
        
        # Step 5: Clean up
        logger.info("🧹 Cleaning up...")
        browserbase_client.close_session(session_id)
        
        logger.info("✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    print("🧪 Testing Startup Roast Bot Scraping Flow")
    print("=" * 50)
    
    # Check required environment variables
    required_vars = ["BROWSERBASE_API_KEY", "GROK_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set them in your .env file or environment")
        exit(1)
    
    asyncio.run(test_scraping_flow())
