"""
Platforms API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict

from app.database.database import get_db
from app.database.models import PlatformConfig, User
from app.core.auth import get_current_user
from app.services.platform_service import PlatformService
from app.schemas.platform import PlatformConfigResponse, PlatformConfigUpdate


router = APIRouter()


@router.get("/", response_model=List[PlatformConfigResponse])
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
        PlatformConfigResponse(
            id=platform.id,
            platform=platform.platform,
            additional_settings=platform.additional_settings,
            enabled=platform.enabled,
            created_at=platform.created_at,
            updated_at=platform.updated_at
        )
        for platform in platforms
    ]


@router.get("/supported")
async def get_supported_platforms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of supported platforms
    """
    platform_service = PlatformService(db)
    supported = await platform_service.get_supported_platforms()
    
    return {
        "supported_platforms": supported,
        "total": len(supported)
    }


@router.get("/schema")
async def get_platform_schemas(
    current_user: User = Depends(get_current_user)
):
    """
    Get configuration schema for all supported platforms
    """
    schemas = {
        "twitch": {
            "required_fields": [
                {
                    "key": "client_id",
                    "label": "Twitch Client ID",
                    "type": "text",
                    "required": True,
                    "description": "Your Twitch application client ID",
                    "help_url": "https://dev.twitch.tv/console",
                    "placeholder": "Enter your Twitch client ID"
                },
                {
                    "key": "client_secret",
                    "label": "Twitch Client Secret",
                    "type": "password",
                    "required": True,
                    "description": "Your Twitch application client secret",
                    "help_url": "https://dev.twitch.tv/console",
                    "placeholder": "Enter your Twitch client secret"
                }
            ],
            "optional_fields": []
        },
        "youtube": {
            "required_fields": [
                {
                    "key": "api_key",
                    "label": "YouTube API Key",
                    "type": "password",
                    "required": True,
                    "description": "Your YouTube Data API key for checking stream status",
                    "help_url": "https://console.developers.google.com/",
                    "placeholder": "Enter your YouTube API key"
                }
            ],
            "optional_fields": []
        },
        "sooplive": {
            "required_fields": [
                {
                    "key": "username",
                    "label": "Sooplive Username",
                    "type": "text",
                    "required": True,
                    "description": "Your Sooplive account username for login",
                    "help_url": "https://www.sooplive.co.kr/",
                    "placeholder": "Enter your Sooplive username"
                },
                {
                    "key": "password",
                    "label": "Sooplive Password",
                    "type": "password",
                    "required": True,
                    "description": "Your Sooplive account password for login",
                    "help_url": "https://www.sooplive.co.kr/",
                    "placeholder": "Enter your Sooplive password"
                }
            ],
            "optional_fields": []
        }
    }
    
    return schemas


@router.get("/{platform_name}/config")
async def get_platform_config(
    platform_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific platform configuration
    """
    platform_service = PlatformService(db)
    config = await platform_service.get_platform_config(platform_name)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Platform '{platform_name}' not found"
        )
    
    return PlatformConfigResponse(
        id=config.id,
        platform=config.platform,
        additional_settings=config.additional_settings,
        enabled=config.enabled,
        created_at=config.created_at,
        updated_at=config.updated_at
    )


@router.put("/{platform_name}/config")
async def update_platform_config(
    platform_name: str,
    config_update: PlatformConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update platform configuration
    """
    platform_service = PlatformService(db)
    config = await platform_service.get_platform_config(platform_name)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Platform '{platform_name}' not found"
        )
    
    # Update fields
    for field, value in config_update.dict(exclude_unset=True).items():
        setattr(config, field, value)
    
    await db.commit()
    await db.refresh(config)
    
    # Invalidate strategy cache for this platform
    platform_service.invalidate_cache(platform_name)
    
    return PlatformConfigResponse(
        id=config.id,
        platform=config.platform,
        additional_settings=config.additional_settings,
        enabled=config.enabled,
        created_at=config.created_at,
        updated_at=config.updated_at
    )


@router.get("/{platform_name}/stream-info")
async def get_stream_info(
    platform_name: str,
    streamer_id: str = Query(..., description="Streamer ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get stream information for a specific platform and streamer
    """
    platform_service = PlatformService(db)
    
    # Validate platform
    if not await platform_service.get_strategy(platform_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Platform '{platform_name}' not supported or not configured"
        )
    
    # Get stream info
    stream_info = await platform_service.get_stream_info(platform_name, streamer_id)
    
    if not stream_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stream not found or not live for {streamer_id} on {platform_name}"
        )
    
    return {
        "platform": platform_name,
        "streamer_id": stream_info.streamer_id,
        "streamer_name": stream_info.streamer_name,
        "title": stream_info.title,
        "is_live": stream_info.is_live,
        "viewer_count": stream_info.viewer_count,
        "thumbnail_url": stream_info.thumbnail_url,
        "started_at": stream_info.started_at
    }


@router.get("/{platform_name}/stream-urls")
async def get_stream_urls(
    platform_name: str,
    streamer_id: str = Query(..., description="Streamer ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get available stream URLs for a specific platform and streamer
    """
    platform_service = PlatformService(db)
    
    # Validate platform
    if not await platform_service.get_strategy(platform_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Platform '{platform_name}' not supported or not configured"
        )
    
    # Get stream URLs
    stream_urls = await platform_service.get_stream_urls(platform_name, streamer_id)
    
    return {
        "platform": platform_name,
        "streamer_id": streamer_id,
        "stream_urls": [
            {
                "url": url.url,
                "quality": url.quality,
                "format": url.format,
                "bandwidth": url.bandwidth
            }
            for url in stream_urls
        ]
    }


@router.get("/{platform_name}/streamlink-args")
async def get_streamlink_args(
    platform_name: str,
    streamer_id: str = Query(..., description="Streamer ID"),
    quality: str = Query("best", description="Stream quality"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get Streamlink command arguments for a specific platform and streamer
    """
    platform_service = PlatformService(db)
    
    # Validate platform
    if not await platform_service.get_strategy(platform_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Platform '{platform_name}' not supported or not configured"
        )
    
    # Get Streamlink arguments
    args = await platform_service.get_streamlink_args(platform_name, streamer_id, quality)
    
    return {
        "platform": platform_name,
        "streamer_id": streamer_id,
        "quality": quality,
        "arguments": args,
        "command": f"streamlink {' '.join(args)}"
    }


@router.post("/initialize")
async def initialize_platforms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initialize default platform configurations
    """
    platform_service = PlatformService(db)
    await platform_service.create_default_configs()
    
    return {
        "message": "Default platform configurations created successfully",
        "supported_platforms": await platform_service.get_supported_platforms()
    }


@router.get("/sooplive/stream-status/{streamer_id}")
async def check_sooplive_stream_status(
    streamer_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if a Sooplive streamer is currently live
    """
    platform_service = PlatformService(db)
    
    # Get stream info
    stream_info = await platform_service.get_stream_info("sooplive", streamer_id)
    
    if not stream_info:
        return {
            "platform": "sooplive",
            "streamer_id": streamer_id,
            "is_live": False,
            "message": "Stream not found or not live"
        }
    
    return {
        "platform": "sooplive",
        "streamer_id": streamer_id,
        "is_live": True,
        "streamer_name": stream_info.streamer_name,
        "title": stream_info.title,
        "viewer_count": stream_info.viewer_count,
        "thumbnail_url": stream_info.thumbnail_url
    }
