"""
Twitch platform definition
"""
from ..registry import PlatformRegistry, PlatformDefinition
from ..twitch_strategy import TwitchStrategy


# Twitch platform definition with detailed configuration schema
twitch_definition = PlatformDefinition(
    name="twitch",
    display_name="Twitch",
    description="Live streaming platform owned by Amazon, popular for gaming and creative content",
    
    # Technical configuration
    strategy_class=TwitchStrategy,
    config_schema={
        "type": "object",
        "properties": {
            "client_id": {
                "type": "string",
                "title": "Client ID",
                "description": "Twitch Application Client ID"
            },
            "client_secret": {
                "type": "string", 
                "title": "Client Secret",
                "description": "Twitch Application Client Secret"
            },
            "api_token": {
                "type": "string",
                "title": "API Token", 
                "description": "Personal API token for Twitch API access"
            },
            "--twitch-disable-ads": {
                "type": "boolean",
                "title": "Disable Ads",
                "description": "Skip embedded Twitch ads",
                "default": True
            },
            "--twitch-disable-hosting": {
                "type": "boolean",
                "title": "Disable Hosting",
                "description": "Do not open hosted streams",
                "default": True
            }
        },
        "required": [],
        "additionalProperties": True
    },
    
    # Streaming configuration
    default_streamlink_args=[
        "--hls-live-edge", "6",  # HLS live edge segments
        "--hls-timeout", "60",   # HLS timeout
        "--hls-segment-stream-data"  # Better handling of stream data
    ],
    supported_qualities=[
        "source",    # Original quality (best)
        "1080p60",   # 1080p 60fps
        "1080p",     # 1080p 30fps  
        "900p60",    # 900p 60fps
        "900p",      # 900p 30fps
        "720p60",    # 720p 60fps
        "720p",      # 720p 30fps
        "540p",      # 540p
        "480p",      # 480p
        "360p",      # 360p
        "160p",      # 160p (audio only basically)
        "best",      # Best available quality
        "worst"      # Worst available quality
    ],
    
    # Platform features
    requires_auth=False,  # Works without auth but limited
    supports_chat=True,   # Chat can be recorded
    supports_vod=True,    # VODs can be recorded
    
    # UI and help
    help_text="""
    Twitch is Amazon's live streaming platform. You can record streams without authentication,
    but having API credentials provides better reliability and higher rate limits.
    """,
    setup_instructions="""
    To set up Twitch with API credentials:
    1. Go to https://dev.twitch.tv/console
    2. Create a new application
    3. Copy the Client ID and Client Secret
    4. Alternatively, generate a personal API token
    
    Without credentials, public API access is limited but functional.
    """,
    
    # Performance limits
    api_rate_limit=800,  # Twitch API: 800 requests per minute with app credentials
    concurrent_streams_limit=5  # Reasonable limit for concurrent streams
)


# Register the platform
PlatformRegistry.register(twitch_definition)