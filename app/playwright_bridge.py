"""
Playwright bridge for website scraping and screenshots.
"""

import asyncio
from typing import Dict, Optional, Tuple
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from logutil import setup_logger

logger = setup_logger(__name__)


class PlaywrightBridge:
    """Bridge for Playwright operations over Browserbase CDP."""
    
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
            
            logger.info("Connected to Playwright via CDP")
            
        except Exception as e:
            logger.error("Failed to connect to Playwright", error=str(e))
            raise
    
    async def goto(self, url: str, timeout: int = 30000) -> bool:
        """Navigate to a URL."""
        try:
            if not self.page:
                raise RuntimeError("Playwright not connected")
            
            logger.info("Navigating to URL", url=url)
            await self.page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            await asyncio.sleep(0.3)  # Short wait for page to settle
            
            return True
            
        except Exception as e:
            logger.error("Failed to navigate to URL", url=url, error=str(e))
            return False
    
    async def screenshot(self, full_page: bool = False) -> Optional[bytes]:
        """Take a screenshot."""
        try:
            if not self.page:
                raise RuntimeError("Playwright not connected")
            
            screenshot_data = await self.page.screenshot(
                full_page=full_page,
                type="png"
            )
            
            logger.info("Screenshot taken", size=len(screenshot_data), full_page=full_page)
            return screenshot_data
            
        except Exception as e:
            logger.error("Failed to take screenshot", error=str(e))
            return None
    
    async def extract_summary(self) -> Dict[str, str]:
        """Extract page summary (title, hero, CTA)."""
        try:
            if not self.page:
                raise RuntimeError("Playwright not connected")
            
            # Get page title
            title = await self.page.title()
            
            # Extract hero text (first h1 or fallback)
            hero = ""
            try:
                hero_element = await self.page.query_selector("h1")
                if hero_element:
                    hero = await hero_element.inner_text()
                else:
                    # Fallback to h1 span or data-test=hero
                    hero_element = await self.page.query_selector("h1 span, [data-test=hero]")
                    if hero_element:
                        hero = await hero_element.inner_text()
            except:
                pass
            
            # Extract CTA text (first button)
            cta = ""
            try:
                cta_element = await self.page.get_by_role("button").first
                if cta_element:
                    cta = await cta_element.inner_text()
            except:
                pass
            
            # Clean up text
            title = title.strip() if title else ""
            hero = hero.strip() if hero else ""
            cta = cta.strip() if cta else ""
            
            summary = {
                "title": title,
                "hero": hero,
                "cta": cta
            }
            
            logger.info("Extracted page summary", 
                       title_length=len(title), 
                       hero_length=len(hero), 
                       cta_length=len(cta))
            
            return summary
            
        except Exception as e:
            logger.error("Failed to extract page summary", error=str(e))
            return {"title": "", "hero": "", "cta": ""}
    
    async def extract_website_url(self, yc_profile_url: str) -> Optional[str]:
        """Extract external website URL from YC profile page."""
        try:
            if not self.page:
                raise RuntimeError("Playwright not connected")
            
            # Wait for page to load
            await asyncio.sleep(1)
            
            # Look for website link with multiple strategies
            website_url = None
            
            # Strategy 1: Look for "Website" text and find nearby link
            try:
                website_text = await self.page.get_by_text("Website").first
                if website_text:
                    # Find the parent element that contains the link
                    parent = await website_text.locator("..").first
                    link = await parent.locator("a").first
                    if link:
                        href = await link.get_attribute("href")
                        if href and href.startswith("http") and "ycombinator.com" not in href:
                            website_url = href
            except:
                pass
            
            # Strategy 2: Look for common website link patterns
            if not website_url:
                try:
                    selectors = [
                        "a[href^='http']:not([href*='ycombinator.com'])",
                        "a[href^='https']:not([href*='ycombinator.com'])",
                        ".website-link",
                        "[data-testid='website-link']",
                        "a:has-text('Visit')",
                        "a:has-text('Go to')"
                    ]
                    
                    for selector in selectors:
                        try:
                            link = await self.page.query_selector(selector)
                            if link:
                                href = await link.get_attribute("href")
                                if href and href.startswith("http") and "ycombinator.com" not in href:
                                    website_url = href
                                    break
                        except:
                            continue
                except:
                    pass
            
            # Strategy 3: Look for any external link in the main content
            if not website_url:
                try:
                    links = await self.page.query_selector_all("a[href^='http']")
                    for link in links:
                        href = await link.get_attribute("href")
                        if href and "ycombinator.com" not in href and not href.startswith("https://www.linkedin.com"):
                            website_url = href
                            break
                except:
                    pass
            
            logger.info("Extracted website URL", 
                       yc_profile=yc_profile_url, 
                       website_url=website_url)
            
            return website_url
            
        except Exception as e:
            logger.error("Failed to extract website URL", 
                        yc_profile=yc_profile_url, 
                        error=str(e))
            return None
    
    async def close(self) -> None:
        """Close Playwright connection."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            
            logger.info("Closed Playwright connection")
            
        except Exception as e:
            logger.error("Failed to close Playwright connection", error=str(e))
