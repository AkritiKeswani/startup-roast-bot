"""
S3 storage for artifacts - using AWS S3 for storing screenshots and traces.
"""

import os
import json
import base64
import boto3
from typing import Optional
from botocore.exceptions import ClientError
from logutil import setup_logger

logger = setup_logger(__name__)


class S3Storage:
    """S3 storage for saving artifacts."""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.environ.get('S3_BUCKET')
        
        if not self.bucket_name:
            logger.warning("S3_BUCKET not set, using fallback storage")
            self.bucket_name = None
    
    def put_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Save bytes to S3 and return the URL."""
        try:
            if not self.bucket_name:
                # Fallback to data URL for local development
                if content_type.startswith("image/"):
                    b64_data = base64.b64encode(data).decode('utf-8')
                    return f"data:{content_type};base64,{b64_data}"
                else:
                    return f"fallback://storage/{key}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
                ContentType=content_type
            )
            
            # Generate public URL
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
            logger.info("Uploaded to S3", key=key, size=len(data))
            return url
                
        except ClientError as e:
            logger.error("Failed to upload to S3", key=key, error=str(e))
            # Fallback to data URL for images
            if content_type.startswith("image/"):
                b64_data = base64.b64encode(data).decode('utf-8')
                return f"data:{content_type};base64,{b64_data}"
            return f"error://storage/{key}"
        except Exception as e:
            logger.error("Failed to upload to S3", key=key, error=str(e))
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
            logger.error("Failed to generate signed URL", key=key, error=str(e))
            return f"error://storage/{key}"


# Global storage instance
storage = S3Storage()
