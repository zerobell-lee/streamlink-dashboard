"""
Base strategy interface for platform-specific stream URL acquisition
"""
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class StreamInfo:
    """Stream information data class"""
    streamer_id: str
    streamer_name: str
    title: str
    is_live: bool
    viewer_count: Optional[int] = None
    thumbnail_url: Optional[str] = None
    started_at: Optional[str] = None


@dataclass
class StreamUrl:
    """Stream URL information"""
    url: str
    quality: str
    format: str
    bandwidth: Optional[int] = None


class PlatformStrategy(ABC):
    """Abstract base class for platform-specific strategies"""
    
    def __init__(self, config: Dict):
        """
        Initialize strategy with platform configuration
        
        Args:
            config: Platform-specific configuration dictionary
        """
        self.config = config
        self.platform_name = self.get_platform_name()
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return platform name (e.g., 'twitch', 'youtube')"""
        pass
    
    @abstractmethod
    def get_stream_info(self, streamer_id: str) -> Optional[StreamInfo]:
        """
        Get stream information for a given streamer
        
        Args:
            streamer_id: Platform-specific streamer identifier
            
        Returns:
            StreamInfo object if stream is live, None otherwise
        """
        pass
    
    @abstractmethod
    def get_stream_urls(self, streamer_id: str) -> List[StreamUrl]:
        """
        Get available stream URLs for a given streamer
        
        Args:
            streamer_id: Platform-specific streamer identifier
            
        Returns:
            List of StreamUrl objects with different qualities
        """
        pass
    
    
    def get_streamlink_args(self, streamer_id: str, quality: str = "best") -> List[str]:
        """
        Get Streamlink command arguments for this platform
        
        Args:
            streamer_id: Platform-specific streamer identifier
            quality: Desired stream quality
            
        Returns:
            List of command line arguments for Streamlink
        """
        base_args = self._get_base_streamlink_args()
        platform_args = self._get_platform_specific_args(streamer_id, quality)
        return base_args + platform_args
    
    def _get_base_streamlink_args(self) -> List[str]:
        """Get base Streamlink arguments common to all platforms"""
        args = [
        ]
        
        # Add custom arguments from config
        if "additional_settings" in self.config:
            custom_args = self.config["additional_settings"]
            if isinstance(custom_args, dict):
                for key, value in custom_args.items():
                    if key.startswith("--"):
                        args.append(key)
                        # Only append value if it's not a boolean True (flag-only arguments)
                        if value is not None and value != "" and value is not True:
                            args.append(str(value))
        
        return args
    
    @abstractmethod
    def _get_platform_specific_args(self, streamer_id: str, quality: str) -> List[str]:
        """
        Get platform-specific Streamlink arguments
        
        Args:
            streamer_id: Platform-specific streamer identifier
            quality: Desired stream quality
            
        Returns:
            List of platform-specific command line arguments
        """
        pass
    
    
    def is_enabled(self) -> bool:
        """Check if this platform is enabled"""
        return self.config.get("enabled", True)
