"""
YouTube platform strategy implementation
"""
import asyncio
import logging
import shutil
import sys
import os
from typing import Dict, List, Optional
from .base_strategy import PlatformStrategy, StreamInfo, StreamUrl

logger = logging.getLogger(__name__)


class YouTubeStrategy(PlatformStrategy):
    """YouTube platform strategy implementation"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self._streamlink_path = None

    def get_platform_name(self) -> str:
        return "youtube"

    def _get_streamlink_path(self) -> str:
        """Get the path to streamlink executable"""
        if self._streamlink_path:
            return self._streamlink_path

        from app.core.config import settings

        logger.debug(f"Looking for streamlink executable...")

        # First try the configured path
        if hasattr(settings, 'STREAMLINK_PATH') and settings.STREAMLINK_PATH:
            if shutil.which(settings.STREAMLINK_PATH):
                self._streamlink_path = settings.STREAMLINK_PATH
                return self._streamlink_path

        # Try to find streamlink in various locations
        possible_paths = [
            "streamlink",  # System PATH
            os.path.join(os.path.dirname(sys.executable), "streamlink"),  # Same dir as Python
            os.path.join(os.path.dirname(sys.executable), "bin", "streamlink"),  # Unix venv
            "/usr/local/bin/streamlink",  # Common system location
            "/usr/bin/streamlink",  # System location
        ]

        for path in possible_paths:
            found_path = shutil.which(path)
            if found_path:
                logger.debug(f"Found streamlink at: {found_path}")
                self._streamlink_path = found_path
                return self._streamlink_path

        # Fallback to configured path even if not found
        fallback_path = getattr(settings, 'STREAMLINK_PATH', 'streamlink')
        logger.warning(f"No streamlink found, using fallback: {fallback_path}")
        self._streamlink_path = fallback_path
        return self._streamlink_path

    def _get_youtube_url(self, streamer_id: str) -> str:
        """Get YouTube URL from streamer ID"""
        # Handle different YouTube URL formats
        if streamer_id.startswith("UC") and len(streamer_id) == 24:
            # Channel ID format
            return f"https://www.youtube.com/channel/{streamer_id}/live"
        elif streamer_id.startswith("@"):
            # Handle format
            return f"https://www.youtube.com/{streamer_id}/live"
        elif "/" in streamer_id or streamer_id.startswith("http"):
            # Full URL or path
            if not streamer_id.startswith("http"):
                streamer_id = f"https://www.youtube.com/{streamer_id}"
            if "/live" not in streamer_id:
                streamer_id = streamer_id.rstrip("/") + "/live"
            return streamer_id
        else:
            # Username format - try both handle and channel approaches
            return f"https://www.youtube.com/@{streamer_id}/live"

    async def _check_stream_with_streamlink(self, url: str) -> Optional[Dict]:
        """Use Streamlink to check if stream is available and get info"""
        try:
            streamlink_path = self._get_streamlink_path()

            # Use streamlink to check stream availability
            cmd = [
                streamlink_path,
                "--json",  # Get JSON output
                "--stream-timeout", "10",  # 10 second timeout
                url,
                "--dry-run"  # Don't actually download, just check
            ]

            logger.debug(f"Running streamlink command: {' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=15)

            if process.returncode == 0:
                # Stream is available
                try:
                    import json
                    result = json.loads(stdout.decode())
                    logger.debug(f"Streamlink JSON result: {result}")
                    return result
                except json.JSONDecodeError:
                    # No JSON output but command succeeded - stream likely available
                    logger.debug(f"Streamlink succeeded but no JSON output: {stdout.decode()}")
                    return {"streams": {"best": {"url": url}}}
            else:
                # Stream not available or error
                stderr_text = stderr.decode()
                logger.debug(f"Streamlink failed (exit code {process.returncode}): {stderr_text}")

                # Check if it's just "no streams found" vs actual error
                if "No playable streams found" in stderr_text or "Unable to find" in stderr_text:
                    return None  # Stream offline, not an error
                else:
                    logger.warning(f"Streamlink error for {url}: {stderr_text}")
                    return None

        except asyncio.TimeoutError:
            logger.warning(f"Streamlink timeout for {url}")
            return None
        except Exception as e:
            logger.error(f"Error running streamlink for {url}: {e}")
            return None

    async def get_stream_info(self, streamer_id: str) -> Optional[StreamInfo]:
        """
        Get YouTube stream information using Streamlink
        """
        logger.debug(f"Checking stream info for YouTube: {streamer_id}")

        try:
            # Get the YouTube URL
            url = self._get_youtube_url(streamer_id)
            logger.debug(f"YouTube URL: {url}")

            # Check if stream is live using Streamlink
            stream_data = await self._check_stream_with_streamlink(url)

            if stream_data is None:
                logger.debug(f"No live stream found for {streamer_id}")
                return None

            # Extract channel name from URL if possible
            streamer_name = streamer_id
            if streamer_id.startswith("@"):
                streamer_name = streamer_id[1:]  # Remove @ prefix

            return StreamInfo(
                streamer_id=streamer_id,
                streamer_name=streamer_name,
                title="Live Stream",  # Streamlink doesn't provide title
                is_live=True,
                viewer_count=None,  # Streamlink doesn't provide viewer count
                thumbnail_url=None,  # Streamlink doesn't provide thumbnail
                started_at=None  # Streamlink doesn't provide start time
            )

        except Exception as e:
            logger.error(f"Error getting YouTube stream info for {streamer_id}: {e}")
            return None
    
    async def get_stream_urls(self, streamer_id: str) -> List[StreamUrl]:
        """
        Get YouTube stream URLs using Streamlink
        """
        try:
            # Get the proper YouTube URL
            url = self._get_youtube_url(streamer_id)

            # Check if stream is available first
            stream_data = await self._check_stream_with_streamlink(url)
            if stream_data is None:
                return []

            # Return different quality options
            return [
                StreamUrl(
                    url=url,
                    quality="best",
                    format="hls",
                    bandwidth=None
                ),
                StreamUrl(
                    url=url,
                    quality="720p",
                    format="hls",
                    bandwidth=None
                ),
                StreamUrl(
                    url=url,
                    quality="480p",
                    format="hls",
                    bandwidth=None
                )
            ]
        except Exception as e:
            logger.error(f"Error getting YouTube stream URLs for {streamer_id}: {e}")
            return []

    def _get_platform_specific_args(self, streamer_id: str, quality: str) -> List[str]:
        """
        Get YouTube-specific Streamlink arguments
        """
        args = [
            "--youtube-live-chunk-size", "4",  # Optimize for YouTube
            "--youtube-live-from-start",  # Start from beginning if possible
            "--stream-segment-threads", "2"  # Optimize performance
        ]

        # Get the proper YouTube URL
        stream_url = self._get_youtube_url(streamer_id)

        # Add URL and quality as the last arguments
        args.extend([
            stream_url,
            quality
        ])

        return args
    
    async def close(self):
        """Cleanup resources - no resources to clean up for YouTube strategy"""
        pass
