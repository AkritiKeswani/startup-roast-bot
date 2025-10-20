from pydantic import BaseModel
from typing import Literal, Optional, List, Dict

class YCConfig(BaseModel):
    batch: Optional[str] = None
    limit: int = 24

class CustomConfig(BaseModel):
    urls: List[str] = []

class RunRequest(BaseModel):
    source: Literal["yc","custom"] = "yc"
    yc: YCConfig = YCConfig()
    custom: CustomConfig = CustomConfig()
    style: Literal["spicy","kind","deadpan"] = "spicy"
    max_steps: int = 6

class CompanyResult(BaseModel):
    name: str
    website: str
    title: str = ""
    hero: str = ""
    cta: str = ""
    roast: str = ""
    screenshot_url: Optional[str] = None
    status: Literal["done","skipped"] = "done"
    reason: Optional[str] = None