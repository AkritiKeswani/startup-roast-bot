#!/usr/bin/env python3
"""
Simple test script to verify Browserbase connection works
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
api_key = os.getenv("BROWSERBASE_API_KEY")
project_id = os.getenv("BROWSERBASE_PROJECT_ID")

print(f"API Key: {api_key[:10]}..." if api_key else "❌ No API key")
print(f"Project ID: {project_id}" if project_id else "❌ No Project ID")

if not api_key or not project_id:
    print("❌ Missing credentials!")
    exit(1)

# Test Browserbase API
headers = {
    "x-bb-api-key": api_key,
    "Content-Type": "application/json"
}

payload = {
    "projectId": project_id,
    "region": "us-east-1"
}

print("\n🧪 Testing Browserbase API...")
try:
    response = requests.post(
        "https://api.browserbase.com/v1/sessions",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        session_data = response.json()
        print("✅ SUCCESS! Browserbase is working!")
        print(f"Session ID: {session_data.get('id')}")
        print(f"Connect URL: {session_data.get('connectUrl', 'N/A')}")
    else:
        print(f"❌ FAILED! Status: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
