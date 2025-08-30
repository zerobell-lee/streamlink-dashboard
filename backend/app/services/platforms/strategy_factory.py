"""
Strategy factory for creating platform-specific strategies
"""
from typing import Dict, Optional
from .base_strategy import PlatformStrategy
from .twitch_strategy import TwitchStrategy
from .youtube_strategy import YouTubeStrategy
from .sooplive_strategy import SoopliveStrategy
from .chzzk_strategy import ChzzkStrategy


class PlatformStrategyFactory:
    """Factory for creating platform-specific strategies"""
    
    _strategies = {
        "twitch": TwitchStrategy,
        "youtube": YouTubeStrategy,
        "sooplive": SoopliveStrategy,
        "chzzk": ChzzkStrategy,
    }
    
    @classmethod
    def create_strategy(cls, platform: str, config: Dict) -> Optional[PlatformStrategy]:
        """
        Create a strategy instance for the given platform
        
        Args:
            platform: Platform name (e.g., 'twitch', 'youtube', 'sooplive', 'chzzk')
            config: Platform-specific configuration
            
        Returns:
            PlatformStrategy instance or None if platform not supported
        """
        strategy_class = cls._strategies.get(platform.lower())
        if strategy_class:
            return strategy_class(config)
        return None
    
    @classmethod
    def get_supported_platforms(cls) -> list[str]:
        """Get list of supported platforms"""
        return list(cls._strategies.keys())
    
    @classmethod
    def is_platform_supported(cls, platform: str) -> bool:
        """Check if a platform is supported"""
        return platform.lower() in cls._strategies
    
    @classmethod
    def register_strategy(cls, platform: str, strategy_class: type):
        """
        Register a new strategy for a platform
        
        Args:
            platform: Platform name
            strategy_class: Strategy class that inherits from PlatformStrategy
        """
        cls._strategies[platform.lower()] = strategy_class
