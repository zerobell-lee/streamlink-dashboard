"""
Recordings API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
import os

from app.database.database import get_db
from app.database.models import Recording, User
from app.core.auth import get_current_user
from app.core.config import settings
from app.schemas.recording import RecordingResponse, RecordingCreate, RecordingUpdate

router = APIRouter()


@router.get("/", response_model=List[RecordingResponse])
async def get_recordings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    platform: Optional[str] = None,
    streamer_id: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of recordings with optional filters
    """
    query = select(Recording)
    
    # Apply filters
    filters = []
    if platform:
        filters.append(Recording.platform == platform)
    if streamer_id:
        filters.append(Recording.streamer_id == streamer_id)
    if is_favorite is not None:
        filters.append(Recording.is_favorite == is_favorite)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(Recording.created_at.desc())
    
    result = await db.execute(query)
    recordings = result.scalars().all()
    
    return recordings


@router.get("/{recording_id}", response_model=RecordingResponse)
async def get_recording(
    recording_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific recording by ID
    """
    result = await db.execute(
        select(Recording).where(Recording.id == recording_id)
    )
    recording = result.scalar_one_or_none()
    
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    return recording


@router.put("/{recording_id}/favorite")
async def toggle_favorite(
    recording_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle favorite status of a recording
    """
    result = await db.execute(
        select(Recording).where(Recording.id == recording_id)
    )
    recording = result.scalar_one_or_none()
    
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    recording.is_favorite = not recording.is_favorite
    await db.commit()
    await db.refresh(recording)
    
    return {"message": f"Recording {'marked as favorite' if recording.is_favorite else 'unmarked from favorite'}"}


@router.delete("/{recording_id}")
async def delete_recording(
    recording_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a recording (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    result = await db.execute(
        select(Recording).where(Recording.id == recording_id)
    )
    recording = result.scalar_one_or_none()
    
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    # Delete file if exists
    if os.path.exists(recording.file_path):
        try:
            os.remove(recording.file_path)
        except OSError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )
    
    await db.delete(recording)
    await db.commit()
    
    return {"message": "Recording deleted successfully"}
