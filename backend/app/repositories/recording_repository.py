"""
Recording Repository - Data access layer for Recording entities
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.models import Recording, RecordingSchedule


class RecordingRepository:
    """Repository for Recording data access operations"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    async def get_active_recordings_for_schedule(self, schedule_id: int) -> List[Recording]:
        """Get all active recordings for a schedule"""
        result = await self.session.execute(
            select(Recording).where(
                Recording.schedule_id == schedule_id,
                Recording.status.in_(["recording", "pending"])
            )
        )
        return result.scalars().all()

    async def has_active_recordings_for_schedule(self, schedule_id: int) -> bool:
        """Check if schedule has any active recordings"""
        recordings = await self.get_active_recordings_for_schedule(schedule_id)
        return len(recordings) > 0

    async def get_by_id(self, recording_id: int) -> Optional[Recording]:
        """Get recording by ID"""
        result = await self.session.execute(
            select(Recording)
            .options(selectinload(Recording.schedule))
            .where(Recording.id == recording_id)
        )
        return result.scalar_one_or_none()

    async def get_all_for_schedule(self, schedule_id: int) -> List[Recording]:
        """Get all recordings for a schedule"""
        result = await self.session.execute(
            select(Recording)
            .where(Recording.schedule_id == schedule_id)
            .order_by(Recording.created_at.desc())
        )
        return result.scalars().all()

    async def create(self, recording: Recording) -> Recording:
        """Create new recording"""
        self.session.add(recording)
        await self.session.flush()  # Flush to get ID without committing
        await self.session.refresh(recording)
        return recording

    async def update(self, recording: Recording) -> Recording:
        """Update existing recording"""
        await self.session.merge(recording)
        return recording

    async def delete(self, recording_id: int) -> bool:
        """Delete recording by ID"""
        recording = await self.get_by_id(recording_id)
        if recording:
            await self.session.delete(recording)
            return True
        return False