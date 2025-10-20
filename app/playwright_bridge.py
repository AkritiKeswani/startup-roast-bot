import asyncio
from playwright.async_api import async_playwright

class PW:
    def __init__(self, cdp_ws: str):
        self.cdp_ws = cdp_ws
        self._p = None
        self.browser = None
        self.ctx = None
        self.page = None

    async def __aenter__(self):
        self._p = await async_playwright().start()
        try:
            print(f"DEBUG: Connecting to CDP URL: {self.cdp_ws[:50]}...")
            self.browser = await self._p.chromium.connect_over_cdp(self.cdp_ws, timeout=30000)
            print(f"DEBUG: Browser connected: {self.browser}")
            self.ctx = self.browser.contexts[0] if self.browser.contexts else await self.browser.new_context()
            print(f"DEBUG: Context: {self.ctx}")
            self.page = self.ctx.pages[0] if self.ctx.pages else await self.ctx.new_page()
            print(f"DEBUG: Page: {self.page}")
            if self.page:
                await self.page.set_default_timeout(15000)
        except Exception as e:
            print(f"DEBUG: Error in __aenter__: {e}")
            if self._p:
                await self._p.stop()
            raise RuntimeError(f"Failed to connect to browser: {e}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self._p:
            await self._p.stop()

    async def goto(self, url: str):
        await self.page.goto(url, wait_until="domcontentloaded")

    async def grab_summary(self):
        title = hero = cta = ""
        try: 
            title = await self.page.title() or ""
        except: 
            pass
        try:
            h1 = self.page.locator("h1, h1 span").first
            if h1 and h1.count() > 0: 
                hero = await h1.inner_text(timeout=1500)
                hero = hero.strip()
        except: 
            pass
        try:
            btn = self.page.get_by_role("button").first
            if btn and btn.count() > 0: 
                cta = await btn.inner_text(timeout=1200)
                cta = cta.strip()
        except: 
            pass
        return {"title": title, "hero": hero, "cta": cta}

    async def screenshot(self, path: str):
        await self.page.screenshot(path=path)