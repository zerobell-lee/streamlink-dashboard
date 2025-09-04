"""
Scheduler API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict
from datetime import datetime

from app.database.database import get_db
from app.database.models import RecordingSchedule, User
from app.core.auth import get_current_user
from app.services.scheduler_service import SchedulerService
from app.schemas.schedule import (
    RecordingScheduleCreate, 
    RecordingScheduleResponse, 
    RecordingScheduleUpdate,
    ScheduleStatusResponse
)

router = APIRouter()


@router.get("/status")
async def get_scheduler_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get scheduler status and information
    """
    scheduler_service = SchedulerService(db)
    
    return {
        "scheduler_info": scheduler_service.get_scheduler_info(),
        "active_recordings": await scheduler_service.get_active_recordings(),
        "schedule_status": await scheduler_service.get_all_schedule_status()
    }


@router.post("/start")
async def start_scheduler(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Start the scheduler
    """
    scheduler_service = SchedulerService(db)
    
    if scheduler_service.is_running():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scheduler is already running"
        )
    
    await scheduler_service.start()
    
    return {
        "message": "Scheduler started successfully",
        "scheduler_info": scheduler_service.get_scheduler_info()
    }


@router.post("/stop")
async def stop_scheduler(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Stop the scheduler
    """
    scheduler_service = SchedulerService(db)
    
    if not scheduler_service.is_running():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scheduler is not running"
        )
    
    await scheduler_service.stop()
    
    return {
        "message": "Scheduler stopped successfully",
        "scheduler_info": scheduler_service.get_scheduler_info()
    }


@router.get("/schedules", response_model=List[RecordingScheduleResponse])
async def get_schedules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all recording schedules
    """
    result = await db.execute(select(RecordingSchedule))
    schedules = result.scalars().all()
    
    return [
        RecordingScheduleResponse(
            id=schedule.id,
            platform=schedule.platform,
            streamer_id=schedule.streamer_id,
            streamer_name=schedule.streamer_name,
            quality=schedule.quality,
            custom_arguments=schedule.custom_arguments,
            enabled=schedule.enabled,
            output_format=schedule.output_format,
            filename_template=schedule.filename_template,
            rotation_enabled=schedule.rotation_enabled,
            rotation_type=schedule.rotation_type,
            max_age_days=schedule.max_age_days,
            max_count=schedule.max_count,
            max_size_gb=schedule.max_size_gb,
            protect_favorites=schedule.protect_favorites,
            delete_empty_files=schedule.delete_empty_files,
            created_at=schedule.created_at,
            updated_at=schedule.updated_at
        )
        for schedule in schedules
    ]


@router.get("/schedules/{schedule_id}", response_model=RecordingScheduleResponse)
async def get_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific recording schedule
    """
    result = await db.execute(
        select(RecordingSchedule).where(RecordingSchedule.id == schedule_id)
    )
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule {schedule_id} not found"
        )
    
    return RecordingScheduleResponse(
        id=schedule.id,
        platform=schedule.platform,
        streamer_id=schedule.streamer_id,
        streamer_name=schedule.streamer_name,
        quality=schedule.quality,
        custom_arguments=schedule.custom_arguments,
        enabled=schedule.enabled,
        output_format=schedule.output_format,
        filename_template=schedule.filename_template,
        rotation_enabled=schedule.rotation_enabled,
        rotation_type=schedule.rotation_type,
        max_age_days=schedule.max_age_days,
        max_count=schedule.max_count,
        max_size_gb=schedule.max_size_gb,
        protect_favorites=schedule.protect_favorites,
        delete_empty_files=schedule.delete_empty_files,
        created_at=schedule.created_at,
        updated_at=schedule.updated_at
    )


@router.post("/schedules", response_model=RecordingScheduleResponse)
async def create_schedule(
    schedule_data: RecordingScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new recording schedule
    """
    # Create schedule object
    schedule = RecordingSchedule(**schedule_data.model_dump())
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    
    # Add to global scheduler service if enabled
    if schedule.enabled:
        from app.main import scheduler_service
        if scheduler_service:
            await scheduler_service._start_monitoring(schedule)
    
    success = True
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create schedule"
        )
    
    return RecordingScheduleResponse(
        id=schedule.id,
        platform=schedule.platform,
        streamer_id=schedule.streamer_id,
        streamer_name=schedule.streamer_name,
        quality=schedule.quality,
        custom_arguments=schedule.custom_arguments,
        enabled=schedule.enabled,
        output_format=schedule.output_format,
        filename_template=schedule.filename_template,
        rotation_enabled=schedule.rotation_enabled,
        rotation_type=schedule.rotation_type,
        max_age_days=schedule.max_age_days,
        max_count=schedule.max_count,
        max_size_gb=schedule.max_size_gb,
        protect_favorites=schedule.protect_favorites,
        delete_empty_files=schedule.delete_empty_files,
        created_at=schedule.created_at,
        updated_at=schedule.updated_at
    )


@router.put("/schedules/{schedule_id}", response_model=RecordingScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_update: RecordingScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a recording schedule
    """
    # Get existing schedule
    result = await db.execute(
        select(RecordingSchedule).where(RecordingSchedule.id == schedule_id)
    )
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule {schedule_id} not found"
        )
    
    # Update fields
    for field, value in schedule_update.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
    
    await db.commit()
    await db.refresh(schedule)
    
    # Update scheduler service
    from app.main import scheduler_service
    if scheduler_service:
        await scheduler_service._start_monitoring(schedule)
    
    success = True
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update schedule"
        )
    
    return RecordingScheduleResponse(
        id=schedule.id,
        platform=schedule.platform,
        streamer_id=schedule.streamer_id,
        streamer_name=schedule.streamer_name,
        quality=schedule.quality,
        custom_arguments=schedule.custom_arguments,
        enabled=schedule.enabled,
        output_format=schedule.output_format,
        filename_template=schedule.filename_template,
        rotation_enabled=schedule.rotation_enabled,
        rotation_type=schedule.rotation_type,
        max_age_days=schedule.max_age_days,
        max_count=schedule.max_count,
        max_size_gb=schedule.max_size_gb,
        protect_favorites=schedule.protect_favorites,
        delete_empty_files=schedule.delete_empty_files,
        created_at=schedule.created_at,
        updated_at=schedule.updated_at
    )


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a recording schedule
    """
    result = await db.execute(
        select(RecordingSchedule).where(RecordingSchedule.id == schedule_id)
    )
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # Remove from scheduler service first
    from app.main import scheduler_service
    if scheduler_service:
        await scheduler_service.stop_monitoring(schedule.id)
    
    # Delete from database
    await db.delete(schedule)
    await db.commit()
    
    return {"message": "Schedule deleted successfully"}


@router.get("/schedules/{schedule_id}/status", response_model=ScheduleStatusResponse)
async def get_schedule_status(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get status of a specific schedule
    """
    scheduler_service = SchedulerService(db)
    
    status_info = await scheduler_service.get_schedule_status(schedule_id)
    
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule {schedule_id} not found or not active"
        )
    
    return ScheduleStatusResponse(**status_info)


@router.post("/schedules/{schedule_id}/trigger")
async def trigger_schedule_now(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger an immediate stream check for a schedule
    """
    scheduler_service = SchedulerService(db)
    
    success = await scheduler_service.trigger_check_now(schedule_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger stream check"
        )
    
    return {"message": f"Stream check triggered for schedule {schedule_id}"}


@router.get("/active-recordings")
async def get_active_recordings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of currently active recordings
    """
    scheduler_service = SchedulerService(db)
    
    active_recordings = await scheduler_service.get_active_recordings()
    
    return {
        "active_recordings": active_recordings,
        "count": len(active_recordings)
    }


@router.post("/stop-all-recordings")
async def stop_all_recordings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Stop all active recordings
    """
    scheduler_service = SchedulerService(db)
    
    success = await scheduler_service.stop_all_recordings()
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop all recordings"
        )
    
    return {"message": "All recordings stopped successfully"}
