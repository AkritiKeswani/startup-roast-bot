"""
Pydantic models for the Startup Roast Bot API.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class RoastRequest(BaseModel):
    """Request model for starting a roast session."""
    startup_url: HttpUrl = Field(..., description="URL of the startup website to roast")
    roast_style: Optional[str] = Field("savage", description="Style of roast: savage, constructive, humorous")
    focus_areas: Optional[List[str]] = Field(
        default=["design", "copy", "ux", "value_prop"],
        description="Areas to focus the roast on"
    )


class RoastStep(BaseModel):
    """Individual step in a roast session."""
    timestamp: datetime
    message: str
    step_type: str = Field(..., description="Type of step: info, success, error, warning")


class RoastSession(BaseModel):
    """Complete roast session with all steps and results."""
    id: str
    startup_url: str
    status: str = Field(..., description="Session status: running, completed, failed")
    created_at: datetime
    completed_at: Optional[datetime] = None
    steps: List[RoastStep] = Field(default_factory=list)
    final_roast: Optional[str] = None
    s3_screenshot_url: Optional[str] = None
    error_message: Optional[str] = None


class RoastResponse(BaseModel):
    """Response model for roast session creation."""
    session_id: str
    status: str
    message: str


class GeminiAnalysis(BaseModel):
    """Analysis result from Gemini Computer Use."""
    website_summary: str
    design_issues: List[str]
    copy_issues: List[str]
    ux_issues: List[str]
    value_prop_clarity: str
    overall_score: int = Field(..., ge=1, le=10)
    needs_more_screenshots: bool = False
    screenshot_instructions: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)


class GrokRoast(BaseModel):
    """Generated roast from Grok LLM."""
    roast_text: str
    roast_style: str
    key_critiques: List[str]
    suggestions: List[str]
    roast_score: int = Field(..., ge=1, le=10)
