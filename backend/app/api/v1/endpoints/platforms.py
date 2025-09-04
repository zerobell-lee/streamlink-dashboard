"""
Registry-based Platforms API endpoints
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from app.database.database import get_db
from app.database.models import PlatformUserConfig, User
from app.core.auth import get_current_user
from app.services.platform_service import PlatformService
from app.schemas.platform import (
    PlatformDefinitionResponse, PlatformDefinitionListResponse,
    PlatformUserConfigCreate, PlatformUserConfigUpdate, PlatformUserConfigResponse,
    PlatformInfoResponse, PlatformListResponse, PlatformSchemaResponse,
    StreamInfoResponse, StreamUrlResponse, StreamUrlsResponse, StreamlinkArgsResponse,
    SupportedPlatformsResponse
)


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=PlatformListResponse)
async def get_platforms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive list of all platforms with their definitions and user configurations
    """
    platform_service = PlatformService(db)
    
    try:
        # Get all platform definitions from registry
        definitions = platform_service.get_available_platforms()
        
        # Get all user configurations
        user_configs_db = await platform_service.get_all_platform_configs()
        user_configs_map = {config.platform_name: config for config in user_configs_db}
        
        platforms = []
        for definition in definitions:
            user_config = user_configs_map.get(definition.name)
            
            platforms.append(PlatformInfoResponse(
                definition=PlatformDefinitionResponse(
                    name=definition.name,
                    display_name=definition.display_name,
                    description=definition.description,
                    requires_auth=definition.requires_auth,
                    supports_chat=definition.supports_chat,
                    supports_vod=definition.supports_vod,
                    help_text=definition.help_text,
                    setup_instructions=definition.setup_instructions,
                    config_schema=definition.config_schema,
                    supported_qualities=definition.supported_qualities,
                    default_streamlink_args=definition.default_streamlink_args
                ),
                user_config=PlatformUserConfigResponse(
                    platform_name=user_config.platform_name,
                    user_credentials=user_config.user_credentials,
                    custom_settings=user_config.custom_settings,
                    created_at=user_config.created_at,
                    updated_at=user_config.updated_at
                ) if user_config else None,
                is_configured=user_config is not None
            ))
        
        return PlatformListResponse(
            platforms=platforms,
            total=len(platforms)
        )
        
    finally:
        await platform_service.close()


@router.get("/available", response_model=PlatformDefinitionListResponse)
async def get_available_platforms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all available platform definitions from registry
    """
    platform_service = PlatformService(db)
    
    try:
        definitions = platform_service.get_available_platforms()
        
        platforms = [
            PlatformDefinitionResponse(
                name=definition.name,
                display_name=definition.display_name,
                description=definition.description,
                requires_auth=definition.requires_auth,
                supports_chat=definition.supports_chat,
                supports_vod=definition.supports_vod,
                help_text=definition.help_text,
                setup_instructions=definition.setup_instructions,
                config_schema=definition.config_schema,
                supported_qualities=definition.supported_qualities,
                default_streamlink_args=definition.default_streamlink_args
            )
            for definition in definitions
        ]
        
        return PlatformDefinitionListResponse(
            platforms=platforms,
            total=len(platforms)
        )
        
    finally:
        await platform_service.close()


@router.get("/{platform_name}/schema", response_model=PlatformSchemaResponse)
async def get_platform_schema(
    platform_name: str = Path(..., description="Platform name"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get configuration schema for a specific platform
    """
    platform_service = PlatformService(db)
    
    try:
        schema = platform_service.get_platform_schema(platform_name)
        if not schema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform {platform_name} not found"
            )
        
        return PlatformSchemaResponse(
            platform_name=platform_name,
            schema=schema
        )
        
    finally:
        await platform_service.close()


@router.get("/{platform_name}", response_model=PlatformInfoResponse)
async def get_platform(
    platform_name: str = Path(..., description="Platform name"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific platform information with definition and user configuration
    """
    platform_service = PlatformService(db)
    
    try:
        # Get platform definition
        definition = platform_service.get_platform_definition(platform_name)
        if not definition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform {platform_name} not found"
            )
        
        # Get user configuration
        user_config = await platform_service.get_platform_user_config(platform_name)
        
        return PlatformInfoResponse(
            definition=PlatformDefinitionResponse(
                name=definition.name,
                display_name=definition.display_name,
                description=definition.description,
                requires_auth=definition.requires_auth,
                supports_chat=definition.supports_chat,
                supports_vod=definition.supports_vod,
                help_text=definition.help_text,
                setup_instructions=definition.setup_instructions,
                config_schema=definition.config_schema,
                supported_qualities=definition.supported_qualities,
                default_streamlink_args=definition.default_streamlink_args
            ),
            user_config=PlatformUserConfigResponse(
                platform_name=user_config.platform_name,
                user_credentials=user_config.user_credentials,
                custom_settings=user_config.custom_settings,
                created_at=user_config.created_at,
                updated_at=user_config.updated_at
            ) if user_config else None,
            is_configured=user_config is not None
        )
        
    finally:
        await platform_service.close()


@router.post("/{platform_name}/config", response_model=PlatformUserConfigResponse)
async def create_or_update_platform_config(
    platform_name: str = Path(..., description="Platform name"),
    config_data: PlatformUserConfigCreate = ...,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create or update platform user configuration
    """
    platform_service = PlatformService(db)
    
    try:
        await platform_service.update_platform_config(
            platform=platform_name,
            user_credentials=config_data.user_credentials,
            custom_settings=config_data.custom_settings
        )
        
        # Return updated configuration
        user_config = await platform_service.get_platform_user_config(platform_name)
        if not user_config:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create platform configuration"
            )
        
        return PlatformUserConfigResponse(
            platform_name=user_config.platform_name,
            user_credentials=user_config.user_credentials,
            custom_settings=user_config.custom_settings,
            created_at=user_config.created_at,
            updated_at=user_config.updated_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    finally:
        await platform_service.close()


@router.put("/{platform_name}/config", response_model=PlatformUserConfigResponse)
async def update_platform_config(
    platform_name: str = Path(..., description="Platform name"),
    config_data: PlatformUserConfigUpdate = ...,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update existing platform user configuration
    """
    platform_service = PlatformService(db)
    
    try:
        # Check if configuration exists
        existing_config = await platform_service.get_platform_user_config(platform_name)
        if not existing_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform configuration for {platform_name} not found"
            )
        
        await platform_service.update_platform_config(
            platform=platform_name,
            user_credentials=config_data.user_credentials,
            custom_settings=config_data.custom_settings
        )
        
        # Return updated configuration
        user_config = await platform_service.get_platform_user_config(platform_name)
        
        return PlatformUserConfigResponse(
            platform_name=user_config.platform_name,
            user_credentials=user_config.user_credentials,
            custom_settings=user_config.custom_settings,
            created_at=user_config.created_at,
            updated_at=user_config.updated_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    finally:
        await platform_service.close()


@router.delete("/{platform_name}/config")
async def delete_platform_config(
    platform_name: str = Path(..., description="Platform name"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete platform user configuration
    """
    platform_service = PlatformService(db)
    
    try:
        # Check if configuration exists
        existing_config = await platform_service.get_platform_user_config(platform_name)
        if not existing_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform configuration for {platform_name} not found"
            )
        
        await platform_service.delete_platform_config(platform_name)
        
        return {"message": f"Platform configuration for {platform_name} deleted successfully"}
        
    finally:
        await platform_service.close()


@router.get("/{platform_name}/stream-info", response_model=StreamInfoResponse)
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
    
    try:
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
        
        return StreamInfoResponse(
            platform=platform_name,
            streamer_id=stream_info.streamer_id,
            streamer_name=stream_info.streamer_name,
            title=stream_info.title,
            is_live=stream_info.is_live,
            viewer_count=stream_info.viewer_count,
            thumbnail_url=stream_info.thumbnail_url,
            started_at=stream_info.started_at
        )
    
    finally:
        await platform_service.close()


@router.get("/{platform_name}/stream-urls", response_model=StreamUrlsResponse)
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
    
    try:
        # Validate platform
        if not await platform_service.get_strategy(platform_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform '{platform_name}' not supported or not configured"
            )
        
        # Get stream URLs
        stream_urls = await platform_service.get_stream_urls(platform_name, streamer_id)
        
        return StreamUrlsResponse(
            platform=platform_name,
            streamer_id=streamer_id,
            stream_urls=[
                StreamUrlResponse(
                    url=url.url,
                    quality=url.quality,
                    format=url.format,
                    bandwidth=url.bandwidth
                )
                for url in stream_urls
            ]
        )
    
    finally:
        await platform_service.close()


@router.get("/{platform_name}/streamlink-args", response_model=StreamlinkArgsResponse)
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
    
    try:
        # Validate platform
        if not await platform_service.get_strategy(platform_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform '{platform_name}' not supported or not configured"
            )
        
        # Get Streamlink arguments
        args = await platform_service.get_streamlink_args(platform_name, streamer_id, quality)
        
        return StreamlinkArgsResponse(
            platform=platform_name,
            streamer_id=streamer_id,
            quality=quality,
            arguments=args,
            command=f"streamlink {' '.join(args)}"
        )
    
    finally:
        await platform_service.close()


@router.get("/supported", response_model=SupportedPlatformsResponse)
async def get_supported_platforms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of supported platforms from registry
    """
    platform_service = PlatformService(db)
    
    try:
        configured_platforms = await platform_service.get_configured_platforms()
        supported_platforms = [definition.name for definition in platform_service.get_available_platforms()]
        
        return SupportedPlatformsResponse(
            supported_platforms=supported_platforms,
            total=len(supported_platforms)
        )
    finally:
        await platform_service.close()
