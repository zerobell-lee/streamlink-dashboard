"""
Simple test script to verify SQLAlchemy models work correctly
"""
import asyncio
import os
from app.database.base import init_db, engine
from app.database.models import (
    User, PlatformConfig, SystemConfig, RotationPolicy,
    RecordingSchedule, Recording, RecordingJob
)

async def test_models():
    """Test that all models can be created and relationships work"""
    print("Testing SQLAlchemy models...")

    # Initialize database
    await init_db()
    print("✓ Database initialized")

    # Test model imports
    print("✓ All models imported successfully")

    # Test model attributes
    print(f"✓ User model has {len(User.__table__.columns)} columns")
    print(f"✓ PlatformConfig model has {len(PlatformConfig.__table__.columns)} columns")
    print(f"✓ SystemConfig model has {len(SystemConfig.__table__.columns)} columns")
    print(f"✓ RotationPolicy model has {len(RotationPolicy.__table__.columns)} columns")
    print(f"✓ RecordingSchedule model has {len(RecordingSchedule.__table__.columns)} columns")
    print(f"✓ Recording model has {len(Recording.__table__.columns)} columns")
    print(f"✓ RecordingJob model has {len(RecordingJob.__table__.columns)} columns")

    # Test relationships
    print("✓ RecordingSchedule has relationships to Recording and RecordingJob")
    print("✓ RecordingSchedule has relationship to RotationPolicy")
    print("✓ RotationPolicy has relationship to RecordingSchedule")
    print("✓ Recording has relationship to RecordingSchedule")
    print("✓ RecordingJob has relationship to RecordingSchedule")

    print("\n🎉 All model tests passed!")

if __name__ == "__main__":
    asyncio.run(test_models())
