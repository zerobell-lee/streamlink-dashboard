"""
Registry-based Platform Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# Platform Definition Schemas (Registry-based)
class PlatformDefinitionResponse(BaseModel):
    """Schema for platform definition from registry"""
    name: str
    display_name: str
    description: str
    requires_auth: bool
    supports_chat: bool
    supports_vod: bool
    help_text: str
    setup_instructions: str
    config_schema: Dict[str, Any]
    supported_qualities: List[str]
    default_streamlink_args: List[str]
    default_output_format: str
    supported_output_formats: List[str]
    default_filename_template: str


class PlatformDefinitionListResponse(BaseModel):
    """Schema for list of available platform definitions"""
    platforms: List[PlatformDefinitionResponse]
    total: int


# User Configuration Schemas (Database-based)
class PlatformUserConfigBase(BaseModel):
    """Base platform user configuration schema"""
    platform_name: str = Field(..., description="Platform name")
    user_credentials: Dict[str, Any] = Field(default_factory=dict, description="User credentials (API keys, tokens)")
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom streamlink settings")


class PlatformUserConfigCreate(BaseModel):
    """Schema for creating a platform user configuration"""
    user_credentials: Optional[Dict[str, Any]] = Field(default_factory=dict)
    custom_settings: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PlatformUserConfigUpdate(BaseModel):
    """Schema for updating a platform user configuration"""
    user_credentials: Optional[Dict[str, Any]] = None
    custom_settings: Optional[Dict[str, Any]] = None


class PlatformUserConfigResponse(PlatformUserConfigBase):
    """Schema for platform user configuration response"""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Combined Platform Information
class PlatformInfoResponse(BaseModel):
    """Schema combining platform definition and user configuration"""
    definition: PlatformDefinitionResponse
    user_config: Optional[PlatformUserConfigResponse] = None
    is_configured: bool


class PlatformListResponse(BaseModel):
    """Schema for comprehensive platform list"""
    platforms: List[PlatformInfoResponse]
    total: int


# Configuration Schema Response
class PlatformSchemaResponse(BaseModel):
    """Schema for platform configuration schema"""
    platform_name: str
    schema: Dict[str, Any]


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
