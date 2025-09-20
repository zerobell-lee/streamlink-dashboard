"""
Schedules API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database.database import get_db
from app.database.models import RecordingSchedule, User
from app.core.auth import get_current_user
from app.schemas.schedule import (
    RecordingScheduleResponse, 
    RecordingScheduleCreate, 
    RecordingScheduleUpdate
)

router = APIRouter()


@router.get("", response_model=List[RecordingScheduleResponse])
async def get_schedules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of recording schedules with rotation policies
    """
    result = await db.execute(
        select(RecordingSchedule)
        .order_by(RecordingSchedule.created_at.desc())
    )
    schedules = result.scalars().all()
    
    return schedules


@router.post("", response_model=RecordingScheduleResponse)
async def create_schedule(
    schedule_data: RecordingScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new recording schedule
    """
    # Check for duplicate schedule
    result = await db.execute(
        select(RecordingSchedule)
        .where(
            RecordingSchedule.platform == schedule_data.platform,
            RecordingSchedule.streamer_id == schedule_data.streamer_id
        )
    )
    existing_schedule = result.scalar_one_or_none()
    
    if existing_schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Schedule for {schedule_data.platform}/{schedule_data.streamer_id} already exists"
        )
    
    # Create new schedule
    schedule = RecordingSchedule(**schedule_data.model_dump())
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    
    # Add to scheduler service if it's enabled
    if schedule.enabled:
        from app.core.service_container import get_service_container
        service_container = get_service_container()
        scheduler_service = service_container.get_scheduler_service()
        if scheduler_service and scheduler_service.is_running():
            await scheduler_service._start_monitoring(schedule)
    
    
    return schedule


@router.get("/{schedule_id}", response_model=RecordingScheduleResponse)
async def get_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific schedule by ID
    """
    result = await db.execute(
        select(RecordingSchedule)
        .where(RecordingSchedule.id == schedule_id)
    )
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    return schedule


@router.put("/{schedule_id}", response_model=RecordingScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_data: RecordingScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update recording schedule
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
    
    # Update fields
    for field, value in schedule_data.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
    
    await db.commit()
    await db.refresh(schedule)
    
    # Update scheduler service
    from app.core.service_container import get_service_container
    service_container = get_service_container()
    scheduler_service = service_container.get_scheduler_service()
    if scheduler_service and scheduler_service.is_running():
        await scheduler_service._start_monitoring(schedule)
    
    
    return schedule


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete recording schedule
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
    
    # Remove from scheduler service
    from app.core.service_container import get_service_container
    service_container = get_service_container()
    scheduler_service = service_container.get_scheduler_service()
    if scheduler_service and scheduler_service.is_running():
        await scheduler_service.stop_monitoring(schedule.id)
    
    await db.delete(schedule)
    await db.commit()
    
    return {"message": "Schedule deleted successfully"}


@router.post("/{schedule_id}/toggle")
async def toggle_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle schedule enabled status
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
    
    schedule.enabled = not schedule.enabled
    await db.commit()
    await db.refresh(schedule)
    
    # Update scheduler service
    from app.core.service_container import get_service_container
    service_container = get_service_container()
    scheduler_service = service_container.get_scheduler_service()
    if scheduler_service and scheduler_service.is_running():
        if schedule.enabled:
            await scheduler_service._start_monitoring(schedule)
        else:
            await scheduler_service.stop_monitoring(schedule.id)
    
    return {
        "message": f"Schedule {'enabled' if schedule.enabled else 'disabled'}",
        "enabled": schedule.enabled
    }
