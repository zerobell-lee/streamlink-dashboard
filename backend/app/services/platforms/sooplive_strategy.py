"""
Sooplive platform strategy implementation
"""
import re
import asyncio
import aiohttp
import time
import logging
from typing import Dict, List, Optional
from .base_strategy import PlatformStrategy, StreamInfo, StreamUrl

logger = logging.getLogger(__name__)


class SoopliveStrategy(PlatformStrategy):
    """Sooplive platform strategy implementation"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self._session = None
        
        # Get credentials from additional_settings if available
        additional_settings = config.get("additional_settings", {})
        self.username = additional_settings.get("username", config.get("username", ""))
        self.password = additional_settings.get("password", config.get("password", ""))
        
        # Cookie lifetime for session management
        self._cookie_lifetime = 3600  # 1 hour default cookie lifetime
        self._last_login_time = 0  # Track when we last logged in
    
    def get_platform_name(self) -> str:
        return "sooplive"
    
    async def _ensure_login(self) -> bool:
        """
        Ensure we are logged in to Sooplive by updating session cookies
        
        Returns:
            True if login successful, False otherwise
        """
        if not self.username or not self.password:
            return False
        
        # Check if we recently logged in (within cookie lifetime)
        current_time = time.time()
        if current_time < self._last_login_time + self._cookie_lifetime:
            return True  # Assume still valid
            
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            # Login endpoint
            login_url = 'https://login.sooplive.co.kr/app/LoginAction.php'
            login_data = {
                'szWork': 'login',
                'szType': 'json',
                'szUid': self.username,
                'szPassword': self.password,
                'isSaveId': 'true',
                'isSavePw': 'false',
                'isSaveJoin': 'false',
                'isLoginRetain': 'Y'
            }
            
            async with self._session.post(login_url, data=login_data) as response:
                if response.status != 200:
                    logger.warning(f"Sooplive login failed with status: {response.status}")
                    return False
                
                # Cookies are automatically stored in session.cookie_jar
                if response.cookies:
                    self._last_login_time = time.time()
                    logger.info(f"Sooplive login successful for user: {self.username}")
                    return True
                else:
                    logger.warning(f"No cookies received for user: {self.username}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error during Sooplive login: {e}")
            return False

    async def _is_streaming(self, user_id: str) -> Optional[bool]:
        """
        Check if a user is currently streaming using Sooplive API
        
        Args:
            user_id: Sooplive user ID
            
        Returns:
            True if streaming, False if not streaming, None if error
        """
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            # Ensure we're logged in if we have credentials
            has_auth = await self._ensure_login()
            
            logger.debug(f"Checking stream status for {user_id}")
            logger.debug(f"Authentication available: {has_auth}")
            
            url = 'https://live.sooplive.co.kr/afreeca/player_live_api.php'
            data = {
                "bid": user_id,
                "quality": "original",
                "type": "aid", 
                "pwd": "",
                "stream_type": "common",
            }
            
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            
            async with self._session.post(url, data=data, headers=headers) as response:
                if response.status != 200:
                    logger.debug(f"HTTP response status: {response.status}")
                    return None
                
                # Sooplive returns JSON data with text/html MIME type
                # Parse raw string as JSON
                import json
                raw_text = await response.text()
                logger.debug(f"Raw API response: {raw_text[:500]}...")  # First 500 chars
                
                result = json.loads(raw_text)
                channel_result = result.get('CHANNEL', {}).get('RESULT', 'missing')
                logger.debug(f"CHANNEL.RESULT: {channel_result}")
                
                if result['CHANNEL']['RESULT'] == 0:
                    # Not streaming
                    logger.debug(f"{user_id} is not streaming")
                    return False
                elif result['CHANNEL']['RESULT'] == 1:
                    # Currently streaming
                    logger.debug(f"{user_id} is streaming")
                    return True
                elif result['CHANNEL']['RESULT'] == -6:
                    # Member-only broadcast (likely streaming but requires subscription)
                    logger.warning(f"{user_id} is likely streaming but broadcast is member-only (RESULT: -6)")
                    return True
                else:
                    logger.debug(f"Unknown RESULT code: {result['CHANNEL']['RESULT']}")
                    # Authentication failure or other issue - try once more with fresh login
                    if has_auth and self.username and self.password:
                        logger.debug("Retrying with fresh authentication...")
                        # Force fresh login by resetting login time
                        self._last_login_time = 0
                        if await self._ensure_login():
                            async with self._session.post(url, data=data, headers=headers) as auth_response:
                                if auth_response.status == 200:
                                    auth_text = await auth_response.text()
                                    logger.debug(f"Auth retry response: {auth_text[:500]}...")
                                    auth_result = json.loads(auth_text)
                                    auth_channel_result = auth_result.get('CHANNEL', {}).get('RESULT', 'missing')
                                    logger.debug(f"Auth retry RESULT: {auth_channel_result}")
                                    if auth_result['CHANNEL']['RESULT'] == 1:
                                        return True
                                    elif auth_result['CHANNEL']['RESULT'] == 0:
                                        return False
                    return None
                    
        except Exception as e:
            logger.error(f"Error checking Sooplive streaming status for {user_id}: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return None
    
    async def get_stream_info(self, streamer_id: str) -> Optional[StreamInfo]:
        """
        Get Sooplive stream information using Sooplive API
        """
        try:
            logger.debug(f"get_stream_info called for {streamer_id}")
            # Check if streaming
            is_live = await self._is_streaming(streamer_id)
            logger.debug(f"_is_streaming returned: {is_live}")
            
            if is_live is None:
                # API error, cannot determine stream status
                logger.warning(f"Sooplive API error for {streamer_id}, cannot determine stream status")
                return None
            
            if not is_live:
                # Not streaming
                return None
                
            return StreamInfo(
                streamer_id=streamer_id,
                streamer_name="streamer_name",
                title="title",
                is_live=True,
                viewer_count=0,
                thumbnail_url="thumbnail_url",
                started_at=None  # Sooplive API doesn't provide start time
            )
        
        except Exception as e:
            logger.error(f"Error getting Sooplive stream info: {e}")
            return None
    
    async def get_stream_urls(self, streamer_id: str) -> List[StreamUrl]:
        """
        Get Sooplive stream URLs using Streamlink
        """
        # For now, return a mock implementation
        # In a real implementation, you'd use Streamlink's API to get actual stream URLs
        return [
            StreamUrl(
                url=f"https://play.sooplive.co.kr/{streamer_id}",
                quality="best",
                format="hls",
                bandwidth=None
            ),
            StreamUrl(
                url=f"https://play.sooplive.co.kr/{streamer_id}",
                quality="720p",
                format="hls",
                bandwidth=None
            ),
            StreamUrl(
                url=f"https://play.sooplive.co.kr/{streamer_id}",
                quality="480p",
                format="hls",
                bandwidth=None
            )
        ]
    
    def _get_platform_specific_args(self, streamer_id: str, quality: str) -> List[str]:
        """
        Get Sooplive-specific Streamlink arguments
        """
        args = []
        
        # Add Sooplive authentication if credentials are available
        if self.username and self.password:
            args.extend([
                "--soop-username", self.username,
                "--soop-password", self.password,
                "--soop-purge-credentials"
            ])
        
        # Sooplive stream URL
        stream_url = f"https://play.sooplive.co.kr/{streamer_id}"
        
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
