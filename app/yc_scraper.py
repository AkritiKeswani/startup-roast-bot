from typing import List, Tuple
from playwright.async_api import Page

async def list_profiles(page: Page, batch: str = None, limit: int = 24) -> List[str]:
    await page.goto("https://www.ycombinator.com/companies", wait_until="domcontentloaded")
    if batch:
        try:
            await page.fill("input[placeholder*='Search']", batch)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(600)
        except: pass
    links = []
    seen = set()
    for el in await page.locator("a[href^='/companies/']").all():
        href = await el.get_attribute("href") or ""
        if href.startswith("/companies/") and href not in seen:
            seen.add(href); links.append("https://www.ycombinator.com"+href)
            if len(links)>=limit: break
    return links

async def profile_to_external(page: Page, profile_url: str) -> Tuple[str, str]:
    await page.goto(profile_url, wait_until="domcontentloaded")
    name = ""
    try:
        node = page.locator("h1").first
        name = await node.inner_text(timeout=2000)
        name = name.strip()
    except: pass
    site = None
    candidates = [
        "a:has-text('Website')",
        "a[rel='noopener'][target='_blank']",
        "a[href^='http']:not([href*='ycombinator.com'])",
    ]
    for sel in candidates:
        try:
            link = page.locator(sel).first
            if link and link.count()>0:
                url = await link.get_attribute("href")
                if url and "ycombinator.com" not in url:
                    site = url; break
        except: pass
    return name or profile_url.split("/")[-1], site