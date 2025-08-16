"""
Platforms API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database.database import get_db
from app.database.models import PlatformConfig, User
from app.core.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_platforms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of platform configurations
    """
    result = await db.execute(select(PlatformConfig))
    platforms = result.scalars().all()
    
    return [
        {
            "id": platform.id,
            "platform": platform.platform,
            "stream_url_pattern": platform.stream_url_pattern,
            "quality_options": platform.quality_options,
            "default_quality": platform.default_quality,
            "additional_settings": platform.additional_settings,
            "enabled": platform.enabled
        }
        for platform in platforms
    ]
