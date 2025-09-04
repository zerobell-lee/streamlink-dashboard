"""
Registry-based strategy factory for creating platform-specific strategies
"""
import logging
from typing import Dict, Optional, List
from .base_strategy import PlatformStrategy
from .registry import PlatformRegistry, PlatformDefinition

# Import all platform definitions to ensure they're registered
from . import definitions

logger = logging.getLogger(__name__)


class PlatformStrategyFactory:
    """Registry-based factory for creating platform-specific strategies"""
    
    @classmethod
    def create_strategy(cls, platform: str, user_config: Dict) -> Optional[PlatformStrategy]:
        """
        Create a strategy instance for the given platform using registry definition
        
        Args:
            platform: Platform name (e.g., 'twitch', 'youtube', 'sooplive', 'chzzk')
            user_config: User-specific platform configuration
            
        Returns:
            PlatformStrategy instance or None if platform not supported
        """
        # Get platform definition from registry
        platform_definition = PlatformRegistry.get_platform(platform)
        if not platform_definition:
            logger.warning(f"Platform {platform} not found in registry")
            return None
        
        try:
            # Merge user config with platform defaults
            merged_config = platform_definition.get_merged_config(user_config)
            
            # Create strategy instance
            strategy_instance = platform_definition.strategy_class(merged_config)
            logger.info(f"Created strategy for platform: {platform}")
            return strategy_instance
            
        except Exception as e:
            logger.error(f"Failed to create strategy for platform {platform}: {e}")
            return None
    
    @classmethod
    def get_supported_platforms(cls) -> List[str]:
        """Get list of supported platforms from registry"""
        return PlatformRegistry.get_platform_names()
    
    @classmethod
    def get_platform_definitions(cls) -> List[PlatformDefinition]:
        """Get all platform definitions from registry"""
        return PlatformRegistry.get_all_platforms()
    
    @classmethod
    def get_platform_definition(cls, platform: str) -> Optional[PlatformDefinition]:
        """Get platform definition by name"""
        return PlatformRegistry.get_platform(platform)
    
    @classmethod
    def is_platform_supported(cls, platform: str) -> bool:
        """Check if a platform is supported in registry"""
        return PlatformRegistry.is_platform_supported(platform)
    
    @classmethod
    def validate_platform_config(cls, platform: str, config: Dict) -> bool:
        """
        Validate platform configuration against its schema
        
        Args:
            platform: Platform name
            config: Configuration to validate
            
        Returns:
            True if configuration is valid
        """
        platform_definition = PlatformRegistry.get_platform(platform)
        if not platform_definition:
            return False
        
        try:
            platform_definition.validate_config(config)
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed for {platform}: {e}")
            return False
    
    @classmethod
    def get_platform_config_schema(cls, platform: str) -> Optional[Dict]:
        """
        Get configuration schema for a platform
        
        Args:
            platform: Platform name
            
        Returns:
            JSON schema for platform configuration or None if not found
        """
        platform_definition = PlatformRegistry.get_platform(platform)
        return platform_definition.config_schema if platform_definition else None
