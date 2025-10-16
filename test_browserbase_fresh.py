#!/usr/bin/env python3
"""
Test with fresh credentials to verify Browserbase API.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
API_KEY = os.environ.get("BROWSERBASE_API_KEY")
PROJECT_ID = os.environ.get("BROWSERBASE_PROJECT_ID")

print("🔍 Testing Browserbase API with fresh credentials")
print("=" * 60)

# Check for any hidden characters
print(f"API Key length: {len(API_KEY)}")
print(f"API Key first 10: '{API_KEY[:10]}'")
print(f"API Key last 10: '{API_KEY[-10:]}'")
print(f"Project ID length: {len(PROJECT_ID)}")
print(f"Project ID: '{PROJECT_ID}'")

# Test the API
url = "https://api.browserbase.com/v1/sessions"
headers = {
    "x-bb-api-key": API_KEY,
    "Content-Type": "application/json"
}
payload = {
    "projectId": PROJECT_ID
}

print(f"\n🌐 Making request to: {url}")
print(f"Headers: {headers}")
print(f"Payload: {payload}")

try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"📥 Response Headers: {dict(response.headers)}")
    print(f"📥 Response Body: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Session ID: {data.get('id')}")
        print(f"✅ Connect URL: {data.get('connectUrl')}")
    else:
        print(f"❌ Failed with status {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("If this still shows 401, the issue is with the credentials themselves.")
print("Please verify in the Browserbase dashboard that:")
print("1. The API key is active and not expired")
print("2. The Project ID matches the API key")
print("3. Both are copied exactly without extra spaces")
