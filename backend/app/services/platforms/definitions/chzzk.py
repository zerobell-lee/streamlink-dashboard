"""
Chzzk platform definition
"""
from ..registry import PlatformRegistry, PlatformDefinition
from ..chzzk_strategy import ChzzkStrategy


# Chzzk platform definition based on actual database configuration
chzzk_definition = PlatformDefinition(
    name="chzzk",
    display_name="CHZZK",
    description="Naver's live streaming platform",
    
    # Technical configuration
    strategy_class=ChzzkStrategy,
    config_schema={
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": True
    },
    
    # Streaming configuration  
    default_streamlink_args=[],
    supported_qualities=["best", "worst"],
    
    # Output file configuration
    default_output_format="mp4",  # Chzzk works well with MP4
    supported_output_formats=["mp4", "ts", "mkv"],
    default_filename_template="{streamer_id}_{yyyyMMdd}_{HHmmss}",
    
    # Platform features
    requires_auth=False,
    supports_chat=False,
    supports_vod=False,
    
    # UI and help
    help_text="CHZZK is Naver's live streaming platform.",
    setup_instructions="No additional configuration required for CHZZK.",
    
    # Performance limits
    api_rate_limit=None,
    concurrent_streams_limit=3
)


# Register the platform
PlatformRegistry.register(chzzk_definition)