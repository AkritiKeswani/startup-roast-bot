"""
Browserbase client for creating sessions and getting Playwright endpoints.
"""

import os
import requests
from typing import Dict, Any
from logutil import setup_logger

logger = setup_logger(__name__)

BROWSERBASE_API_KEY = os.environ["BROWSERBASE_API_KEY"]
BROWSERBASE_BASE_URL = "https://www.browserbase.com/v1"


class BrowserbaseClient:
    """Client for interacting with Browserbase API."""
    
    def __init__(self):
        self.api_key = BROWSERBASE_API_KEY
        self.base_url = BROWSERBASE_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_session(self, project_id: str = None) -> Dict[str, Any]:
        """Create a new Browserbase session."""
        try:
            payload = {
                "projectId": project_id,
                "region": "us-east-1"  # Default region
            }
            
            logger.info("Creating Browserbase session", project_id=project_id)
            
            response = requests.post(
                f"{self.base_url}/sessions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            session_data = response.json()
            logger.info("Created Browserbase session", session_id=session_data.get("id"))
            
            return session_data
            
        except Exception as e:
            logger.error("Failed to create Browserbase session", error=str(e))
            raise
    
    def get_playwright_endpoint(self, session_id: str) -> str:
        """Get the Playwright WebSocket endpoint for a session."""
        try:
            response = requests.get(
                f"{self.base_url}/sessions/{session_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            session_data = response.json()
            playwright_endpoint = session_data.get("playwrightWsEndpoint")
            
            if not playwright_endpoint:
                raise ValueError("No Playwright endpoint found in session data")
            
            logger.info("Retrieved Playwright endpoint", session_id=session_id)
            return playwright_endpoint
            
        except Exception as e:
            logger.error("Failed to get Playwright endpoint", session_id=session_id, error=str(e))
            raise
    
    def close_session(self, session_id: str) -> bool:
        """Close a Browserbase session."""
        try:
            response = requests.delete(
                f"{self.base_url}/sessions/{session_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info("Closed Browserbase session", session_id=session_id)
            return True
            
        except Exception as e:
            logger.error("Failed to close Browserbase session", session_id=session_id, error=str(e))
            return False


# Global client instance
browserbase_client = BrowserbaseClient()
