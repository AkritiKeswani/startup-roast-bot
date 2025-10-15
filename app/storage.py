"""
S3 storage functionality for artifacts.
"""

import os
import json
import boto3
from typing import Optional
from botocore.exceptions import ClientError
from .logutil import setup_logger

logger = setup_logger(__name__)


class S3Storage:
    """S3 storage client for saving artifacts."""
    
    def __init__(self):
        self.bucket_name = os.environ.get("S3_BUCKET")
        if not self.bucket_name:
            raise ValueError("S3_BUCKET environment variable is required")
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
        )
    
    def put_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Upload bytes to S3 and return the URL."""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
                ContentType=content_type
            )
            
            # Generate signed URL (valid for 1 hour)
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=3600
            )
            
            logger.info("Uploaded bytes to S3", key=key, size=len(data))
            return url
            
        except ClientError as e:
            logger.error("Failed to upload bytes to S3", key=key, error=str(e))
            raise
    
    def put_json(self, key: str, data: dict) -> str:
        """Upload JSON data to S3 and return the URL."""
        json_data = json.dumps(data, indent=2, default=str)
        return self.put_bytes(key, json_data.encode('utf-8'), "application/json")
    
    def put_screenshot(self, run_id: str, company_slug: str, step: int, image_data: bytes) -> str:
        """Upload screenshot to S3 and return the URL."""
        key = f"runs/{run_id}/{company_slug}/step-{step}.png"
        return self.put_bytes(key, image_data, "image/png")
    
    def put_trace(self, run_id: str, company_slug: str, trace_data: dict) -> str:
        """Upload trace data to S3 and return the URL."""
        key = f"runs/{run_id}/{company_slug}/trace.json"
        return self.put_json(key, trace_data)
    
    def get_signed_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a signed URL for accessing an S3 object."""
        try:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
        except ClientError as e:
            logger.error("Failed to generate signed URL", key=key, error=str(e))
            raise


# Global storage instance
storage = S3Storage()
