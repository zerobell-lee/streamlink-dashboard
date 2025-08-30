"""
Twitch platform strategy implementation
"""
import re
import asyncio
import aiohttp
import time
import logging
from typing import Dict, List, Optional
from .base_strategy import PlatformStrategy, StreamInfo, StreamUrl

logger = logging.getLogger(__name__)


class TwitchStrategy(PlatformStrategy):
    """Twitch platform strategy implementation"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        # Support both old client credentials and new api_token approach
        self.client_id = config.get("client_id", "")
        self.client_secret = config.get("client_secret", "")
        self.api_token = config.get("api_token", "")  # User-provided API token
        
        # Token caching with expiration
        self.access_token = None
        self._token_expires_at = 0  # Unix timestamp when token expires
        self._session = None
    
    def get_platform_name(self) -> str:
        return "twitch"
    
    async def _get_access_token(self) -> Optional[str]:
        """Get Twitch API access token with caching"""
        # Check if cached token is still valid
        current_time = time.time()
        if self.access_token and current_time < self._token_expires_at:
            return self.access_token
        
        if not self.client_id or not self.client_secret:
            # Use public API (limited functionality)
            return None
        
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            url = "https://id.twitch.tv/oauth2/token"
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials"
            }
            
            async with self._session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.access_token = result.get("access_token")
                    # Set expiration time (Twitch tokens typically last 60 days, but we'll be conservative with 1 hour)
                    expires_in = result.get("expires_in", 3600)  # Default to 1 hour if not provided
                    self._token_expires_at = time.time() + expires_in
                    return self.access_token
        except Exception as e:
            logger.error(f"Error getting Twitch access token: {e}")
        
        return None
    
    async def get_stream_info(self, streamer_id: str) -> Optional[StreamInfo]:
        """
        Get Twitch stream information using Twitch API
        """
        logger.debug(f"Checking stream info for {streamer_id}")
        try:
            headers = {}
            
            # Use user-provided API token if available, otherwise try OAuth flow
            if self.api_token:
                logger.debug("Using provided API token")
                headers["Authorization"] = f"Bearer {self.api_token}"
                # For API tokens, we need to extract client_id from the token or use a default
                # Most Twitch API tokens require a client_id, so we'll use a known valid one
                headers["Client-Id"] = "kimne78kx3ncx6brgo4mv6wki5h1ko"  # Public client ID
            else:
                logger.debug(f"Using OAuth flow with client_id={self.client_id}")
                access_token = await self._get_access_token()
                if access_token:
                    logger.debug("Got OAuth access token")
                    headers["Authorization"] = f"Bearer {access_token}"
                    headers["Client-Id"] = self.client_id
                else:
                    logger.warning("Failed to get OAuth access token")
            
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            # First get user info
            user_url = f"https://api.twitch.tv/helix/users?login={streamer_id}"
            async with self._session.get(user_url, headers=headers) as response:
                if response.status != 200:
                    return None
                
                user_data = await response.json()
                if not user_data.get("data"):
                    return None
                
                user = user_data["data"][0]
                user_id = user["id"]
                display_name = user["display_name"]
            
            # Then get stream info
            stream_url = f"https://api.twitch.tv/helix/streams?user_id={user_id}"
            async with self._session.get(stream_url, headers=headers) as response:
                if response.status != 200:
                    return None
                
                stream_data = await response.json()
                streams = stream_data.get("data", [])
                
                if not streams:
                    return None
                
                stream = streams[0]
                return StreamInfo(
                    streamer_id=streamer_id,
                    streamer_name=display_name,
                    title=stream.get("title", ""),
                    is_live=True,
                    viewer_count=stream.get("viewer_count"),
                    thumbnail_url=stream.get("thumbnail_url", "").replace("{width}", "320").replace("{height}", "180"),
                    started_at=stream.get("started_at")
                )
        
        except Exception as e:
            logger.error(f"Error getting Twitch stream info: {e}")
            return None
    
    async def get_stream_urls(self, streamer_id: str) -> List[StreamUrl]:
        """
        Get Twitch stream URLs using Streamlink
        Note: This is a simplified implementation. In practice, you'd use Streamlink's API
        """
        # For now, return a mock implementation
        # In a real implementation, you'd use Streamlink's API to get actual stream URLs
        return [
            StreamUrl(
                url=f"https://www.twitch.tv/{streamer_id}",
                quality="best",
                format="hls",
                bandwidth=None
            ),
            StreamUrl(
                url=f"https://www.twitch.tv/{streamer_id}",
                quality="720p",
                format="hls",
                bandwidth=None
            ),
            StreamUrl(
                url=f"https://www.twitch.tv/{streamer_id}",
                quality="480p",
                format="hls",
                bandwidth=None
            )
        ]
    
    def _get_platform_specific_args(self, streamer_id: str, quality: str) -> List[str]:
        """
        Get Twitch-specific Streamlink arguments
        """
        args = [
            "--twitch-disable-ads",  # Disable ads
            "--twitch-disable-hosting",  # Disable hosting
            "--twitch-disable-ads",  # Disable ads again (sometimes needed)
        ]
        
        # Add quality
        args.extend(["--stream-segment-threads", "2"])  # Optimize for Twitch
        
        # Add stream URL
        stream_url = f"https://www.twitch.tv/{streamer_id}"
        args.append(stream_url)
        args.append(quality)
        
        return args
    
    async def close(self):
        """Close the aiohttp session"""
        if self._session:
            await self._session.close()
            self._session = None
