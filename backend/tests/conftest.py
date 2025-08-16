"""
Pytest configuration and fixtures for Streamlink Dashboard tests
"""
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.models import (
    User, PlatformConfig, SystemConfig, 
    RecordingSchedule, Recording, RecordingJob
)


# Test database URL - in-memory SQLite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

# Create test session factory
TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db_setup():
    """Set up test database with all tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(test_db_setup) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture
async def sample_user(db_session: AsyncSession) -> User:
    """Create a sample user for testing."""
    user = User(
        username="testuser",
        password_hash="hashed_password",
        is_admin=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def sample_platform_config(db_session: AsyncSession) -> PlatformConfig:
    """Create a sample platform configuration for testing."""
    config = PlatformConfig(
        platform_name="twitch",
        api_key="test_api_key",
        client_id="test_client_id",
        client_secret="test_client_secret",
        enabled=True
    )
    db_session.add(config)
    await db_session.commit()
    await db_session.refresh(config)
    return config


@pytest.fixture
async def sample_recording_schedule(db_session: AsyncSession) -> RecordingSchedule:
    """Create a sample recording schedule for testing."""
    schedule = RecordingSchedule(
        platform="twitch",
        streamer_id="123456",
        streamer_name="teststreamer",
        quality="best",
        output_path="/recordings",
        enabled=True
    )
    db_session.add(schedule)
    await db_session.commit()
    await db_session.refresh(schedule)
    return schedule


@pytest.fixture
async def sample_recording(db_session: AsyncSession, sample_recording_schedule: RecordingSchedule) -> Recording:
    """Create a sample recording for testing."""
    from datetime import datetime
    
    recording = Recording(
        schedule_id=sample_recording_schedule.id,
        file_path="/recordings/test.mp4",
        file_name="test.mp4",
        file_size=1024000,
        duration=3600.0,
        start_time=datetime.now(),
        platform="twitch",
        streamer_id="123456",
        streamer_name="teststreamer",
        status="completed"
    )
    db_session.add(recording)
    await db_session.commit()
    await db_session.refresh(recording)
    return recording


@pytest.fixture
async def sample_recording_job(db_session: AsyncSession, sample_recording_schedule: RecordingSchedule) -> RecordingJob:
    """Create a sample recording job for testing."""
    from datetime import datetime
    
    job = RecordingJob(
        schedule_id=sample_recording_schedule.id,
        status="completed",
        start_time=datetime.now(),
        end_time=datetime.now(),
        pid=12345
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    return job
