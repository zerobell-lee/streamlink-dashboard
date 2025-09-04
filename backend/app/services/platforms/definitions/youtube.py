"""
YouTube platform definition
"""
from ..registry import PlatformRegistry, PlatformDefinition
from ..youtube_strategy import YouTubeStrategy


# YouTube platform definition with detailed configuration schema
youtube_definition = PlatformDefinition(
    name="youtube",
    display_name="YouTube",
    description="Google's video platform supporting live streaming and VOD content",
    
    # Technical configuration
    strategy_class=YouTubeStrategy,
    config_schema={
        "type": "object",
        "properties": {
            "api_key": {
                "type": "string",
                "title": "API Key",
                "description": "YouTube Data API v3 key for accessing live stream information"
            },
            "--youtube-live-chunk-size": {
                "type": "string",
                "title": "Live Chunk Size",
                "description": "Size of chunks to fetch for live streams",
                "default": "4"
            },
            "--youtube-live-from-start": {
                "type": "boolean",
                "title": "Record from Start",
                "description": "Record live streams from the beginning",
                "default": True
            }
        },
        "required": [],
        "additionalProperties": True
    },
    
    # Streaming configuration
    default_streamlink_args=[
        "--hls-timeout", "60",
        "--http-timeout", "60"
    ],
    supported_qualities=[
        "1080p60",   # 1080p 60fps
        "1080p",     # 1080p 30fps
        "720p60",    # 720p 60fps
        "720p",      # 720p 30fps
        "480p",      # 480p
        "360p",      # 360p
        "240p",      # 240p
        "144p",      # 144p
        "best",      # Best available quality
        "worst"      # Worst available quality
    ],
    
    # Platform features
    requires_auth=True,   # YouTube requires API key
    supports_chat=True,   # YouTube chat can be recorded
    supports_vod=True,    # YouTube VODs supported
    
    # UI and help
    help_text="""
    YouTube Live streaming requires a YouTube Data API v3 key for accessing 
    live stream information and chat data.
    """,
    setup_instructions="""
    To set up YouTube Live recording:
    1. Go to Google Cloud Console (https://console.cloud.google.com/)
    2. Create a new project or select existing one
    3. Enable YouTube Data API v3
    4. Create credentials (API Key)
    5. Copy the API key and paste it here
    
    Make sure to restrict the API key to YouTube Data API for security.
    """,
    
    # Performance limits
    api_rate_limit=10000,  # YouTube Data API: 10,000 units per day by default
    concurrent_streams_limit=3  # Conservative limit for YouTube Live
)


# Register the platform
PlatformRegistry.register(youtube_definition)