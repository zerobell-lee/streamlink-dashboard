"""
YouTube platform strategy implementation
"""
import re
import asyncio
import aiohttp
from typing import Dict, List, Optional
from .base_strategy import PlatformStrategy, StreamInfo, StreamUrl


class YouTubeStrategy(PlatformStrategy):
    """YouTube platform strategy implementation"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self._session = None
    
    def get_platform_name(self) -> str:
        return "youtube"
    
    async def get_stream_info(self, streamer_id: str) -> Optional[StreamInfo]:
        """
        Get YouTube stream information using YouTube Data API
        """
        if not self.api_key:
            # Without API key, we can't get detailed info
            return None
        
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            # First, get channel info
            channel_id = await self._get_channel_id(streamer_id)
            if not channel_id:
                return None
            
            # Get live streams for this channel
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "channelId": channel_id,
                "type": "video",
                "eventType": "live",
                "key": self.api_key
            }
            
            async with self._session.get(url, params=params) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                items = data.get("items", [])
                
                if not items:
                    return None
                
                video_id = items[0]["id"]["videoId"]
                snippet = items[0]["snippet"]
                
                # Get video details
                video_url = "https://www.googleapis.com/youtube/v3/videos"
                video_params = {
                    "part": "snippet,statistics,liveStreamingDetails",
                    "id": video_id,
                    "key": self.api_key
                }
                
                async with self._session.get(video_url, params=video_params) as response:
                    if response.status != 200:
                        return None
                    
                    video_data = await response.json()
                    video_items = video_data.get("items", [])
                    
                    if not video_items:
                        return None
                    
                    video = video_items[0]
                    video_snippet = video["snippet"]
                    live_details = video.get("liveStreamingDetails", {})
                    
                    return StreamInfo(
                        streamer_id=streamer_id,
                        streamer_name=video_snippet.get("channelTitle", ""),
                        title=video_snippet.get("title", ""),
                        is_live=True,
                        viewer_count=live_details.get("concurrentViewers"),
                        thumbnail_url=video_snippet.get("thumbnails", {}).get("medium", {}).get("url"),
                        started_at=live_details.get("actualStartTime")
                    )
        
        except Exception as e:
            print(f"Error getting YouTube stream info: {e}")
            return None
    
    async def _get_channel_id(self, streamer_id: str) -> Optional[str]:
        """Get YouTube channel ID from username or channel ID"""
        if not self.api_key:
            return None
        
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            # If it's already a channel ID, return it
            if re.match(r'^UC[a-zA-Z0-9_-]{22}$', streamer_id):
                return streamer_id
            
            # Search for channel by username
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": streamer_id,
                "type": "channel",
                "key": self.api_key
            }
            
            async with self._session.get(url, params=params) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                items = data.get("items", [])
                
                if items:
                    return items[0]["id"]["channelId"]
        
        except Exception as e:
            print(f"Error getting YouTube channel ID: {e}")
        
        return None
    
    async def get_stream_urls(self, streamer_id: str) -> List[StreamUrl]:
        """
        Get YouTube stream URLs using Streamlink
        """
        # For now, return a mock implementation
        # In a real implementation, you'd use Streamlink's API to get actual stream URLs
        return [
            StreamUrl(
                url=f"https://www.youtube.com/channel/{streamer_id}/live",
                quality="best",
                format="hls",
                bandwidth=None
            ),
            StreamUrl(
                url=f"https://www.youtube.com/channel/{streamer_id}/live",
                quality="720p",
                format="hls",
                bandwidth=None
            ),
            StreamUrl(
                url=f"https://www.youtube.com/channel/{streamer_id}/live",
                quality="480p",
                format="hls",
                bandwidth=None
            )
        ]
    
    def _get_platform_specific_args(self, streamer_id: str, quality: str) -> List[str]:
        """
        Get YouTube-specific Streamlink arguments
        """
        args = [
            "--youtube-live-chunk-size", "4",  # Optimize for YouTube
            "--youtube-live-from-start",  # Start from beginning if possible
        ]
        
        # Add quality
        args.extend(["--stream-segment-threads", "2"])
        
        # Add stream URL
        stream_url = f"https://www.youtube.com/channel/{streamer_id}/live"
        args.append(stream_url)
        args.append(quality)
        
        return args
    
    async def close(self):
        """Close the aiohttp session"""
        if self._session:
            await self._session.close()
            self._session = None
