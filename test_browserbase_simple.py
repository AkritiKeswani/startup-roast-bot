#!/usr/bin/env python3
"""
Simple test to check if Browserbase API key works at all.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BROWSERBASE_API_KEY = os.environ.get("BROWSERBASE_API_KEY")
BROWSERBASE_PROJECT_ID = os.environ.get("BROWSERBASE_PROJECT_ID")

print("🔍 Testing Browserbase API Key Validity")
print("=" * 50)

# Test 1: Try to get projects (if this endpoint exists)
print("📝 Testing projects endpoint...")
headers = {
    "x-bb-api-key": BROWSERBASE_API_KEY,
    "Content-Type": "application/json"
}

try:
    response = requests.get(
        "https://api.browserbase.com/v1/projects",
        headers=headers,
        timeout=30
    )
    print(f"Projects endpoint status: {response.status_code}")
    if response.status_code == 200:
        print("✅ API key is valid!")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Projects endpoint failed: {response.text}")
except Exception as e:
    print(f"❌ Projects endpoint error: {e}")

# Test 2: Try different header format
print("\n📝 Testing alternative header format...")
headers_alt = {
    "Authorization": f"Bearer {BROWSERBASE_API_KEY}",
    "Content-Type": "application/json"
}

try:
    response = requests.post(
        "https://api.browserbase.com/v1/sessions",
        headers=headers_alt,
        json={"projectId": BROWSERBASE_PROJECT_ID, "region": "us-east-1"},
        timeout=30
    )
    print(f"Bearer token status: {response.status_code}")
    if response.status_code != 401:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Bearer token error: {e}")

# Test 3: Try with different API version
print("\n📝 Testing v2 API...")
try:
    response = requests.post(
        "https://api.browserbase.com/v2/sessions",
        headers=headers,
        json={"projectId": BROWSERBASE_PROJECT_ID, "region": "us-east-1"},
        timeout=30
    )
    print(f"V2 API status: {response.status_code}")
    if response.status_code != 401:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ V2 API error: {e}")
