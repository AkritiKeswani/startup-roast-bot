"""
Simple storage for artifacts - using data URLs for screenshots and in-memory for traces.
"""

import json
import base64
from typing import Optional
from logutil import setup_logger

logger = setup_logger(__name__)


class SimpleStorage:
    """Simple storage using data URLs for screenshots."""
    
    def __init__(self):
        logger.info("Using simple data URL storage for screenshots")
    
    def put_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Convert bytes to data URL."""
        try:
            if content_type.startswith("image/"):
                b64_data = base64.b64encode(data).decode('utf-8')
                data_url = f"data:{content_type};base64,{b64_data}"
                logger.info("Created data URL for image", key=key, size=len(data))
                return data_url
            else:
                # For non-images, return a simple identifier
                return f"data://{key}"
                
        except Exception as e:
            logger.error("Failed to create data URL", extra={'extra_fields': {'key': key, 'error': str(e)}})
            return f"error://storage/{key}"
    
    def put_json(self, key: str, data: dict) -> str:
        """Save JSON data to S3 and return the URL."""
        json_data = json.dumps(data, indent=2, default=str)
        return self.put_bytes(key, json_data.encode('utf-8'), "application/json")
    
    def put_screenshot(self, run_id: str, company_slug: str, step: int, image_data: bytes) -> str:
        """Save screenshot to S3 and return the URL."""
        key = f"runs/{run_id}/{company_slug}/step-{step}.png"
        return self.put_bytes(key, image_data, "image/png")
    
    def put_trace(self, run_id: str, company_slug: str, trace_data: dict) -> str:
        """Save trace data to S3 and return the URL."""
        key = f"runs/{run_id}/{company_slug}/trace.json"
        return self.put_json(key, trace_data)
    
    def get_signed_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a signed S3 URL with proper access controls."""
        try:
            if not self.bucket_name:
                return f"fallback://storage/{key}"
            
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error("Failed to generate signed URL", extra={'extra_fields': {'key': key, 'error': str(e)}})
            return f"error://storage/{key}"


# Global storage instance
storage = SimpleStorage()
