"""
Pydantic models for the Startup Roast Bot API.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    """Request model for starting a roast run."""
    source: str = Field(..., description="Source type: 'yc' or 'custom'")
    yc: Optional[Dict[str, Any]] = Field(None, description="YC-specific parameters")
    custom: Optional[Dict[str, Any]] = Field(None, description="Custom URL parameters")
    max_steps: int = Field(6, description="Maximum steps per site")
    style: str = Field("spicy", description="Roast style: spicy, kind, deadpan")


class YCParams(BaseModel):
    """YC directory parameters."""
    batch: Optional[str] = Field(None, description="YC batch filter (e.g., 'F25', 'S24')")
    limit: int = Field(24, description="Maximum number of companies to process")


class CustomParams(BaseModel):
    """Custom URL parameters."""
    urls: List[str] = Field(..., description="List of URLs to process")


class CompanyResult(BaseModel):
    """Result for a single company."""
    name: str
    website: str
    roast: Optional[str] = None
    screenshot_url: Optional[str] = None
    status: str = Field("pending", description="Status: pending, done, skipped, error")
    error_reason: Optional[str] = None
    summary: Optional[Dict[str, str]] = None  # title, hero, cta


class RunStatus(BaseModel):
    """Status of a roast run."""
    run_id: str
    status: str = Field(..., description="Status: running, completed, failed")
    created_at: datetime
    completed_at: Optional[datetime] = None
    total_companies: int = 0
    processed_companies: int = 0
    results: List[CompanyResult] = Field(default_factory=list)
    error_message: Optional[str] = None


class RunResponse(BaseModel):
    """Response model for run creation."""
    run_id: str
    status: str
    stream_url: str


class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    company: Optional[Dict[str, str]] = None
    roast: Optional[str] = None
    screenshot_url: Optional[str] = None
    status: str
    error_reason: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
