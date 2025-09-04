"""
Platform Registry system for managing platform definitions and configurations
"""
import logging
from abc import ABC
from typing import Dict, List, Optional, Type, Any
from dataclasses import dataclass, field
from jsonschema import validate, ValidationError

from .base_strategy import PlatformStrategy

logger = logging.getLogger(__name__)


@dataclass
class PlatformDefinition(ABC):
    """
    Platform definition containing all metadata and configuration schema
    This is code-managed data that defines what a platform is and how to configure it
    """
    # Basic platform information
    name: str                           # Internal platform identifier (e.g., "twitch")
    display_name: str                   # Human-readable name (e.g., "Twitch")
    description: str                    # Platform description
    
    # Technical configuration
    strategy_class: Type[PlatformStrategy]  # Strategy class for this platform
    config_schema: Dict[str, Any]       # JSON Schema for user configuration validation
    
    # Default streaming configuration
    default_streamlink_args: List[str] = field(default_factory=list)  # Default streamlink arguments
    supported_qualities: List[str] = field(default_factory=lambda: ["best", "worst"])  # Available quality options
    
    # Output file configuration
    default_output_format: str = "mp4"  # Default container format (mp4, ts, mkv, etc.)
    supported_output_formats: List[str] = field(default_factory=lambda: ["mp4", "ts", "mkv"])  # Available formats
    default_filename_template: str = "{streamer_id}_{yyyyMMdd}_{HHmmss}"  # Default filename template
    
    # Authentication and features
    requires_auth: bool = False         # Whether this platform requires authentication
    supports_chat: bool = False         # Whether chat recording is supported
    supports_vod: bool = False          # Whether VOD recording is supported
    
    # UI and help
    help_text: str = ""                 # Platform-specific help text for users
    setup_instructions: str = ""        # Setup instructions for this platform
    
    # Rate limiting and performance
    api_rate_limit: Optional[int] = None  # API calls per minute limit
    concurrent_streams_limit: Optional[int] = None  # Max concurrent streams
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user configuration against the platform's schema
        
        Args:
            config: User configuration to validate
            
        Returns:
            Validated configuration
            
        Raises:
            ValidationError: If configuration is invalid
        """
        try:
            validate(instance=config, schema=self.config_schema)
            return config
        except ValidationError as e:
            logger.error(f"Configuration validation failed for {self.name}: {e.message}")
            raise
    
    def get_merged_config(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge platform defaults with user configuration
        
        Args:
            user_config: User-specific configuration
            
        Returns:
            Merged configuration with defaults applied
        """
        # Validate user config first
        validated_config = self.validate_config(user_config)
        
        # Merge with platform defaults
        merged = {
            "platform": self.name,
            "display_name": self.display_name,
            "default_streamlink_args": self.default_streamlink_args,
            "supported_qualities": self.supported_qualities,
            **validated_config  # User config overrides defaults
        }
        
        return merged


class PlatformRegistry:
    """
    Registry for managing platform definitions with decorator-based registration
    """
    _platforms: Dict[str, PlatformDefinition] = {}
    
    @classmethod
    def register(cls, definition: PlatformDefinition):
        """
        Decorator to register a platform definition
        
        Args:
            definition: Platform definition instance
            
        Returns:
            The original definition (for decorator pattern)
        """
        def wrapper(definition_instance):
            cls._platforms[definition.name] = definition
            logger.info(f"Registered platform: {definition.name} ({definition.display_name})")
            return definition_instance
        
        # If used as @PlatformRegistry.register without parentheses
        if isinstance(definition, PlatformDefinition):
            cls._platforms[definition.name] = definition
            logger.info(f"Registered platform: {definition.name} ({definition.display_name})")
            return definition
        
        # If used as @PlatformRegistry.register()
        return wrapper
    
    @classmethod
    def get_all_platforms(cls) -> List[PlatformDefinition]:
        """Get list of all registered platform definitions"""
        return list(cls._platforms.values())
    
    @classmethod
    def get_platform(cls, name: str) -> Optional[PlatformDefinition]:
        """Get a platform definition by name"""
        return cls._platforms.get(name.lower())
    
    @classmethod
    def get_platform_names(cls) -> List[str]:
        """Get list of all registered platform names"""
        return list(cls._platforms.keys())
    
    @classmethod
    def is_platform_supported(cls, name: str) -> bool:
        """Check if a platform is supported"""
        return name.lower() in cls._platforms
    
    @classmethod
    def get_enabled_platforms(cls, user_configs: Dict[str, Dict]) -> List[PlatformDefinition]:
        """
        Get platforms that are enabled based on user configurations
        
        Args:
            user_configs: Dictionary mapping platform names to user configurations
            
        Returns:
            List of enabled platform definitions
        """
        enabled = []
        for name, definition in cls._platforms.items():
            user_config = user_configs.get(name, {})
            if user_config.get("enabled", False):
                enabled.append(definition)
        return enabled
    
    @classmethod
    def validate_all_schemas(cls) -> bool:
        """
        Validate all platform schemas for correctness
        Used for testing and development
        
        Returns:
            True if all schemas are valid
        """
        try:
            for name, definition in cls._platforms.items():
                # Try to validate with empty config (should show required fields)
                try:
                    definition.validate_config({})
                except ValidationError:
                    # This is expected for platforms with required fields
                    pass
                logger.info(f"Schema validation passed for {name}")
            return True
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False
    
    @classmethod
    def clear_registry(cls):
        """Clear all registered platforms (for testing)"""
        cls._platforms.clear()
    
    @classmethod
    def get_platform_by_strategy_class(cls, strategy_class: Type[PlatformStrategy]) -> Optional[PlatformDefinition]:
        """Get platform definition by strategy class"""
        for definition in cls._platforms.values():
            if definition.strategy_class == strategy_class:
                return definition
        return None