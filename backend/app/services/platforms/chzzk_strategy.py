"""
Chzzk (치지직) platform strategy implementation
"""
import aiohttp
import logging
from typing import Dict, List, Optional
from .base_strategy import PlatformStrategy, StreamInfo, StreamUrl

logger = logging.getLogger(__name__)


class ChzzkStrategy(PlatformStrategy):
    """Chzzk platform strategy implementation"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self._session = None
    
    def get_platform_name(self) -> str:
        return "chzzk"
    
    async def get_stream_info(self, streamer_id: str) -> Optional[StreamInfo]:
        """
        Get Chzzk stream information using Chzzk API
        
        Args:
            streamer_id: Chzzk channel ID
            
        Returns:
            StreamInfo if streaming, None otherwise
        """
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            logger.debug(f"Checking stream info for Chzzk channel: {streamer_id}")
            
            # Chzzk API endpoint
            url = f"https://api.chzzk.naver.com/service/v1/channels/{streamer_id}"
            
            # Chzzk API requires User-Agent header to prevent bot blocking
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            async with self._session.get(url, headers=headers) as response:
                if response.status != 200:
                    logger.debug(f"Chzzk API returned status: {response.status}")
                    return None
                
                data = await response.json()
                logger.debug(f"Chzzk API response: {data}")
                
                # Check if the response contains content
                content = data.get("content")
                if not content:
                    logger.debug(f"No content found for channel: {streamer_id}")
                    return None
                
                # Check if stream is live using $.content.openLive
                is_live = content.get("openLive", False)
                if not is_live:
                    logger.debug(f"Channel {streamer_id} is not live")
                    return None
                
                # Extract stream information
                channel_name = content.get("channelName", streamer_id)
                channel_description = content.get("channelDescription", "")
                
                # Additional info available but not used currently
                # follower_count = content.get("followerCount")
                
                logger.info(f"Chzzk stream info retrieved for {streamer_id}: {channel_name}")
                return StreamInfo(
                    streamer_id=streamer_id,
                    streamer_name=channel_name,
                    title=channel_description or "Live Stream",
                    is_live=True,
                    viewer_count=None,  # Chzzk API doesn't provide current viewer count in channel info
                    thumbnail_url=None,  # Would need additional API call for live stream thumbnail
                    started_at=None  # Would need additional API call for stream start time
                )
                
        except Exception as e:
            logger.error(f"Error getting Chzzk stream info for {streamer_id}: {e}")
            return None
    
    async def get_stream_urls(self, streamer_id: str) -> List[StreamUrl]:
        """
        Get Chzzk stream URLs using Streamlink
        """
        # Return Chzzk stream URLs for Streamlink
        stream_url = f"https://chzzk.naver.com/live/{streamer_id}"
        
        return [
            StreamUrl(
                url=stream_url,
                quality="best",
                format="hls",
                bandwidth=None
            ),
            StreamUrl(
                url=stream_url,
                quality="720p",
                format="hls",
                bandwidth=None
            ),
            StreamUrl(
                url=stream_url,
                quality="480p",
                format="hls",
                bandwidth=None
            )
        ]
    
    def _get_platform_specific_args(self, streamer_id: str, quality: str) -> List[str]:
        """
        Get Chzzk-specific Streamlink arguments
        """
        args = []
        
        # Chzzk stream URL
        stream_url = f"https://chzzk.naver.com/live/{streamer_id}"
        
        # Add URL and quality as the last arguments
        args.extend([
            stream_url,
            quality
        ])
        
        return args
    
    async def close(self):
        """Close the aiohttp session"""
        if self._session:
            await self._session.close()
            self._session = None