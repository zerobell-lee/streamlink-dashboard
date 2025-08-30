"""
Recording Pydantic schemas
"""
from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime


class RecordingBase(BaseModel):
    """Base recording schema"""
    file_path: str = Field(..., description="Path to the recording file")
    file_name: str = Field(..., description="Name of the recording file")
    file_size: int = Field(..., description="Size of the recording file in bytes")
    start_time: datetime = Field(..., description="Recording start time")
    end_time: Optional[datetime] = Field(None, description="Recording end time")
    duration: Optional[int] = Field(None, description="Recording duration in seconds")
    platform: str = Field(..., description="Streaming platform")
    streamer_id: str = Field(..., description="Streamer ID")
    streamer_name: str = Field(..., description="Streamer name")
    quality: str = Field(..., description="Recording quality")
    status: str = Field(default="completed", description="Recording status")
    error_message: Optional[str] = Field(None, description="Error message if recording failed")
    is_favorite: bool = Field(default=False, description="Favorite status")


class RecordingCreate(RecordingBase):
    """Schema for creating a recording"""
    schedule_id: int = Field(..., description="Associated schedule ID")


class RecordingUpdate(BaseModel):
    """Schema for updating a recording"""
    file_name: Optional[str] = None
    is_favorite: Optional[bool] = None
    status: Optional[str] = None


class RecordingResponse(RecordingBase):
    """Schema for recording response"""
    id: int
    schedule_id: Optional[int] = Field(None, description="Associated schedule ID (nullable)")
    created_at: datetime
    updated_at: datetime

    @field_serializer('start_time', 'end_time', 'created_at', 'updated_at')
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        """Serialize datetime using system timezone"""
        if dt is None:
            return None
        # Use local system timezone
        return dt.isoformat()

    class Config:
        from_attributes = True
