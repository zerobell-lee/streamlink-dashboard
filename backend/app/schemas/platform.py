"""
Platform Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class PlatformConfigBase(BaseModel):
    """Base platform configuration schema"""
    platform: str = Field(..., description="Platform name")
    additional_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional platform settings")
    enabled: bool = Field(default=True, description="Whether platform is enabled")


class PlatformConfigCreate(PlatformConfigBase):
    """Schema for creating a platform configuration"""
    pass


class PlatformConfigUpdate(BaseModel):
    """Schema for updating a platform configuration"""
    additional_settings: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class PlatformConfigResponse(PlatformConfigBase):
    """Schema for platform configuration response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StreamInfoResponse(BaseModel):
    """Schema for stream information response"""
    platform: str
    streamer_id: str
    streamer_name: str
    title: str
    is_live: bool
    viewer_count: Optional[int] = None
    thumbnail_url: Optional[str] = None
    started_at: Optional[str] = None


class StreamUrlResponse(BaseModel):
    """Schema for stream URL response"""
    url: str
    quality: str
    format: str
    bandwidth: Optional[int] = None


class StreamUrlsResponse(BaseModel):
    """Schema for stream URLs response"""
    platform: str
    streamer_id: str
    stream_urls: list[StreamUrlResponse]


class StreamlinkArgsResponse(BaseModel):
    """Schema for Streamlink arguments response"""
    platform: str
    streamer_id: str
    quality: str
    arguments: list[str]
    command: str


class SupportedPlatformsResponse(BaseModel):
    """Schema for supported platforms response"""
    supported_platforms: list[str]
    total: int


class PlatformInitializationResponse(BaseModel):
    """Schema for platform initialization response"""
    message: str
    supported_platforms: list[str]
