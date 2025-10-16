#!/usr/bin/env python3
"""
Debug script to test Browserbase API with detailed logging.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BROWSERBASE_API_KEY = os.environ.get("BROWSERBASE_API_KEY")
BROWSERBASE_PROJECT_ID = os.environ.get("BROWSERBASE_PROJECT_ID")
BROWSERBASE_BASE_URL = "https://api.browserbase.com/v1"

print("🔍 Debug Browserbase API Test")
print("=" * 50)
print(f"API Key: {BROWSERBASE_API_KEY[:10]}...{BROWSERBASE_API_KEY[-5:]}")
print(f"Project ID: {BROWSERBASE_PROJECT_ID}")
print(f"Base URL: {BROWSERBASE_BASE_URL}")

headers = {
    "x-bb-api-key": BROWSERBASE_API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "projectId": BROWSERBASE_PROJECT_ID,
    "region": "us-east-1"
}

print(f"\n📤 Request Headers:")
for key, value in headers.items():
    print(f"   {key}: {value}")

print(f"\n📤 Request Payload:")
print(json.dumps(payload, indent=2))

print(f"\n🌐 Making request to: {BROWSERBASE_BASE_URL}/sessions")

try:
    response = requests.post(
        f"{BROWSERBASE_BASE_URL}/sessions",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"📥 Response Headers:")
    for key, value in response.headers.items():
        print(f"   {key}: {value}")
    
    print(f"\n📥 Response Body:")
    try:
        response_json = response.json()
        print(json.dumps(response_json, indent=2))
    except:
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
