"""
YC directory scraping functionality.
"""

import asyncio
import random
from typing import List, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from logutil import setup_logger

logger = setup_logger(__name__)


class YCScraper:
    """Scraper for YC directory to collect company profile URLs."""
    
    def __init__(self, playwright_ws_endpoint: str):
        self.playwright_ws_endpoint = playwright_ws_endpoint
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def connect(self) -> None:
        """Connect to Playwright via CDP."""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.connect_over_cdp(self.playwright_ws_endpoint)
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )
            self.page = await self.context.new_page()
            
            logger.info("Connected to Playwright for YC scraping")
            
        except Exception as e:
            logger.error("Failed to connect to Playwright for YC scraping", extra={'extra_fields': {'error': str(e)}})
            raise
    
    async def scrape_company_urls(self, batch: Optional[str] = None, limit: int = 24) -> List[str]:
        """Scrape company profile URLs from YC directory."""
        try:
            if not self.page:
                raise RuntimeError("Playwright not connected")
            
            # Navigate to YC companies directory
            url = "https://www.ycombinator.com/companies"
            logger.info("Navigating to YC directory", url=url)
            
            await self.page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(1)  # Wait for page to load
            
            # Apply batch filter if specified
            if batch:
                await self._apply_batch_filter(batch)
            
            # Scroll to load more companies (infinite scroll)
            await self._scroll_to_load_companies(limit)
            
            # Extract company profile URLs
            profile_urls = await self._extract_profile_urls(limit)
            
            logger.info("Scraped company URLs", 
                       count=len(profile_urls), 
                       batch=batch, 
                       limit=limit)
            
            return profile_urls
            
        except Exception as e:
            logger.error("Failed to scrape company URLs", extra={'extra_fields': {'error': str(e)}})
            return []
    
    async def _apply_batch_filter(self, batch: str) -> None:
        """Apply batch filter to YC directory."""
        try:
            # Wait for page to load
            await asyncio.sleep(2)
            
            # Look for batch filter UI elements
            # YC directory typically has filters in the sidebar or top area
            
            # Strategy 1: Look for batch filter dropdown or buttons
            batch_selectors = [
                f"button:has-text('{batch}')",
                f"[data-batch='{batch}']",
                f"text={batch}",
                ".filter-button",
                ".batch-filter",
                "select option"
            ]
            
            for selector in batch_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        await element.click()
                        await asyncio.sleep(1)
                        logger.info("Applied batch filter", batch=batch, selector=selector)
                        return
                except:
                    continue
            
            # Strategy 2: Look for search/filter input
            search_selectors = [
                "input[type='search']",
                "input[placeholder*='search']",
                "input[placeholder*='Search']",
                "input[placeholder*='Filter']",
                ".search-input",
                ".filter-input"
            ]
            
            for selector in search_selectors:
                try:
                    search_box = await self.page.query_selector(selector)
                    if search_box:
                        await search_box.fill(batch)
                        await search_box.press("Enter")
                        await asyncio.sleep(2)
                        logger.info("Applied batch filter via search", batch=batch, selector=selector)
                        return
                except:
                    continue
            
            # Strategy 3: Look for any clickable element that might be a filter
            try:
                # Look for elements that might contain the batch name
                elements = await self.page.query_selector_all("button, a, .filter-item, .batch-item")
                for element in elements:
                    text = await element.inner_text()
                    if batch.lower() in text.lower():
                        await element.click()
                        await asyncio.sleep(1)
                        logger.info("Applied batch filter via text match", batch=batch, text=text)
                        return
            except:
                pass
            
            logger.warning("Could not find batch filter UI", batch=batch)
            
        except Exception as e:
            logger.warning("Failed to apply batch filter", extra={'extra_fields': {'batch': batch, 'error': str(e)}})
    
    async def _scroll_to_load_companies(self, target_count: int) -> None:
        """Scroll to load more companies via infinite scroll."""
        try:
            current_count = 0
            scroll_attempts = 0
            max_scrolls = 10
            
            while current_count < target_count and scroll_attempts < max_scrolls:
                # Count current company links
                links = await self.page.query_selector_all("a[href^='/companies/']")
                current_count = len(links)
                
                if current_count >= target_count:
                    break
                
                # Scroll down
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)  # Wait for new content to load
                
                scroll_attempts += 1
                logger.debug("Scrolled to load companies", 
                           current_count=current_count, 
                           target_count=target_count,
                           scroll_attempts=scroll_attempts)
            
        except Exception as e:
            logger.warning("Failed to scroll for more companies", extra={'extra_fields': {'error': str(e)}})
    
    async def _extract_profile_urls(self, limit: int) -> List[str]:
        """Extract company profile URLs from the page."""
        try:
            # Find all company profile links
            links = await self.page.query_selector_all("a[href^='/companies/']")
            
            profile_urls = []
            for link in links[:limit]:
                try:
                    href = await link.get_attribute("href")
                    if href and href.startswith("/companies/"):
                        full_url = f"https://www.ycombinator.com{href}"
                        profile_urls.append(full_url)
                except:
                    continue
            
            logger.info("Extracted profile URLs", count=len(profile_urls))
            
            # Shuffle to get random companies
            random.shuffle(profile_urls)
            
            return profile_urls
            
        except Exception as e:
            logger.error("Failed to extract profile URLs", extra={'extra_fields': {'error': str(e)}})
            return []
    
    async def close(self) -> None:
        """Close Playwright connection."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            
            logger.info("Closed Playwright connection for YC scraping")
            
        except Exception as e:
            logger.error("Failed to close Playwright connection for YC scraping", extra={'extra_fields': {'error': str(e)}})
