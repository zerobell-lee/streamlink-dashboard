"""
Unit of Work pattern implementation for transaction management
"""
from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.recording_repository import RecordingRepository
from app.repositories.schedule_repository import ScheduleRepository


class UnitOfWorkProtocol(Protocol):
    """Unit of Work protocol defining the interface"""
    recordings: RecordingRepository
    schedules: ScheduleRepository

    async def __aenter__(self):
        """Async context manager entry"""
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        ...

    async def commit(self):
        """Commit all changes"""
        ...

    async def rollback(self):
        """Rollback all changes"""
        ...


class AsyncSQLAlchemyUnitOfWork:
    """SQLAlchemy implementation of Unit of Work pattern"""

    def __init__(self, session_factory):
        """Initialize with session factory"""
        self.session_factory = session_factory
        self._session: AsyncSession = None

    async def __aenter__(self):
        """Start new transaction"""
        self._session = self.session_factory()

        # Initialize repositories with the same session
        self.recordings = RecordingRepository(self._session)
        self.schedules = ScheduleRepository(self._session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """End transaction"""
        if exc_type is not None:
            await self.rollback()
        await self._session.close()

    async def commit(self):
        """Commit transaction"""
        await self._session.commit()

    async def rollback(self):
        """Rollback transaction"""
        await self._session.rollback()

    async def flush(self):
        """Flush changes without committing"""
        await self._session.flush()