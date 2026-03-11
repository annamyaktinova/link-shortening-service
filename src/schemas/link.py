from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ShortenRequest(BaseModel):
    original_url: str
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

class LinkResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    custom_alias: Optional[str]
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    original_url: str
    created_at: datetime
    clicks: int
    last_accessed: Optional[datetime]

    class Config:
        from_attributes = True

class UpdateLinkRequest(BaseModel):
    original_url: Optional[str] = None
    custom_alias: Optional[str] = None