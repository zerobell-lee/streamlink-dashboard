"""
Schedule Repository - Data access layer for RecordingSchedule entities
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.models import RecordingSchedule


class ScheduleRepository:
    """Repository for RecordingSchedule data access operations"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    async def get_by_id(self, schedule_id: int) -> Optional[RecordingSchedule]:
        """Get schedule by ID"""
        result = await self.session.execute(
            select(RecordingSchedule)
            .where(RecordingSchedule.id == schedule_id)
        )
        return result.scalar_one_or_none()

    async def get_all_enabled(self) -> List[RecordingSchedule]:
        """Get all enabled schedules"""
        result = await self.session.execute(
            select(RecordingSchedule)
            .where(RecordingSchedule.enabled == True)
        )
        return result.scalars().all()

    async def get_rotation_enabled(self) -> List[RecordingSchedule]:
        """Get all schedules with rotation enabled"""
        result = await self.session.execute(
            select(RecordingSchedule)
            .where(RecordingSchedule.rotation_enabled == True)
        )
        return result.scalars().all()

    async def create(self, schedule: RecordingSchedule) -> RecordingSchedule:
        """Create new schedule"""
        self.session.add(schedule)
        await self.session.flush()  # Flush to get ID without committing
        await self.session.refresh(schedule)
        return schedule

    async def update(self, schedule: RecordingSchedule) -> RecordingSchedule:
        """Update existing schedule"""
        await self.session.merge(schedule)
        return schedule

    async def delete(self, schedule_id: int) -> bool:
        """Delete schedule by ID"""
        schedule = await self.get_by_id(schedule_id)
        if schedule:
            await self.session.delete(schedule)
            return True
        return False