"""
Sooplive platform definition
"""
from ..registry import PlatformRegistry, PlatformDefinition
from ..sooplive_strategy import SoopliveStrategy


# Sooplive platform definition based on actual database configuration
sooplive_definition = PlatformDefinition(
    name="sooplive",
    display_name="SoopLive",
    description="Korean live streaming platform (formerly AfreecaTV)",
    
    # Technical configuration
    strategy_class=SoopliveStrategy,
    config_schema={
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "title": "Username",
                "description": "SoopLive account username"
            },
            "password": {
                "type": "string",
                "title": "Password",
                "description": "SoopLive account password"
            }
        },
        "required": [],
        "additionalProperties": True
    },
    
    # Streaming configuration  
    default_streamlink_args=[],
    supported_qualities=["best", "worst"],
    
    # Output file configuration
    default_output_format="ts",  # Sooplive works best with TS container
    supported_output_formats=["ts", "mp4"],
    default_filename_template="{streamer_id}_{yyyyMMdd}_{HHmmss}",
    
    # Platform features
    requires_auth=False,
    supports_chat=False,
    supports_vod=False,
    
    # UI and help
    help_text="SoopLive (formerly AfreecaTV) is a Korean live streaming platform.",
    setup_instructions="Enter your SoopLive username and password to access streams and premium content.",
    
    # Performance limits
    api_rate_limit=None,
    concurrent_streams_limit=3
)


# Register the platform
PlatformRegistry.register(sooplive_definition)