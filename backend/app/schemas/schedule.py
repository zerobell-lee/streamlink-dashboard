"""
Pydantic schemas for RecordingSchedule
"""
from pydantic import BaseModel, Field, field_serializer, field_validator
from typing import Optional
from datetime import datetime


class RecordingScheduleBase(BaseModel):
    """Base schema for RecordingSchedule"""
    platform: str = Field(..., description="Platform name (twitch, youtube, sooplive)", min_length=1, max_length=50)
    streamer_id: str = Field(..., description="Streamer identifier", min_length=1, max_length=100)
    streamer_name: str = Field(..., description="Streamer display name", min_length=1, max_length=100)
    quality: str = Field(default="best", description="Stream quality", min_length=1, max_length=20)
    custom_arguments: Optional[str] = Field(None, description="Custom Streamlink arguments", max_length=1000)
    enabled: bool = Field(default=True, description="Whether the schedule is enabled")
    
    # Output file configuration
    output_format: Optional[str] = Field(None, description="Output file format (mp4, ts, mkv, etc.)", max_length=10)
    filename_template: Optional[str] = Field(None, description="Filename template string", max_length=500)
    
    # Inline rotation settings
    rotation_enabled: bool = Field(default=False, description="Whether rotation is enabled")
    rotation_type: Optional[str] = Field(None, description="Rotation type (time, count, size)")
    max_age_days: Optional[int] = Field(None, description="Maximum age in days (time-based)")
    max_count: Optional[int] = Field(None, description="Maximum file count (count-based)")
    max_size_gb: Optional[int] = Field(None, description="Maximum size in GB (size-based)")
    protect_favorites: bool = Field(default=True, description="Protect favorite recordings")
    delete_empty_files: bool = Field(default=True, description="Delete empty files")

    @field_validator('filename_template')
    @classmethod
    def validate_filename_template(cls, v):
        """Validate filename template syntax"""
        if v is not None and v.strip():
            try:
                from app.services.output_filename_template import OutputFileNameTemplate
                # Test template creation and validation
                template_engine = OutputFileNameTemplate(v)
                # Test template generation with sample data
                template_engine.preview_filename()
                return v
            except Exception as e:
                raise ValueError(f"Invalid filename template: {str(e)}")
        return v


class RecordingScheduleCreate(RecordingScheduleBase):
    """Schema for creating a new RecordingSchedule"""
    pass


class RecordingScheduleUpdate(BaseModel):
    """Schema for updating a RecordingSchedule"""
    platform: Optional[str] = Field(None, description="Platform name", min_length=1, max_length=50)
    streamer_id: Optional[str] = Field(None, description="Streamer identifier", min_length=1, max_length=100)
    streamer_name: Optional[str] = Field(None, description="Streamer display name", min_length=1, max_length=100)
    quality: Optional[str] = Field(None, description="Stream quality", min_length=1, max_length=20)
    custom_arguments: Optional[str] = Field(None, description="Custom Streamlink arguments", max_length=1000)
    enabled: Optional[bool] = Field(None, description="Whether the schedule is enabled")
    
    # Output file configuration
    output_format: Optional[str] = Field(None, description="Output file format (mp4, ts, mkv, etc.)", max_length=10)
    filename_template: Optional[str] = Field(None, description="Filename template string", max_length=500)
    
    # Inline rotation settings
    rotation_enabled: Optional[bool] = Field(None, description="Whether rotation is enabled")
    rotation_type: Optional[str] = Field(None, description="Rotation type (time, count, size)")
    max_age_days: Optional[int] = Field(None, description="Maximum age in days (time-based)")
    max_count: Optional[int] = Field(None, description="Maximum file count (count-based)")
    max_size_gb: Optional[int] = Field(None, description="Maximum size in GB (size-based)")
    protect_favorites: Optional[bool] = Field(None, description="Protect favorite recordings")
    delete_empty_files: Optional[bool] = Field(None, description="Delete empty files")

    @field_validator('filename_template')
    @classmethod
    def validate_filename_template(cls, v):
        """Validate filename template syntax"""
        if v is not None and v.strip():
            try:
                from app.services.output_filename_template import OutputFileNameTemplate
                # Test template creation and validation
                template_engine = OutputFileNameTemplate(v)
                # Test template generation with sample data
                template_engine.preview_filename()
                return v
            except Exception as e:
                raise ValueError(f"Invalid filename template: {str(e)}")
        return v


class RecordingScheduleResponse(RecordingScheduleBase):
    """Schema for RecordingSchedule response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        """Serialize datetime using system timezone"""
        if dt is None:
            return None
        # Use local system timezone
        return dt.isoformat()
    
    class Config:
        from_attributes = True


class ScheduleStatusResponse(BaseModel):
    """Schema for schedule status response"""
    schedule_id: int
    platform: str
    streamer_id: str
    streamer_name: str
    enabled: bool
    monitoring_active: bool
    last_check: str
    
    class Config:
        from_attributes = True


class MonitoringConfig(BaseModel):
    """Configuration for monitoring behavior"""
    check_interval_seconds: int = Field(default=60, description="Interval between stream checks in seconds", ge=30, le=3600)
    max_concurrent_recordings: int = Field(default=5, description="Maximum number of concurrent recordings", ge=1, le=20)
    retry_on_failure: bool = Field(default=True, description="Retry recording on failure")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts", ge=0, le=10)
