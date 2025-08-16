"""
System API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import psutil
import os

from app.database.database import get_db
from app.database.models import SystemConfig, User
from app.core.auth import get_current_admin_user
from app.core.config import settings

router = APIRouter()


@router.get("/status")
async def get_system_status(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get system status information
    """
    # Disk usage
    disk_usage = psutil.disk_usage(settings.RECORDINGS_DIR)
    
    # Memory usage
    memory = psutil.virtual_memory()
    
    return {
        "disk": {
            "total": disk_usage.total,
            "used": disk_usage.used,
            "free": disk_usage.free,
            "percent": disk_usage.percent
        },
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent
        },
        "recordings_dir": settings.RECORDINGS_DIR,
        "max_file_size": settings.MAX_FILE_SIZE
    }


@router.get("/config", response_model=List[dict])
async def get_system_configs(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get system configurations
    """
    result = await db.execute(select(SystemConfig))
    configs = result.scalars().all()
    
    return [
        {
            "id": config.id,
            "config_key": config.config_key,
            "config_value": config.config_value,
            "description": config.description
        }
        for config in configs
    ]
