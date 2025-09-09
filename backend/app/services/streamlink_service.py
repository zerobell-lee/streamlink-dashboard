"""
Streamlink service for managing actual recording processes
"""
import asyncio
import logging
import subprocess
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import Recording, RecordingSchedule
from app.services.platform_service import PlatformService
from app.services.platforms.strategy_factory import PlatformStrategyFactory
from app.services.output_filename_template import OutputFileNameTemplate

logger = logging.getLogger(__name__)


class StreamlinkService:
    """Service for managing Streamlink recording processes"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.platform_service = PlatformService(db)
        self._active_recordings: Dict[int, asyncio.Task] = {}
    
    async def start_recording(
        self, 
        recording_id: int, 
        schedule_id: int,
        platform: str, 
        streamer_id: str, 
        quality: str = "best",
        output_path: str = None
    ) -> bool:
        """
        Start a recording using Streamlink
        
        Args:
            recording_id: Database recording ID
            platform: Platform name (twitch, youtube, sooplive)
            streamer_id: Streamer identifier
            quality: Stream quality
            output_path: Output file path
            
        Returns:
            True if recording started successfully
        """
        try:
            logger.info(f"=== Starting recording {recording_id} ===")
            logger.info(f"Platform: {platform}, Streamer: {streamer_id}, Quality: {quality}")
            
            # Get recording schedule for output format and filename template
            schedule_query = select(RecordingSchedule).where(RecordingSchedule.id == schedule_id)
            schedule_result = await self.db.execute(schedule_query)
            schedule = schedule_result.scalar_one_or_none()
            
            if not schedule:
                logger.error(f"Recording schedule {schedule_id} not found")
                return False
            
            # Get platform definition for defaults
            platform_definition = PlatformStrategyFactory.get_platform_definition(platform)
            if not platform_definition:
                logger.error(f"Platform definition not found for: {platform}")
                return False
            
            # Determine output format (schedule override or platform default)
            output_format = schedule.output_format or platform_definition.default_output_format
            
            # Determine filename template (schedule override or platform default)  
            filename_template = schedule.filename_template or platform_definition.default_filename_template
            
            # Generate filename using template engine
            if not output_path:
                template_engine = OutputFileNameTemplate(filename_template)
                output_filename = template_engine.generate_filename(
                    streamer_id=streamer_id,
                    platform=platform,
                    quality=quality,
                    streamer_name=schedule.streamer_name,
                    title=f"{schedule.streamer_name} Stream",
                    file_extension=output_format
                )
                
                # Default output directory
                output_dir = os.path.join("recordings", platform)
                output_path = os.path.join(output_dir, output_filename)
            
            logger.info(f"Output format: {output_format}")
            logger.info(f"Filename template: {filename_template}")
            logger.info(f"Generated output path: {output_path}")
            
            # Check if output directory exists
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                logger.info(f"Creating output directory: {output_dir}")
                os.makedirs(output_dir, exist_ok=True)
            
            # Get platform strategy
            logger.info(f"Getting platform strategy for {platform}")
            strategy = await self.platform_service.get_strategy(platform)
            if not strategy:
                logger.error(f"No strategy found for platform: {platform}")
                return False
            
            logger.info(f"Strategy found: {type(strategy).__name__}")
            
            # Get Streamlink arguments
            logger.info(f"Getting Streamlink arguments for {platform}/{streamer_id} with quality {quality}")
            args = await self.platform_service.get_streamlink_args(platform, streamer_id, quality)
            
            logger.info(f"Received Streamlink arguments: {args}")
            
            if not args:
                logger.error(f"Could not get Streamlink arguments for {platform}/{streamer_id}")
                return False
            
            # Add debug logging level for better error capture
            args.extend(["--loglevel", "debug"])
            logger.info("Added --loglevel debug for better error capture")
            
            # Add output path if provided
            if output_path:
                args.extend(["--output", output_path])
                logger.info(f"Added output path to args: {output_path}")
            
            # Get streamlink executable path
            streamlink_path = self._get_streamlink_path()
            logger.info(f"Using Streamlink path: {streamlink_path}")
            
            # Create Streamlink command
            cmd = [streamlink_path] + args
            
            logger.info(f"Final Streamlink command: {' '.join(cmd)}")
            
            # Check if streamlink is available
            try:
                logger.info(f"Testing streamlink executable: {streamlink_path}")
                result = await asyncio.create_subprocess_exec(
                    streamlink_path, "--version",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await result.communicate()
                
                logger.info(f"Streamlink version check - Return code: {result.returncode}")
                logger.info(f"Streamlink version check - Stdout: {stdout.decode().strip()}")
                logger.info(f"Streamlink version check - Stderr: {stderr.decode().strip()}")
                
                if result.returncode == 0:
                    logger.info(f"Streamlink version: {stdout.decode().strip()}")
                else:
                    logger.error(f"Streamlink version check failed with return code {result.returncode}")
                    logger.error(f"Stdout: {stdout.decode()}")
                    logger.error(f"Stderr: {stderr.decode()}")
                    logger.error("Please install streamlink: pip install streamlink")
                    return False
            except FileNotFoundError as e:
                logger.error(f"Streamlink executable not found: {streamlink_path}")
                logger.error(f"Error: {e}")
                logger.error("Please install streamlink: pip install streamlink")
                return False
            except Exception as e:
                logger.error(f"Failed to check Streamlink version: {e}")
                logger.error(f"Exception type: {type(e).__name__}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return False
            
            logger.info(f"Starting Streamlink process...")
            logger.info(f"Command: {' '.join(cmd)}")
            logger.info(f"Working directory: {os.getcwd()}")
            
            # Set up environment variables for better output capture
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            logger.info("Set PYTHONUNBUFFERED=1 for better stderr capture")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                limit=1024*1024  # 1MB buffer limit
            )
            
            logger.info(f"Streamlink process started with PID: {process.pid}")
            
            # Create task to monitor the process
            task = asyncio.create_task(
                self._monitor_recording(recording_id, process, output_path)
            )
            
            self._active_recordings[recording_id] = task
            
            logger.info(f"Recording {recording_id} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting recording {recording_id}: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def stop_recording(self, recording_id: int) -> bool:
        """
        Stop a recording
        
        Args:
            recording_id: Database recording ID
            
        Returns:
            True if recording stopped successfully
        """
        try:
            logger.info(f"Attempting to stop recording {recording_id}")
            
            # Cancel the monitoring task if it exists in memory
            task_cancelled = False
            if recording_id in self._active_recordings:
                task = self._active_recordings[recording_id]
                task.cancel()
                del self._active_recordings[recording_id]
                task_cancelled = True
                logger.info(f"Cancelled in-memory task for recording {recording_id}")
            else:
                logger.info(f"No in-memory task found for recording {recording_id}")
            
            # Get recording from database
            result = await self.db.execute(
                select(Recording).where(Recording.id == recording_id)
            )
            recording = result.scalar_one_or_none()
            
            if not recording:
                logger.error(f"Recording {recording_id} not found in database")
                return False
            
            # If no task was cancelled but recording is still active, 
            # we need to kill the process manually (server restart scenario)
            if not task_cancelled and recording.status == "recording":
                logger.warning(f"Recording {recording_id} is active but no task found - attempting to kill streamlink process")
                # Try to kill streamlink processes for this recording
                killed_processes = await self._kill_streamlink_processes_for_recording(recording)
                if killed_processes:
                    logger.info(f"Killed {killed_processes} streamlink processes for recording {recording_id}")
            
            # Update recording status in database
            recording.status = "completed"
            recording.end_time = datetime.now()
            
            # Calculate duration
            if recording.start_time and recording.end_time:
                duration = (recording.end_time - recording.start_time).total_seconds()
                recording.duration = int(duration)
            
            # Update file size if file exists
            if recording.file_path and os.path.exists(recording.file_path):
                recording.file_size = os.path.getsize(recording.file_path)
            
            await self.db.commit()
            
            logger.info(f"Recording {recording_id} stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping recording {recording_id}: {e}")
            return False
    
    async def _kill_streamlink_processes_for_recording(self, recording) -> int:
        """Kill streamlink processes for a specific recording"""
        try:
            import subprocess
            import signal
            
            killed_count = 0
            
            # Get all streamlink processes
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if 'streamlink' in line and recording.file_path in line:
                    # Extract PID (second column)
                    parts = line.split()
                    if len(parts) > 1:
                        try:
                            pid = int(parts[1])
                            logger.info(f"Killing streamlink process PID {pid} for recording {recording.id}")
                            os.kill(pid, signal.SIGTERM)
                            killed_count += 1
                        except (ValueError, ProcessLookupError) as e:
                            logger.warning(f"Failed to kill process: {e}")
            
            return killed_count
            
        except Exception as e:
            logger.error(f"Error killing streamlink processes: {e}")
            return 0
    
    async def _monitor_recording(self, recording_id: int, process: asyncio.subprocess.Process, output_path: str):
        """
        Monitor a recording process with real-time stderr capture
        
        Args:
            recording_id: Database recording ID
            process: Subprocess process
            output_path: Output file path
        """
        stderr_lines = []
        stdout_lines = []
        
        try:
            logger.info(f"Starting real-time monitoring for recording {recording_id}")
            
            # Create tasks for real-time stdout and stderr reading
            async def read_stderr():
                try:
                    while True:
                        line = await process.stderr.readline()
                        if not line:
                            break
                        line_text = line.decode('utf-8', errors='ignore').strip()
                        if line_text:
                            stderr_lines.append(line_text)
                            logger.debug(f"Recording {recording_id} stderr: {line_text}")
                except Exception as e:
                    logger.error(f"Error reading stderr for recording {recording_id}: {e}")
            
            async def read_stdout():
                try:
                    while True:
                        line = await process.stdout.readline()
                        if not line:
                            break
                        line_text = line.decode('utf-8', errors='ignore').strip()
                        if line_text:
                            stdout_lines.append(line_text)
                            logger.debug(f"Recording {recording_id} stdout: {line_text}")
                except Exception as e:
                    logger.error(f"Error reading stdout for recording {recording_id}: {e}")
            
            # Start reading tasks
            stderr_task = asyncio.create_task(read_stderr())
            stdout_task = asyncio.create_task(read_stdout())
            
            # Wait for process to complete
            logger.info(f"Waiting for recording {recording_id} process to complete...")
            await process.wait()
            
            # Wait a bit more for any remaining output to be read
            await asyncio.sleep(0.5)
            
            # Cancel reading tasks
            stderr_task.cancel()
            stdout_task.cancel()
            
            # Wait for tasks to finish
            try:
                await stderr_task
            except asyncio.CancelledError:
                pass
            
            try:
                await stdout_task
            except asyncio.CancelledError:
                pass
            
            logger.info(f"Recording {recording_id} process completed with return code: {process.returncode}")
            logger.info(f"Captured {len(stderr_lines)} stderr lines and {len(stdout_lines)} stdout lines")
            
            # Update recording status
            result = await self.db.execute(
                select(Recording).where(Recording.id == recording_id)
            )
            recording = result.scalar_one_or_none()
            
            if recording:
                recording.end_time = datetime.now()
                
                if process.returncode == 0:
                    recording.status = "completed"
                    logger.info(f"Recording {recording_id} completed successfully")
                elif process.returncode == 130:
                    # Exit code 130 = SIGINT (Ctrl+C) - normal shutdown/cancellation
                    recording.status = "completed"
                    logger.info(f"Recording {recording_id} completed (interrupted by user/scheduler)")
                else:
                    recording.status = "failed"
                    error_msg = f"Recording failed with return code {process.returncode}"
                    
                    # Combine stderr lines into error message
                    if stderr_lines:
                        stderr_text = '\n'.join(stderr_lines[-10:])  # Last 10 lines
                        error_msg += f"\n--- Stderr Output ---\n{stderr_text}"
                        logger.error(f"Recording {recording_id} stderr ({len(stderr_lines)} lines):")
                        for i, line in enumerate(stderr_lines[-5:], 1):  # Log last 5 lines
                            logger.error(f"  [{i}] {line}")
                    else:
                        logger.error(f"Recording {recording_id}: No stderr output captured")
                        error_msg += "\nNo stderr output was captured (possible buffer issue)"
                    
                    # Also include last few stdout lines for context
                    if stdout_lines:
                        stdout_text = '\n'.join(stdout_lines[-5:])  # Last 5 lines  
                        error_msg += f"\n--- Last Stdout Output ---\n{stdout_text}"
                    
                    recording.error_message = error_msg
                    logger.error(f"Recording {recording_id} failed with return code {process.returncode}")
                
                # Calculate duration
                if recording.start_time and recording.end_time:
                    duration = (recording.end_time - recording.start_time).total_seconds()
                    recording.duration = int(duration)
                
                # Update file size if file exists
                if output_path and os.path.exists(output_path):
                    recording.file_size = os.path.getsize(output_path)
                
                await self.db.commit()
            
            # Remove from active recordings
            if recording_id in self._active_recordings:
                del self._active_recordings[recording_id]
                
        except asyncio.CancelledError:
            # Recording was cancelled
            logger.info(f"Recording {recording_id} was cancelled")
            logger.info(f"Captured {len(stderr_lines)} stderr lines and {len(stdout_lines)} stdout lines before cancellation")
            
            # Kill the process
            if process.returncode is None:
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    process.kill()
            
            # Update recording status
            result = await self.db.execute(
                select(Recording).where(Recording.id == recording_id)
            )
            recording = result.scalar_one_or_none()
            
            if recording:
                recording.status = "completed"
                recording.end_time = datetime.now()
                
                # Add stderr/stdout info to error message if available
                if stderr_lines or stdout_lines:
                    error_parts = ["Recording cancelled by user/scheduler"]
                    if stderr_lines:
                        error_parts.append(f"--- Last Stderr Output ({len(stderr_lines)} lines) ---")
                        error_parts.extend(stderr_lines[-5:])  # Last 5 lines
                    if stdout_lines:
                        error_parts.append(f"--- Last Stdout Output ({len(stdout_lines)} lines) ---") 
                        error_parts.extend(stdout_lines[-5:])  # Last 5 lines
                    recording.error_message = '\n'.join(error_parts)
                
                # Calculate duration
                if recording.start_time and recording.end_time:
                    duration = (recording.end_time - recording.start_time).total_seconds()
                    recording.duration = int(duration)
                
                # Update file size if file exists
                if recording.file_path and os.path.exists(recording.file_path):
                    recording.file_size = os.path.getsize(recording.file_path)
                
                await self.db.commit()
            
            # Remove from active recordings
            if recording_id in self._active_recordings:
                del self._active_recordings[recording_id]
                
        except Exception as e:
            logger.error(f"Error monitoring recording {recording_id}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Log captured output for debugging
            logger.error(f"Captured {len(stderr_lines)} stderr lines and {len(stdout_lines)} stdout lines before error")
            if stderr_lines:
                logger.error("Last stderr lines:")
                for line in stderr_lines[-3:]:
                    logger.error(f"  {line}")
            
            # Update recording status to failed
            result = await self.db.execute(
                select(Recording).where(Recording.id == recording_id)
            )
            recording = result.scalar_one_or_none()
            
            if recording:
                recording.status = "failed"
                recording.end_time = datetime.now()
                
                error_parts = [f"Exception during recording monitoring: {str(e)}"]
                if stderr_lines:
                    error_parts.append(f"--- Stderr Output ({len(stderr_lines)} lines) ---")
                    error_parts.extend(stderr_lines[-5:])  # Last 5 lines
                if stdout_lines:
                    error_parts.append(f"--- Stdout Output ({len(stdout_lines)} lines) ---")
                    error_parts.extend(stdout_lines[-5:])  # Last 5 lines
                
                recording.error_message = '\n'.join(error_parts)
                await self.db.commit()
            
            # Remove from active recordings
            if recording_id in self._active_recordings:
                del self._active_recordings[recording_id]
    
    async def get_active_recordings(self) -> List[Dict]:
        """Get list of active recordings from both memory and database"""
        try:
            active_list = []
            processed_ids = set()
            
            # First, get recordings from active tasks (in-memory)
            for recording_id, task in self._active_recordings.items():
                # Get recording info from database
                result = await self.db.execute(
                    select(Recording).where(Recording.id == recording_id)
                )
                recording = result.scalar_one_or_none()
                
                if recording:
                    active_list.append({
                        "id": recording_id,
                        "recording_id": recording_id,
                        "file_path": recording.file_path,
                        "start_time": recording.start_time.isoformat() if recording.start_time else None,
                        "status": recording.status,
                        "schedule_id": recording.schedule_id,
                        "file_size": recording.file_size,
                        "platform": recording.platform,
                        "streamer_id": recording.streamer_id,
                        "streamer_name": recording.streamer_name,
                        "quality": recording.quality,
                        "duration": recording.duration,
                        "task_running": not task.done()
                    })
                    processed_ids.add(recording_id)
            
            # Then, get recordings from database with status='recording' (in case of server restart)
            result = await self.db.execute(
                select(Recording).where(Recording.status == "recording")
            )
            db_active_recordings = result.scalars().all()
            
            for recording in db_active_recordings:
                if recording.id not in processed_ids:
                    # This recording is active in DB but not in memory (server restart scenario)
                    active_list.append({
                        "id": recording.id,
                        "recording_id": recording.id,
                        "file_path": recording.file_path,
                        "start_time": recording.start_time.isoformat() if recording.start_time else None,
                        "status": recording.status,
                        "schedule_id": recording.schedule_id,
                        "file_size": recording.file_size,
                        "platform": recording.platform,
                        "streamer_id": recording.streamer_id,
                        "streamer_name": recording.streamer_name,
                        "quality": recording.quality,
                        "duration": recording.duration,
                        "task_running": False  # No task in memory
                    })
            
            logger.debug(f"Found {len(active_list)} active recordings (memory: {len(self._active_recordings)}, db: {len(db_active_recordings)})")
            
            return active_list
            
        except Exception as e:
            logger.error(f"Error getting active recordings: {e}")
            return []
    
    async def get_active_recordings_by_schedule(self, schedule_id: int) -> List[Dict]:
        """Get list of active recordings for a specific schedule"""
        try:
            active_list = []
            
            for recording_id, task in self._active_recordings.items():
                # Get recording info from database
                result = await self.db.execute(
                    select(Recording).where(Recording.id == recording_id)
                )
                recording = result.scalar_one_or_none()
                
                if recording and recording.schedule_id == schedule_id:
                    active_list.append({
                        "id": recording_id,
                        "recording_id": recording_id,
                        "file_path": recording.file_path,
                        "start_time": recording.start_time.isoformat() if recording.start_time else None,
                        "status": recording.status,
                        "schedule_id": recording.schedule_id,
                        "task_running": not task.done()
                    })
            
            return active_list
            
        except Exception as e:
            logger.error(f"Error getting active recordings for schedule {schedule_id}: {e}")
            return []
    
    async def stop_all_recordings(self) -> bool:
        """Stop all active recordings"""
        try:
            recording_ids = list(self._active_recordings.keys())
            
            for recording_id in recording_ids:
                await self.stop_recording(recording_id)
            
            logger.info(f"Stopped {len(recording_ids)} recordings")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping all recordings: {e}")
            return False
    
    def is_recording_active(self, recording_id: int) -> bool:
        """Check if a recording is currently active"""
        return recording_id in self._active_recordings
    
    async def is_schedule_recording_active(self, schedule_id: int) -> bool:
        """Check if any recording for a schedule is currently active"""
        try:
            # Check database for active recordings for this schedule
            result = await self.db.execute(
                select(Recording).where(
                    Recording.schedule_id == schedule_id,
                    Recording.status.in_(["recording", "pending"])
                )
            )
            active_recordings = result.scalars().all()
            
            # Also check if any of these recordings are in our active recordings dict
            for recording in active_recordings:
                if recording.id in self._active_recordings:
                    return True
            
            return len(active_recordings) > 0
            
        except Exception as e:
            logger.error(f"Error checking if schedule {schedule_id} has active recordings: {e}")
            return False
    
    def _get_streamlink_path(self) -> str:
        """Get the path to streamlink executable"""
        import sys
        import shutil
        from app.core.config import settings
        
        logger.info(f"Looking for streamlink executable...")
        logger.info(f"Python executable: {sys.executable}")
        logger.info(f"Configured STREAMLINK_PATH: {getattr(settings, 'STREAMLINK_PATH', 'Not set')}")
        
        # First try the configured path
        if hasattr(settings, 'STREAMLINK_PATH') and settings.STREAMLINK_PATH:
            logger.info(f"Checking configured path: {settings.STREAMLINK_PATH}")
            if shutil.which(settings.STREAMLINK_PATH):
                logger.info(f"Found streamlink at configured path: {settings.STREAMLINK_PATH}")
                return settings.STREAMLINK_PATH
            else:
                logger.warning(f"Configured path not found: {settings.STREAMLINK_PATH}")
        
        # Try to find streamlink in various locations
        possible_paths = [
            "streamlink",  # System PATH
            os.path.join(os.path.dirname(sys.executable), "streamlink"),  # Same dir as Python
            os.path.join(os.path.dirname(sys.executable), "bin", "streamlink"),  # Unix venv
            "/usr/local/bin/streamlink",  # Common system location
            "/usr/bin/streamlink",  # System location
        ]
        
        logger.info(f"Searching in possible paths: {possible_paths}")
        
        for path in possible_paths:
            logger.info(f"Checking path: {path}")
            found_path = shutil.which(path)
            if found_path:
                logger.info(f"Found streamlink at: {found_path}")
                return found_path
            else:
                logger.info(f"Not found at: {path}")
        
        # Fallback to configured path even if not found
        fallback_path = getattr(settings, 'STREAMLINK_PATH', 'streamlink')
        logger.warning(f"No streamlink found, using fallback: {fallback_path}")
        return fallback_path
