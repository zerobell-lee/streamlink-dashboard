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
from app.core.service_container import get_service_container
from app.schemas.schedule import (
    RecordingScheduleCreate,
    RecordingScheduleResponse,
    RecordingScheduleUpdate,
    ScheduleStatusResponse
)

router = APIRouter()


@router.get("/status")
async def get_scheduler_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get scheduler status and information
    """
    container = get_service_container()
    scheduler_service = container.get_scheduler_service()

    return {
        "scheduler_info": scheduler_service.get_scheduler_info(),
        "active_recordings": await scheduler_service.get_active_recordings(),
        "schedule_status": await scheduler_service.get_all_schedule_status()
    }


@router.post("/start")
async def start_scheduler(
    current_user: User = Depends(get_current_user)
):
    """
    Start the scheduler
    """
    container = get_service_container()
    scheduler_service = container.get_scheduler_service()

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
    current_user: User = Depends(get_current_user)
):
    """
    Stop the scheduler
    """
    container = get_service_container()
    scheduler_service = container.get_scheduler_service()

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
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all recording schedules
    """
    container = get_service_container()

    async with container.get_uow_factory()() as uow:
        result = await uow._session.execute(select(RecordingSchedule))
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
    current_user: User = Depends(get_current_user)
):
    """
    Get specific recording schedule
    """
    container = get_service_container()

    async with container.get_uow_factory()() as uow:
        schedule = await uow.schedules.get_by_id(schedule_id)

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
    current_user: User = Depends(get_current_user)
):
    """
    Create a new recording schedule
    """
    container = get_service_container()
    scheduler_service = container.get_scheduler_service()

    # Create schedule object
    schedule = RecordingSchedule(**schedule_data.model_dump())

    success = await scheduler_service.add_schedule(schedule)

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
    current_user: User = Depends(get_current_user)
):
    """
    Update a recording schedule
    """
    container = get_service_container()

    async with container.get_uow_factory()() as uow:
        # Get existing schedule
        schedule = await uow.schedules.get_by_id(schedule_id)

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule {schedule_id} not found"
            )

        # Update fields
        for field, value in schedule_update.model_dump(exclude_unset=True).items():
            setattr(schedule, field, value)

        await uow.schedules.update(schedule)
        await uow.commit()

        # Update scheduler service
        scheduler_service = container.get_scheduler_service()
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
    current_user: User = Depends(get_current_user)
):
    """
    Delete a recording schedule
    """
    container = get_service_container()
    scheduler_service = container.get_scheduler_service()

    success = await scheduler_service.delete_schedule(schedule_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    return {"message": "Schedule deleted successfully"}


@router.get("/schedules/{schedule_id}/status", response_model=ScheduleStatusResponse)
async def get_schedule_status(
    schedule_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of a specific schedule
    """
    container = get_service_container()
    scheduler_service = container.get_scheduler_service()

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
    current_user: User = Depends(get_current_user)
):
    """
    Trigger an immediate stream check for a schedule
    """
    container = get_service_container()
    scheduler_service = container.get_scheduler_service()

    success = await scheduler_service.trigger_check_now(schedule_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger stream check"
        )

    return {"message": f"Stream check triggered for schedule {schedule_id}"}


@router.get("/active-recordings")
async def get_active_recordings(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of currently active recordings
    """
    container = get_service_container()
    scheduler_service = container.get_scheduler_service()

    active_recordings = await scheduler_service.get_active_recordings()

    return {
        "active_recordings": active_recordings,
        "count": len(active_recordings)
    }


@router.post("/stop-all-recordings")
async def stop_all_recordings(
    current_user: User = Depends(get_current_user)
):
    """
    Stop all active recordings
    """
    container = get_service_container()
    scheduler_service = container.get_scheduler_service()

    success = await scheduler_service.stop_all_recordings()

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop all recordings"
        )

    return {"message": "All recordings stopped successfully"}
