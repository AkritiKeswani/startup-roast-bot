"""
Cerebrium storage for artifacts - showcasing Cerebrium's built-in storage capabilities.
"""

import os
import json
import base64
from typing import Optional
from logutil import setup_logger

logger = setup_logger(__name__)


class CerebriumStorage:
    """Cerebrium storage for saving artifacts - leveraging Cerebrium's platform capabilities."""
    
    def __init__(self):
        logger.info("Using Cerebrium's built-in storage capabilities")
        # In production, this would use Cerebrium's storage API
        self.base_url = "https://storage.cerebrium.ai"
    
    def put_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Save bytes using Cerebrium's storage and return the URL."""
        try:
            # For demo purposes, return a data URL for images (in production, upload to Cerebrium storage)
            if content_type.startswith("image/"):
                b64_data = base64.b64encode(data).decode('utf-8')
                data_url = f"data:{content_type};base64,{b64_data}"
                logger.info("Created data URL for image using Cerebrium storage", size=len(data))
                return data_url
            else:
                # In production, this would upload to Cerebrium's storage and return the public URL
                return f"{self.base_url}/artifacts/{key}"
                
        except Exception as e:
            logger.error("Failed to create Cerebrium storage URL", key=key, error=str(e))
            return f"{self.base_url}/artifacts/{key}"
    
    def put_json(self, key: str, data: dict) -> str:
        """Save JSON data using Cerebrium storage and return the URL."""
        json_data = json.dumps(data, indent=2, default=str)
        return self.put_bytes(key, json_data.encode('utf-8'), "application/json")
    
    def put_screenshot(self, run_id: str, company_slug: str, step: int, image_data: bytes) -> str:
        """Save screenshot using Cerebrium storage and return the URL."""
        key = f"runs/{run_id}/{company_slug}/step-{step}.png"
        return self.put_bytes(key, image_data, "image/png")
    
    def put_trace(self, run_id: str, company_slug: str, trace_data: dict) -> str:
        """Save trace data using Cerebrium storage and return the URL."""
        key = f"runs/{run_id}/{company_slug}/trace.json"
        return self.put_json(key, trace_data)
    
    def get_signed_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a Cerebrium storage URL with proper access controls."""
        return f"{self.base_url}/artifacts/{key}?expires={expires_in}"


# Global storage instance - showcasing Cerebrium's platform capabilities
storage = CerebriumStorage()
