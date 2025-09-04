"""
Registry-based platform service for managing platform strategies and configurations
"""
import logging
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update

from app.database.models import PlatformUserConfig
from app.services.platforms.strategy_factory import PlatformStrategyFactory
from app.services.platforms.registry import PlatformRegistry, PlatformDefinition
from app.services.platforms.base_strategy import PlatformStrategy, StreamInfo, StreamUrl

logger = logging.getLogger(__name__)


class PlatformService:
    """Registry-based service for managing platform strategies and configurations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._strategies_cache: Dict[str, PlatformStrategy] = {}
    
    def invalidate_cache(self, platform: str = None):
        """Invalidate strategy cache for a platform or all platforms"""
        if platform:
            self._strategies_cache.pop(platform, None)
            logger.info(f"Invalidated cache for platform: {platform}")
        else:
            self._strategies_cache.clear()
            logger.info("Invalidated all platform strategy cache")
    
    async def get_platform_user_config(self, platform: str) -> Optional[PlatformUserConfig]:
        """
        Get platform user configuration from database
        
        Args:
            platform: Platform name
            
        Returns:
            PlatformUserConfig or None if not found
        """
        result = await self.db.execute(
            select(PlatformUserConfig).where(PlatformUserConfig.platform_name == platform)
        )
        return result.scalar_one_or_none()
    
    async def get_strategy(self, platform: str) -> Optional[PlatformStrategy]:
        """
        Get or create strategy for a platform using registry and user configuration
        
        Args:
            platform: Platform name
            
        Returns:
            PlatformStrategy instance or None if not supported/configured
        """
        # Check cache first
        if platform in self._strategies_cache:
            return self._strategies_cache[platform]
        
        # Get user config from database
        user_config_db = await self.get_platform_user_config(platform)
        user_config = {}
        
        if user_config_db:
            # Combine user credentials and custom settings
            user_config.update(user_config_db.user_credentials)
            user_config.update(user_config_db.custom_settings)
        
        # Create strategy using registry
        strategy = PlatformStrategyFactory.create_strategy(platform, user_config)
        
        if strategy:
            self._strategies_cache[platform] = strategy
            logger.info(f"Created and cached strategy for platform: {platform}")
        
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
    
    # --- Registry-based Platform Management ---
    
    def get_available_platforms(self) -> List[PlatformDefinition]:
        """Get all available platforms from registry"""
        return PlatformRegistry.get_all_platforms()
    
    def get_platform_definition(self, platform: str) -> Optional[PlatformDefinition]:
        """Get platform definition from registry"""
        return PlatformRegistry.get_platform(platform)
    
    def get_platform_schema(self, platform: str) -> Optional[Dict]:
        """Get configuration schema for a platform"""
        definition = PlatformRegistry.get_platform(platform)
        return definition.config_schema if definition else None
    
    def validate_platform_config(self, platform: str, config: Dict) -> bool:
        """Validate platform configuration against schema"""
        return PlatformStrategyFactory.validate_platform_config(platform, config)
    
    # --- User Configuration Management ---
    
    async def update_platform_config(self, platform: str, user_credentials: Dict = None, custom_settings: Dict = None):
        """
        Update or create platform user configuration
        
        Args:
            platform: Platform name
            user_credentials: User credentials (API keys, tokens, etc.)
            custom_settings: Custom streamlink arguments and settings
        """
        # Validate platform exists in registry
        if not PlatformRegistry.is_platform_supported(platform):
            raise ValueError(f"Platform {platform} is not supported")
        
        # Validate configuration
        combined_config = {}
        if user_credentials:
            combined_config.update(user_credentials)
        if custom_settings:
            combined_config.update(custom_settings)
        
        if combined_config and not self.validate_platform_config(platform, combined_config):
            raise ValueError(f"Invalid configuration for platform {platform}")
        
        # Get existing config or create new one
        existing = await self.get_platform_user_config(platform)
        
        if existing:
            # Update existing config
            if user_credentials is not None:
                existing.user_credentials = user_credentials
            if custom_settings is not None:
                existing.custom_settings = custom_settings
        else:
            # Create new config
            new_config = PlatformUserConfig(
                platform_name=platform,
                user_credentials=user_credentials or {},
                custom_settings=custom_settings or {}
            )
            self.db.add(new_config)
        
        await self.db.commit()
        
        # Invalidate cache for this platform
        self.invalidate_cache(platform)
        logger.info(f"Updated configuration for platform: {platform}")
    
    async def delete_platform_config(self, platform: str):
        """Delete platform user configuration"""
        await self.db.execute(
            delete(PlatformUserConfig).where(PlatformUserConfig.platform_name == platform)
        )
        await self.db.commit()
        
        # Invalidate cache for this platform
        self.invalidate_cache(platform)
        logger.info(f"Deleted configuration for platform: {platform}")
    
    async def get_configured_platforms(self) -> List[str]:
        """Get list of platforms that have user configurations"""
        result = await self.db.execute(select(PlatformUserConfig.platform_name))
        return [row[0] for row in result.fetchall()]
    
    async def get_all_platform_configs(self) -> List[PlatformUserConfig]:
        """Get all platform user configurations"""
        result = await self.db.execute(select(PlatformUserConfig))
        return result.scalars().all()
    
    async def close(self):
        """Close all strategy sessions"""
        for strategy in self._strategies_cache.values():
            if hasattr(strategy, 'close'):
                await strategy.close()
        self._strategies_cache.clear()
        logger.info("Closed all platform strategy sessions")
