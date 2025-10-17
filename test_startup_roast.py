#!/usr/bin/env python3
"""
Test roasting real startup websites.
"""
import asyncio
import requests
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv
import json

load_dotenv()

async def roast_website(url):
    try:
        print(f"\n🔥 Roasting: {url}")
        
        # Get credentials
        api_key = os.getenv('BROWSERBASE_API_KEY')
        project_id = os.getenv('BROWSERBASE_PROJECT_ID')
        grok_api_key = os.getenv('GROK_API_KEY')
        
        # Create session
        headers = {'x-bb-api-key': api_key, 'Content-Type': 'application/json'}
        payload = {'projectId': project_id}
        
        response = requests.post('https://api.browserbase.com/v1/sessions', headers=headers, json=payload)
        session_data = response.json()
        connect_url = session_data['connectUrl']
        
        # Connect with Playwright
        playwright = await async_playwright().start()
        browser = await playwright.chromium.connect_over_cdp(connect_url)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = context.pages[0] if context.pages else await context.new_page()
        
        # Navigate and extract content
        await page.goto(url, timeout=30000)
        
        # Extract content
        title = await page.title()
        
        hero = ""
        try:
            hero_element = await page.query_selector("h1")
            if hero_element:
                hero = await hero_element.text_content()
        except:
            pass
        
        cta = ""
        try:
            cta_element = await page.query_selector("a, button")
            if cta_element:
                cta = await cta_element.text_content()
        except:
            pass
        
        print(f"📄 Title: {title}")
        print(f"📄 Hero: {hero}")
        print(f"📄 CTA: {cta}")
        
        # Generate roast
        summary = {"title": title, "hero": hero, "cta": cta}
        
        payload = {
            "model": "grok-3",
            "temperature": 0.9,
            "max_tokens": 80,
            "messages": [
                {"role": "system", "content": "You are a witty startup critic. Generate a single, tasteful roast of a landing page in 1 sentence (max 180 chars). Focus on the value proposition, design, or messaging. Be clever but not mean."},
                {"role": "user", "content": f"Roast this landing page: {json.dumps(summary)}"}
            ],
        }
        
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {grok_api_key}"},
            json=payload, timeout=60
        )
        
        if response.status_code == 200:
            roast = response.json()["choices"][0]["message"]["content"].strip()
            print(f"🔥 ROAST: {roast}")
        else:
            print(f"❌ Grok API error: {response.status_code}")
        
        await browser.close()
        await playwright.stop()
        
    except Exception as e:
        print(f"❌ Error roasting {url}: {e}")

async def main():
    # Test with some real startup websites
    websites = [
        "https://example.com",
        "https://stripe.com",
        "https://linear.app",
        "https://notion.so"
    ]
    
    for url in websites:
        await roast_website(url)
        await asyncio.sleep(2)  # Brief pause between requests

if __name__ == "__main__":
    asyncio.run(main())
