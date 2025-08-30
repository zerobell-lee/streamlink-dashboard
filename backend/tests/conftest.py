"""
PyTest configuration and fixtures
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.database.models import Base
from app.core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db_engine():
    """Create test database engine"""
    # Use in-memory SQLite for testing
    test_db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(test_db_url, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine):
    """Create test database session"""
    async_session = async_sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.add = MagicMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def sample_recording_schedule_data():
    """Sample data for creating a recording schedule"""
    return {
        "platform": "twitch",
        "streamer_id": "test_streamer",
        "streamer_name": "Test Streamer",
        "quality": "best",
        "custom_arguments": "--output-format mp4",
        "enabled": True
    }


@pytest.fixture
def sample_rotation_policy_data():
    """Sample data for creating a rotation policy"""
    return {
        "name": "Test Policy",
        "policy_type": "time",
        "max_age_days": 30,
        "enabled": True,
        "priority": 1,
        "protect_favorites": True
    }
