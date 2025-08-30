"""
Platform service for managing platform strategies and configurations
"""
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import PlatformConfig
from app.services.platforms.strategy_factory import PlatformStrategyFactory
from app.services.platforms.base_strategy import StreamInfo, StreamUrl


class PlatformService:
    """Service for managing platform strategies and configurations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._strategies_cache: Dict[str, any] = {}
    
    def invalidate_cache(self, platform: str = None):
        """Invalidate strategy cache for a platform or all platforms"""
        if platform:
            self._strategies_cache.pop(platform, None)
        else:
            self._strategies_cache.clear()
    
    async def get_platform_config(self, platform: str) -> Optional[PlatformConfig]:
        """
        Get platform configuration from database
        
        Args:
            platform: Platform name
            
        Returns:
            PlatformConfig or None if not found
        """
        result = await self.db.execute(
            select(PlatformConfig).where(PlatformConfig.platform == platform)
        )
        return result.scalar_one_or_none()
    
    async def get_strategy(self, platform: str):
        """
        Get or create strategy for a platform
        
        Args:
            platform: Platform name
            
        Returns:
            PlatformStrategy instance or None if not supported
        """
        # Check cache first
        if platform in self._strategies_cache:
            return self._strategies_cache[platform]
        
        # Get config from database
        config = await self.get_platform_config(platform)
        if not config:
            return None
        
        # Create strategy
        strategy = PlatformStrategyFactory.create_strategy(platform, {
            "additional_settings": config.additional_settings,
            "enabled": config.enabled,
            # Platform-specific settings
            "client_id": config.additional_settings.get("client_id", ""),
            "client_secret": config.additional_settings.get("client_secret", ""),
            "api_key": config.additional_settings.get("api_key", ""),
            "api_token": config.additional_settings.get("api_token", ""),  # Add Twitch API token support
        })
        
        if strategy:
            self._strategies_cache[platform] = strategy
        
        return strategy
    
    async def get_stream_info(self, platform: str, streamer_id: str) -> Optional[StreamInfo]:
        """
        Get stream information for a platform and streamer
        
        Args:
            platform: Platform name
            streamer_id: Streamer identifier
            
        Returns:
            StreamInfo or None if not found/error
        """
        strategy = await self.get_strategy(platform)
        if not strategy:
            return None
        
        return await strategy.get_stream_info(streamer_id)
    
    async def get_stream_urls(self, platform: str, streamer_id: str) -> List[StreamUrl]:
        """
        Get available stream URLs for a platform and streamer
        
        Args:
            platform: Platform name
            streamer_id: Streamer identifier
            
        Returns:
            List of StreamUrl objects
        """
        strategy = await self.get_strategy(platform)
        if not strategy:
            return []
        
        return await strategy.get_stream_urls(streamer_id)
    
    async def get_streamlink_args(self, platform: str, streamer_id: str, quality: str = "best") -> List[str]:
        """
        Get Streamlink command arguments for a platform and streamer
        
        Args:
            platform: Platform name
            streamer_id: Streamer identifier
            quality: Desired quality
            
        Returns:
            List of command line arguments
        """
        strategy = await self.get_strategy(platform)
        if not strategy:
            return []
        
        return strategy.get_streamlink_args(streamer_id, quality)
    
    async def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return PlatformStrategyFactory.get_supported_platforms()
    
    async def get_enabled_platforms(self) -> List[PlatformConfig]:
        """
        Get list of enabled platform configurations
        
        Returns:
            List of enabled PlatformConfig objects
        """
        result = await self.db.execute(
            select(PlatformConfig).where(PlatformConfig.enabled == True)
        )
        return result.scalars().all()
    
    async def create_default_configs(self):
        """Create default platform configurations if they don't exist"""
        default_configs = [
            {
                "platform": "twitch",
                "additional_settings": {
                    "client_id": "",
                    "client_secret": "",
                    "api_token": "",  # User-provided Twitch API token
                    "--twitch-disable-ads": True,
                    "--twitch-disable-hosting": True,
                },
                "enabled": True
            },
            {
                "platform": "youtube",
                "additional_settings": {
                    "api_key": "",
                    "--youtube-live-chunk-size": "4",
                    "--youtube-live-from-start": True,
                },
                "enabled": True
            },
            {
                "platform": "sooplive",
                "additional_settings": {
                    "username": "",
                    "password": "",
                },
                "enabled": True
            },
            {
                "platform": "chzzk",
                "additional_settings": {
                    # Chzzk doesn't require authentication for basic stream checking
                    # Additional Streamlink arguments can be added here if needed
                },
                "enabled": True
            }
        ]
        
        for config_data in default_configs:
            existing = await self.get_platform_config(config_data["platform"])
            if not existing:
                config = PlatformConfig(**config_data)
                self.db.add(config)
        
        await self.db.commit()
    
    async def close(self):
        """Close all strategy sessions"""
        for strategy in self._strategies_cache.values():
            if hasattr(strategy, 'close'):
                await strategy.close()
        self._strategies_cache.clear()
