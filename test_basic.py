#!/usr/bin/env python3
"""
Basic test to verify the app structure works without external APIs
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from app.models import RunRequest, RunResponse, CompanyResult
        print("✅ Models imported successfully")
        
        from app.logutil import setup_logger
        logger = setup_logger("test")
        print("✅ Logger setup successfully")
        
        print("✅ All basic imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_models():
    """Test that Pydantic models work"""
    try:
        from app.models import RunRequest, RunResponse, CompanyResult
        
        # Test RunRequest
        request = RunRequest(
            source="yc",
            yc={"batch": "F25", "limit": 5},
            style="spicy"
        )
        print("✅ RunRequest model works")
        
        # Test CompanyResult
        result = CompanyResult(
            name="Test Company",
            website="https://test.com",
            roast="This is a test roast",
            status="done"
        )
        print("✅ CompanyResult model works")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_logger():
    """Test logger functionality"""
    try:
        from app.logutil import setup_logger, log_with_context
        
        logger = setup_logger("test")
        logger.info("Test log message")
        
        log_with_context(logger, "info", "Test with context", test_key="test_value")
        print("✅ Logger functionality works")
        
        return True
        
    except Exception as e:
        print(f"❌ Logger test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Startup Roast Bot - Basic Structure")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_models()
    success &= test_logger()
    
    if success:
        print("\n✅ All basic tests passed!")
        print("The app structure is working correctly.")
        print("\nNext steps:")
        print("1. Set up your API keys in .env file:")
        print("   - BROWSERBASE_API_KEY")
        print("   - GROK_API_KEY")
        print("2. Run: python test_scraping.py (for full scraping test)")
        print("3. Run: cd app && uvicorn main:app --host 0.0.0.0 --port 5000")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1)