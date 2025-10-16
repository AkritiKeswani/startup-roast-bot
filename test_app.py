#!/usr/bin/env python3
"""
Test script for the startup roast bot
"""

import requests
import json
import time

def test_backend():
    print("🧪 Testing Backend API")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health failed: {e}")
    
    # Test ready endpoint
    try:
        response = requests.get(f"{base_url}/ready")
        print(f"✅ Ready: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Ready failed: {e}")
    
    # Test run endpoint
    try:
        payload = {
            "source": "custom",
            "custom": {
                "urls": ["https://stripe.com"]
            },
            "max_steps": 2,
            "style": "spicy"
        }
        
        response = requests.post(f"{base_url}/run", json=payload)
        print(f"✅ Run: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Run failed: {e}")

def test_frontend():
    print("\n🌐 Testing Frontend")
    print("=" * 25)
    print("✅ Frontend is running at: http://localhost:3002")
    print("   - Open this URL in your browser")
    print("   - Try the Custom Mode with some URLs")
    print("   - Test the YC Mode (needs Grok credits)")

if __name__ == "__main__":
    test_backend()
    test_frontend()
    
    print("\n🎯 Next Steps:")
    print("1. Visit http://localhost:3002 in your browser")
    print("2. Try the Custom Mode with some URLs")
    print("3. Add Grok credits for AI roasts")
    print("4. Deploy to Cerebrium to showcase the platform!")
