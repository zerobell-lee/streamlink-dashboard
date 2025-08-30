"""
SQLAlchemy ORM models for Streamlink Dashboard
"""
from datetime import datetime
from sqlalchemy.sql import func as sql_func
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text,
    ForeignKey, JSON, Float, BigInteger
)
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql import func


def get_local_now():
    """Get current time in system timezone"""
    return datetime.now()


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class User(Base):
    """User authentication model"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now, onupdate=get_local_now)


class PlatformConfig(Base):
    """Platform configuration model"""
    __tablename__ = "platform_configs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    additional_settings: Mapped[Dict] = mapped_column(JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now, onupdate=get_local_now)


class SystemConfig(Base):
    """System-wide configuration model"""
    __tablename__ = "system_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    config_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    config_value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now, onupdate=get_local_now)




class RecordingSchedule(Base):
    """Recording schedule model"""
    __tablename__ = "recording_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    streamer_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    streamer_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    quality: Mapped[str] = mapped_column(String(20), default="best", nullable=False)
    custom_arguments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Inline rotation settings
    rotation_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    rotation_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'time', 'count', 'size'
    max_age_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # for time-based
    max_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # for count-based
    max_size_gb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # for size-based
    protect_favorites: Mapped[bool] = mapped_column(Boolean, default=True)  # protect favorite recordings
    delete_empty_files: Mapped[bool] = mapped_column(Boolean, default=True)  # delete empty files
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now, onupdate=get_local_now)

    # Relationships
    recordings: Mapped[list["Recording"]] = relationship("Recording", back_populates="schedule")
    jobs: Mapped[list["RecordingJob"]] = relationship("RecordingJob", back_populates="schedule", cascade="all, delete-orphan")


class Recording(Base):
    """Recording file model"""
    __tablename__ = "recordings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    schedule_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("recording_schedules.id", ondelete="SET NULL"), nullable=True, index=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # in seconds
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    streamer_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    streamer_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    quality: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="completed", nullable=False, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now, onupdate=get_local_now)

    # Relationships
    schedule: Mapped[Optional["RecordingSchedule"]] = relationship("RecordingSchedule", back_populates="recordings")


class RecordingJob(Base):
    """Recording job execution model"""
    __tablename__ = "recording_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey("recording_schedules.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # 'pending', 'running', 'completed', 'failed'
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now, onupdate=get_local_now)

    # Relationships
    schedule: Mapped["RecordingSchedule"] = relationship("RecordingSchedule", back_populates="jobs")
