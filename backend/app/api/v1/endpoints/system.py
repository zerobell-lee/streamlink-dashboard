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
from app.core.logging import logging_config
from pydantic import BaseModel, validator

router = APIRouter()


class MonitoringIntervalRequest(BaseModel):
    interval_seconds: int

    @validator('interval_seconds')
    def validate_interval(cls, v):
        if v < 5 or v > 3600:
            raise ValueError('Monitoring interval must be between 5 and 3600 seconds')
        return v


class LoggingConfigRequest(BaseModel):
    enable_file_logging: bool = True
    enable_json_logging: bool = False
    log_level: str = "INFO"
    log_retention_days: int = 30
    categories: dict = {
        "app": True,
        "database": True,
        "api": True, 
        "scheduler": True,
        "error": True
    }

    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()

    @validator('log_retention_days')
    def validate_retention_days(cls, v):
        if v < 1 or v > 365:
            raise ValueError('Retention days must be between 1 and 365')
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


# Logging Management Endpoints
@router.get("/logging/config")
async def get_logging_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current logging configuration"""
    # Get current settings from environment/config
    current_config = {
        "enable_file_logging": settings.ENABLE_FILE_LOGGING,
        "enable_json_logging": settings.ENABLE_JSON_LOGGING, 
        "log_level": settings.LOG_LEVEL,
        "log_retention_days": settings.LOG_RETENTION_DAYS,
        "categories": {
            "app": settings.LOG_CATEGORY_APP,
            "database": settings.LOG_CATEGORY_DATABASE,
            "api": settings.LOG_CATEGORY_API,
            "scheduler": settings.LOG_CATEGORY_SCHEDULER,
            "error": settings.LOG_CATEGORY_ERROR
        }
    }
    
    return current_config


@router.post("/logging/config")
async def update_logging_config(
    request: LoggingConfigRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update logging configuration"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Store logging config in database for persistence
    config_map = {
        "log_enable_file": str(request.enable_file_logging),
        "log_enable_json": str(request.enable_json_logging),
        "log_level": request.log_level,
        "log_retention_days": str(request.log_retention_days),
        "log_category_app": str(request.categories.get("app", True)),
        "log_category_database": str(request.categories.get("database", True)),
        "log_category_api": str(request.categories.get("api", True)),
        "log_category_scheduler": str(request.categories.get("scheduler", True)),
        "log_category_error": str(request.categories.get("error", True)),
    }
    
    # Update all logging configs
    for key, value in config_map.items():
        result = await db.execute(select(SystemConfig).where(SystemConfig.config_key == key))
        config = result.scalar_one_or_none()
        
        if config:
            config.config_value = value
        else:
            config = SystemConfig(
                config_key=key,
                config_value=value,
                description=f"Logging configuration: {key}"
            )
            db.add(config)
    
    await db.commit()
    
    return {
        "message": "Logging configuration updated successfully",
        "note": "Changes will take effect on next server restart"
    }


@router.get("/logging/files")
async def get_log_files(
    current_user: User = Depends(get_current_user)
):
    """Get information about log files"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        log_files = logging_config.get_log_files()
        return {
            "log_files": log_files,
            "logs_directory": str(logging_config.logs_dir)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get log files information: {str(e)}"
        )


@router.get("/logging/files/{filename}")
async def get_log_file_content(
    filename: str,
    lines: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get log file content (tail n lines)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    log_file_path = logging_config.logs_dir / filename
    
    if not log_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log file '{filename}' not found"
        )
    
    # Security check - only allow files in logs directory
    if not str(log_file_path).startswith(str(logging_config.logs_dir)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Read last n lines
        with open(log_file_path, 'r', encoding='utf-8') as f:
            file_lines = f.readlines()
            
        # Get last n lines
        tail_lines = file_lines[-lines:] if len(file_lines) > lines else file_lines
        
        return {
            "filename": filename,
            "total_lines": len(file_lines),
            "showing_lines": len(tail_lines),
            "content": tail_lines
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read log file: {str(e)}"
        )


@router.post("/logging/cleanup")
async def cleanup_old_logs(
    max_age_days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Clean up old log files"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if max_age_days < 1 or max_age_days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="max_age_days must be between 1 and 365"
        )
    
    try:
        cleaned_files = logging_config.clean_old_logs(max_age_days)
        return {
            "message": f"Log cleanup completed",
            "cleaned_files_count": len(cleaned_files),
            "cleaned_files": cleaned_files,
            "max_age_days": max_age_days
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clean old logs: {str(e)}"
        )


