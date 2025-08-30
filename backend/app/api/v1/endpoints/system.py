"""
System API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import psutil
import os
from datetime import datetime
import time

from app.database.database import get_db
from app.database.models import SystemConfig, User
from app.core.auth import get_current_user
from app.core.config import settings
from pydantic import BaseModel, validator

router = APIRouter()


class MonitoringIntervalRequest(BaseModel):
    interval_seconds: int

    @validator('interval_seconds')
    def validate_interval(cls, v):
        if v < 5 or v > 3600:
            raise ValueError('Monitoring interval must be between 5 and 3600 seconds')
        return v


@router.get("/time")
async def get_server_time():
    """
    Get server current time and timezone information
    """
    now = datetime.now()
    
    return {
        "current_time": now.isoformat(),
        "timestamp": now.timestamp(),
        "timezone_offset": time.timezone,
        "timezone_name": time.tzname[0] if not time.daylight else time.tzname[1]
    }


@router.get("/status")
async def get_system_status(
    current_user: User = Depends(get_current_user)
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


@router.get("/config")
async def get_system_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get system configuration"""
    result = await db.execute(select(SystemConfig))
    configs = result.scalars().all()
    
    config_dict = {}
    for config in configs:
        config_dict[config.config_key] = {
            'value': config.config_value,
            'description': config.description
        }
    
    return config_dict


@router.post("/config/{key}")
async def set_system_config(
    key: str,
    value: str,
    description: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Set system configuration"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if config exists
    result = await db.execute(select(SystemConfig).where(SystemConfig.config_key == key))
    config = result.scalar_one_or_none()
    
    if config:
        config.config_value = value
        if description:
            config.description = description
    else:
        config = SystemConfig(
            config_key=key,
            config_value=value,
            description=description
        )
        db.add(config)
    
    await db.commit()
    await db.refresh(config)
    
    return {"message": "Configuration updated", "key": key, "value": value}


@router.post("/rotation/apply")
async def trigger_rotation_cleanup(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger immediate rotation cleanup
    """
    from app.services.scheduler_service import SchedulerService
    
    scheduler_service = SchedulerService(db)
    
    try:
        await scheduler_service.run_rotation_cleanup()
        return {"message": "Rotation cleanup completed successfully"}
    except Exception as e:
        logger.error(f"Error running rotation cleanup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run rotation cleanup: {str(e)}"
        )


@router.get("/monitoring-interval")
async def get_monitoring_interval(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current monitoring interval setting"""
    result = await db.execute(
        select(SystemConfig).where(SystemConfig.config_key == "monitoring_interval")
    )
    config = result.scalar_one_or_none()
    
    if config:
        return {
            "interval_seconds": int(config.config_value),
            "description": config.description
        }
    else:
        # Return default value if not set
        return {
            "interval_seconds": 60,
            "description": "Default monitoring interval"
        }


@router.post("/monitoring-interval")
async def set_monitoring_interval(
    request: MonitoringIntervalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Set monitoring interval for stream checking"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if config exists
    result = await db.execute(
        select(SystemConfig).where(SystemConfig.config_key == "monitoring_interval")
    )
    config = result.scalar_one_or_none()
    
    if config:
        config.config_value = str(request.interval_seconds)
        config.description = f"Stream monitoring interval in seconds (set to {request.interval_seconds}s)"
    else:
        config = SystemConfig(
            config_key="monitoring_interval",
            config_value=str(request.interval_seconds),
            description=f"Stream monitoring interval in seconds (set to {request.interval_seconds}s)"
        )
        db.add(config)
    
    await db.commit()
    await db.refresh(config)
    
    # TODO: Update scheduler service with new interval
    # This would require restarting or reconfiguring the scheduler
    
    return {
        "message": "Monitoring interval updated successfully",
        "interval_seconds": request.interval_seconds,
        "note": "Changes will take effect on next scheduler restart"
    }


