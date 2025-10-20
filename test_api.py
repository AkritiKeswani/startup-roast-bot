#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Testing API Keys...")
print(f"BROWSERBASE_API_KEY: {'SET' if os.environ.get('BROWSERBASE_API_KEY') else 'NOT SET'}")
print(f"BROWSERBASE_PROJECT_ID: {'SET' if os.environ.get('BROWSERBASE_PROJECT_ID') else 'NOT SET'}")
print(f"GROK_API_KEY: {'SET' if os.environ.get('GROK_API_KEY') else 'NOT SET'}")

print("\n🧪 Testing Browserbase connection...")
try:
    from app import browserbase_client as bb
    sess = bb.create_session({})
    print(f"✅ Browserbase session created: {sess.get('id')}")
    
    ws = bb.connect_url(sess)
    print(f"✅ Connection URL: {ws[:50]}...")
    
except Exception as e:
    print(f"❌ Browserbase error: {e}")

print("\n🧪 Testing Grok connection...")
try:
    from app.llm_client import generate_roast
    test_summary = {"title": "Test", "hero": "Test Hero", "cta": "Test CTA"}
    roast = generate_roast(test_summary, "spicy")
    print(f"✅ Grok roast: {roast}")
except Exception as e:
    print(f"❌ Grok error: {e}")
