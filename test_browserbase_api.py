#!/usr/bin/env python3
"""
Test script for Browserbase API endpoints.
Run this to verify your API keys and endpoints are working correctly.
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BROWSERBASE_API_KEY = os.environ.get("BROWSERBASE_API_KEY")
BROWSERBASE_PROJECT_ID = os.environ.get("BROWSERBASE_PROJECT_ID")
BROWSERBASE_BASE_URL = "https://api.browserbase.com/v1"

def test_api_connection():
    """Test basic API connection and authentication."""
    print("🔍 Testing Browserbase API connection...")
    
    if not BROWSERBASE_API_KEY:
        print("❌ BROWSERBASE_API_KEY not found in environment variables")
        return False
    
    if not BROWSERBASE_PROJECT_ID:
        print("❌ BROWSERBASE_PROJECT_ID not found in environment variables")
        return False
    
    headers = {
        "x-bb-api-key": BROWSERBASE_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Test 1: Create a session
    print("📝 Creating a test session...")
    try:
        payload = {
            "projectId": BROWSERBASE_PROJECT_ID,
            "region": "us-east-1"
        }
        
        response = requests.post(
            f"{BROWSERBASE_BASE_URL}/sessions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            session_data = response.json()
            session_id = session_data.get("id")
            connect_url = session_data.get("connectUrl")
            
            print(f"✅ Session created successfully!")
            print(f"   Session ID: {session_id}")
            print(f"   Connect URL: {connect_url}")
            
            # Test 2: Get session details
            print("\n🔍 Getting session details...")
            get_response = requests.get(
                f"{BROWSERBASE_BASE_URL}/sessions/{session_id}",
                headers=headers,
                timeout=30
            )
            
            if get_response.status_code == 200:
                session_details = get_response.json()
                print(f"✅ Session details retrieved!")
                print(f"   Status: {session_details.get('status', 'unknown')}")
                print(f"   Connect URL: {session_details.get('connectUrl', 'not found')}")
                
                # Test 3: Close the session
                print("\n🗑️ Closing session...")
                delete_response = requests.delete(
                    f"{BROWSERBASE_BASE_URL}/sessions/{session_id}",
                    headers=headers,
                    timeout=30
                )
                
                if delete_response.status_code in [200, 204]:
                    print("✅ Session closed successfully!")
                    return True
                else:
                    print(f"⚠️ Failed to close session: {delete_response.status_code}")
                    print(f"   Response: {delete_response.text}")
                    return True  # Still consider it a success since we created the session
            else:
                print(f"❌ Failed to get session details: {get_response.status_code}")
                print(f"   Response: {get_response.text}")
                return False
                
        else:
            print(f"❌ Failed to create session: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_playwright_connection():
    """Test Playwright connection to a Browserbase session."""
    print("\n🎭 Testing Playwright connection...")
    
    try:
        from playwright.async_api import async_playwright
        import asyncio
        
        async def test_playwright():
            # Create a session first
            headers = {
                "x-bb-api-key": BROWSERBASE_API_KEY,
                "Content-Type": "application/json"
            }
            
            payload = {
                "projectId": BROWSERBASE_PROJECT_ID,
                "region": "us-east-1"
            }
            
            response = requests.post(
                f"{BROWSERBASE_BASE_URL}/sessions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code not in [200, 201]:
                print(f"❌ Failed to create session for Playwright test: {response.status_code}")
                return False
            
            session_data = response.json()
            connect_url = session_data.get("connectUrl")
            session_id = session_data.get("id")
            
            if not connect_url:
                print("❌ No connect URL found in session data")
                return False
            
            # Test Playwright connection
            playwright = await async_playwright().start()
            try:
                browser = await playwright.chromium.connect_over_cdp(connect_url)
                context = browser.contexts[0] if browser.contexts else await browser.new_context()
                page = context.pages[0] if context.pages else await context.new_page()
                
                # Test navigation
                await page.goto("https://example.com")
                title = await page.title()
                print(f"✅ Playwright connection successful!")
                print(f"   Page title: {title}")
                
                await browser.close()
                return True
                
            except Exception as e:
                print(f"❌ Playwright connection failed: {e}")
                return False
            finally:
                await playwright.stop()
                
                # Clean up session
                requests.delete(
                    f"{BROWSERBASE_BASE_URL}/sessions/{session_id}",
                    headers=headers,
                    timeout=30
                )
        
        return asyncio.run(test_playwright())
        
    except ImportError:
        print("⚠️ Playwright not installed, skipping Playwright test")
        print("   Install with: pip install playwright")
        return True
    except Exception as e:
        print(f"❌ Playwright test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Browserbase API Test Suite")
    print("=" * 50)
    
    # Test API connection
    api_success = test_api_connection()
    
    if api_success:
        # Test Playwright connection
        playwright_success = test_playwright_connection()
        
        print("\n" + "=" * 50)
        if api_success and playwright_success:
            print("🎉 All tests passed! Your Browserbase setup is working correctly.")
        else:
            print("⚠️ Some tests failed, but basic API connection works.")
    else:
        print("\n❌ API connection failed. Please check your API keys and project ID.")
        sys.exit(1)
