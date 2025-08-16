"""
Schedules API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database.database import get_db
from app.database.models import RecordingSchedule, User
from app.core.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_schedules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of recording schedules
    """
    result = await db.execute(select(RecordingSchedule))
    schedules = result.scalars().all()
    
    return [
        {
            "id": schedule.id,
            "name": schedule.name,
            "platform": schedule.platform,
            "streamer_id": schedule.streamer_id,
            "streamer_name": schedule.streamer_name,
            "cron_expression": schedule.cron_expression,
            "output_path": schedule.output_path,
            "enabled": schedule.enabled,
            "created_at": schedule.created_at
        }
        for schedule in schedules
    ]
