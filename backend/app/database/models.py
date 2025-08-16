"""
SQLAlchemy ORM models for Streamlink Dashboard
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text,
    ForeignKey, JSON, Float, BigInteger
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from .base import Base


class User(Base):
    """User authentication model"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PlatformConfig(Base):
    """Platform-specific configuration model"""
    __tablename__ = "platform_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    stream_url_pattern: Mapped[str] = mapped_column(String(500), nullable=False)
    quality_options: Mapped[str] = mapped_column(String(200), nullable=False)
    default_quality: Mapped[str] = mapped_column(String(20), default="best", nullable=False)
    additional_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SystemConfig(Base):
    """System-wide configuration model"""
    __tablename__ = "system_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    config_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    config_value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RotationPolicy(Base):
    """File rotation policy model"""
    __tablename__ = "rotation_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    policy_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # 'time', 'count', 'size'
    max_age_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # for time-based
    max_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # for count-based
    max_size_gb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # for size-based
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=0, index=True)  # higher number = higher priority
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    schedules: Mapped[list["RecordingSchedule"]] = relationship("RecordingSchedule", back_populates="rotation_policy")


class RecordingSchedule(Base):
    """Recording schedule model"""
    __tablename__ = "recording_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    streamer_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    streamer_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    quality: Mapped[str] = mapped_column(String(20), default="best", nullable=False)
    output_path: Mapped[str] = mapped_column(String(500), nullable=False)
    custom_arguments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rotation_policy_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("rotation_policies.id"), nullable=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    rotation_policy: Mapped[Optional["RotationPolicy"]] = relationship("RotationPolicy", back_populates="schedules")
    recordings: Mapped[list["Recording"]] = relationship("Recording", back_populates="schedule", cascade="all, delete-orphan")
    jobs: Mapped[list["RecordingJob"]] = relationship("RecordingJob", back_populates="schedule", cascade="all, delete-orphan")


class Recording(Base):
    """Recording file model"""
    __tablename__ = "recordings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey("recording_schedules.id"), nullable=False, index=True)
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
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    schedule: Mapped["RecordingSchedule"] = relationship("RecordingSchedule", back_populates="recordings")


class RecordingJob(Base):
    """Recording job execution model"""
    __tablename__ = "recording_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey("recording_schedules.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # 'pending', 'running', 'completed', 'failed'
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    schedule: Mapped["RecordingSchedule"] = relationship("RecordingSchedule", back_populates="jobs")
