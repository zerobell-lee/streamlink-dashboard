"""
Scheduler service for managing automated recording schedules (Repository Pattern Version)
"""
import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.database.models import RecordingSchedule, Recording
from app.repositories.unit_of_work import AsyncSQLAlchemyUnitOfWork
from app.services.platform_service import PlatformService
from app.services.recording_service import RecordingService
from app.core.config import settings

logger = logging.getLogger(__name__)


class SchedulerServiceV2:
    """Service for managing automated recording schedules using Repository pattern"""

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self._monitoring_tasks: Dict[int, asyncio.Task] = {}
        self._monitoring_interval = 60  # 60초마다 체크
        self.recordings_dir = settings.RECORDINGS_DIR

    async def start(self):
        """Start the scheduler"""
        # Load existing schedules from database
        await self._load_schedules()

        # Start file size monitoring task
        self._file_size_task = asyncio.create_task(self._monitor_recording_file_sizes())

        # Start rotation cleanup task (runs every 10 minutes)
        self._rotation_task = asyncio.create_task(self._periodic_rotation_cleanup())

        logger.info("Scheduler started successfully")

    async def stop(self):
        """Stop the scheduler"""
        # Cancel file size monitoring task
        if hasattr(self, '_file_size_task'):
            self._file_size_task.cancel()

        # Cancel rotation cleanup task
        if hasattr(self, '_rotation_task'):
            self._rotation_task.cancel()

        # Cancel all monitoring tasks
        for task in self._monitoring_tasks.values():
            task.cancel()

        # Wait for tasks to complete
        all_tasks = list(self._monitoring_tasks.values())
        if hasattr(self, '_file_size_task'):
            all_tasks.append(self._file_size_task)
        if hasattr(self, '_rotation_task'):
            all_tasks.append(self._rotation_task)

        if all_tasks:
            await asyncio.gather(*all_tasks, return_exceptions=True)

        self._monitoring_tasks.clear()
        logger.info("Scheduler stopped")

    async def _load_schedules(self):
        """Load all enabled schedules from database"""
        try:
            async with AsyncSQLAlchemyUnitOfWork(self.session_factory) as uow:
                schedules = await uow.schedules.get_all_enabled()

                for schedule in schedules:
                    await self._start_monitoring(schedule)

                logger.info(f"Loaded {len(schedules)} schedules from database")

        except Exception as e:
            logger.error(f"Error loading schedules: {e}")

    async def _start_monitoring(self, schedule: RecordingSchedule):
        """Start monitoring a schedule"""
        try:
            # Cancel existing monitoring task if exists
            if schedule.id in self._monitoring_tasks:
                self._monitoring_tasks[schedule.id].cancel()

            # Create new monitoring task
            task = asyncio.create_task(
                self._monitor_stream(schedule)
            )
            self._monitoring_tasks[schedule.id] = task

            logger.info(f"Started monitoring for schedule {schedule.id} ({schedule.platform}/{schedule.streamer_id})")

        except Exception as e:
            logger.error(f"Error starting monitoring for schedule {schedule.id}: {e}")

    async def run_rotation_cleanup(self):
        """Run periodic rotation cleanup"""
        try:
            async with AsyncSQLAlchemyUnitOfWork(self.session_factory) as uow:
                # Get all schedules with rotation enabled
                schedules = await uow.schedules.get_rotation_enabled()

                logger.info(f"Running rotation cleanup for {len(schedules)} schedules with rotation enabled")

                for schedule in schedules:
                    await self._apply_rotation_policy(uow, schedule)

                await uow.commit()

        except Exception as e:
            logger.error(f"Error during rotation cleanup: {e}")

    async def _apply_rotation_policy(self, uow: AsyncSQLAlchemyUnitOfWork, schedule: RecordingSchedule):
        """Apply rotation policy for a specific schedule"""
        try:
            # Get all completed recordings for this schedule, ordered by creation date (newest first)
            # Exclude currently recording files to prevent deletion of active recordings
            recordings = await uow.recordings.get_all_for_schedule(schedule.id)
            # Filter out recording status recordings
            recordings = [r for r in recordings if r.status != 'recording']

            if not recordings:
                logger.info(f"No completed recordings found for schedule {schedule.id}")
                return

            logger.info(f"Found {len(recordings)} completed recordings for schedule {schedule.id}")
            for rec in recordings:
                logger.info(f"  Recording: {rec.file_name}, status: {rec.status}, created: {rec.created_at}")

            files_to_delete = []

            if schedule.rotation_type == 'count':
                # Keep only the most recent max_count files
                if len(recordings) > schedule.max_count:
                    files_to_delete = recordings[schedule.max_count:]
                    logger.info(f"Schedule {schedule.id}: {len(recordings)} recordings, keeping {schedule.max_count}, deleting {len(files_to_delete)}")

            elif schedule.rotation_type == 'time':
                # Keep files newer than max_age_days
                cutoff_date = datetime.now() - timedelta(days=schedule.max_age_days)
                files_to_delete = [r for r in recordings if r.created_at < cutoff_date]
                logger.info(f"Schedule {schedule.id}: deleting {len(files_to_delete)} files older than {schedule.max_age_days} days")

            elif schedule.rotation_type == 'size':
                # Keep files until total size exceeds max_size_gb
                total_size = 0
                max_size_bytes = schedule.max_size_gb * 1024 * 1024 * 1024
                for i, recording in enumerate(recordings):
                    total_size += recording.file_size or 0
                    if total_size > max_size_bytes:
                        files_to_delete = recordings[i:]
                        break
                logger.info(f"Schedule {schedule.id}: total size {total_size/1024/1024/1024:.2f}GB, deleting {len(files_to_delete)} files")

            # Filter out favorites if protect_favorites is enabled
            original_count = len(files_to_delete)
            if schedule.protect_favorites:
                files_to_delete = [r for r in files_to_delete if not r.is_favorite]
                if len(files_to_delete) < original_count:
                    logger.info(f"Schedule {schedule.id}: protected {original_count - len(files_to_delete)} favorite files")

            # Delete files
            deleted_count = 0
            for recording in files_to_delete:
                try:
                    # Delete physical file
                    file_path = os.path.join(self.recordings_dir, recording.file_name)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Deleted file: {file_path}")
                    else:
                        logger.warning(f"File not found: {file_path}")

                    # Delete database record using repository
                    await uow.recordings.delete(recording.id)
                    deleted_count += 1

                except Exception as e:
                    logger.error(f"Error deleting recording {recording.id}: {e}")

            if deleted_count > 0:
                logger.info(f"Rotation cleanup for schedule {schedule.id}: deleted {deleted_count} files")
            else:
                logger.debug(f"No files to delete for schedule {schedule.id}")

        except Exception as e:
            logger.error(f"Error applying rotation policy for schedule {schedule.id}: {e}")

    async def _periodic_rotation_cleanup(self):
        """Periodically run rotation cleanup every 10 minutes"""
        try:
            while True:
                await asyncio.sleep(10)  # 10 seconds (for testing)
                await self.run_rotation_cleanup()
        except asyncio.CancelledError:
            logger.info("Rotation cleanup task cancelled")
        except Exception as e:
            logger.error(f"Error in periodic rotation cleanup: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def _monitor_recording_file_sizes(self):
        """Periodically update file sizes for active recordings"""
        import os

        try:
            while True:
                async with AsyncSQLAlchemyUnitOfWork(self.session_factory) as uow:
                    # Query only recordings with 'recording' status using repository
                    from sqlalchemy import select
                    result = await uow._session.execute(
                        select(Recording).where(Recording.status == "recording")
                    )
                    active_recordings = result.scalars().all()

                    updated_count = 0

                    for recording in active_recordings:
                        if recording.file_path and os.path.exists(recording.file_path):
                            try:
                                current_size = os.path.getsize(recording.file_path)

                                # Only update if file size has changed
                                if current_size != recording.file_size:
                                    recording.file_size = current_size

                                    # Also calculate duration
                                    if recording.start_time:
                                        duration_seconds = int((datetime.now() - recording.start_time).total_seconds())
                                        recording.duration = duration_seconds

                                    await uow.recordings.update(recording)
                                    updated_count += 1

                            except OSError:
                                # Skip if file is not accessible
                                continue

                    # Commit only if there are changes
                    if updated_count > 0:
                        await uow.commit()
                        logger.debug(f"Updated file sizes for {updated_count} active recordings")

                # Check every 10 seconds (not too frequent)
                await asyncio.sleep(10)

        except asyncio.CancelledError:
            logger.info("File size monitoring cancelled")
        except Exception as e:
            logger.error(f"Error monitoring file sizes: {e}")
            await asyncio.sleep(10)  # Wait even on error

    async def _monitor_stream(self, schedule: RecordingSchedule):
        """Monitor a stream for live status"""
        logger.info(f"Starting monitoring loop for schedule {schedule.id}")
        try:
            while True:
                try:
                    async with AsyncSQLAlchemyUnitOfWork(self.session_factory) as uow:
                        # Refresh schedule from database to get latest state
                        current_schedule = await uow.schedules.get_by_id(schedule.id)

                        # Check if schedule still exists and is enabled
                        if not current_schedule or not current_schedule.enabled:
                            logger.info(f"Schedule {schedule.id} disabled or deleted, stopping monitoring")
                            break

                        # Create recording service with UoW
                        recording_service = RecordingService(uow)

                        # First check if we're already recording (fast DB check using repository)
                        if not await recording_service.is_schedule_recording_active(current_schedule.id):
                            # Not recording, now check if stream is live (slower API call)
                            # Create platform service with same session
                            platform_service = PlatformService(uow._session)
                            stream_info = await platform_service.get_stream_info(
                                current_schedule.platform,
                                current_schedule.streamer_id
                            )

                            if stream_info and stream_info.is_live:
                                # Stream is live and we're not recording, start recording
                                await self._start_recording_with_uow(uow, current_schedule, stream_info, recording_service)
                                # Commit the recording creation
                                await uow.commit()

                    # Wait before next check
                    await asyncio.sleep(self._monitoring_interval)

                except Exception as e:
                    logger.error(f"Error monitoring stream for schedule {schedule.id}: {e}")
                    await asyncio.sleep(self._monitoring_interval)

        except asyncio.CancelledError:
            logger.info(f"Monitoring cancelled for schedule {schedule.id}")
        except Exception as e:
            logger.error(f"Error in monitoring loop for schedule {schedule.id}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

        logger.info(f"Monitoring loop ended for schedule {schedule.id}")

    async def _start_recording_with_uow(self, uow: AsyncSQLAlchemyUnitOfWork, schedule: RecordingSchedule, stream_info, recording_service: RecordingService):
        """Start recording for a schedule with Unit of Work"""
        try:
            # Import platform service and output filename template
            from app.services.platform_service import PlatformService
            from app.services.output_filename_template import OutputFileNameTemplate

            # Get platform definition to get default filename template
            platform_service = PlatformService(uow._session)
            platform_definition = platform_service.get_platform_definition(schedule.platform)

            # Use schedule's filename template or platform default
            filename_template = schedule.filename_template or platform_definition.default_filename_template

            # Generate filename using template engine
            template_engine = OutputFileNameTemplate(filename_template)
            filename = template_engine.generate_filename(
                streamer_id=schedule.streamer_id,
                platform=schedule.platform,
                quality=schedule.quality,
                streamer_name=schedule.streamer_name,
                title=f"{schedule.streamer_name} Stream",
                file_extension=schedule.output_format or platform_definition.default_output_format
            )

            # Create full output path
            output_path = f"{settings.RECORDINGS_DIR}/{filename}"

            # Create recording record using repository
            recording = Recording(
                schedule_id=schedule.id,
                file_path=output_path,
                file_name=filename,
                start_time=datetime.now(),
                status="recording",
                platform=schedule.platform,
                streamer_id=schedule.streamer_id,
                streamer_name=schedule.streamer_name,
                quality=schedule.quality
            )

            recording = await uow.recordings.create(recording)
            await uow.flush()  # Flush to get ID without committing

            logger.info(f"Started recording {recording.id} for schedule {schedule.id}")

            # Start recording using recording service
            success = await recording_service.start_recording(
                recording_id=recording.id,
                schedule_id=schedule.id,
                platform=schedule.platform,
                streamer_id=schedule.streamer_id,
                quality=schedule.quality,
                output_path=output_path
            )

            if not success:
                logger.error(f"Failed to start recording for schedule {schedule.id}")
                # Note: recording status is already updated by recording_service

        except Exception as e:
            logger.error(f"Error starting recording for schedule {schedule.id}: {e}")

    async def add_schedule(self, schedule: RecordingSchedule) -> bool:
        """Add a new schedule"""
        try:
            async with AsyncSQLAlchemyUnitOfWork(self.session_factory) as uow:
                # Save to database using repository
                schedule = await uow.schedules.create(schedule)
                await uow.commit()

                # Start monitoring if enabled
                if schedule.enabled:
                    await self._start_monitoring(schedule)

                logger.info(f"Added schedule {schedule.id}")
                return True

        except Exception as e:
            logger.error(f"Error adding schedule: {e}")
            return False

    async def update_schedule(self, schedule: RecordingSchedule) -> bool:
        """Update an existing schedule"""
        try:
            async with AsyncSQLAlchemyUnitOfWork(self.session_factory) as uow:
                # Update in database using repository
                await uow.schedules.update(schedule)
                await uow.commit()

                # Restart monitoring
                await self._start_monitoring(schedule)

                logger.info(f"Updated schedule {schedule.id}")
                return True

        except Exception as e:
            logger.error(f"Error updating schedule: {e}")
            return False

    async def stop_monitoring(self, schedule_id: int) -> bool:
        """Stop monitoring a schedule without deleting from database"""
        try:
            logger.info(f"=== stop_monitoring called for schedule {schedule_id} ===")

            # Stop monitoring task
            if schedule_id in self._monitoring_tasks:
                logger.info(f"Cancelling monitoring task for schedule {schedule_id}")
                self._monitoring_tasks[schedule_id].cancel()
                del self._monitoring_tasks[schedule_id]
                logger.info(f"Stopped monitoring for schedule {schedule_id}")
            else:
                logger.warning(f"No monitoring task found for schedule {schedule_id}")

            # Stop any active recordings for this schedule using repository
            logger.info(f"Checking active recordings for schedule {schedule_id}")

            async with AsyncSQLAlchemyUnitOfWork(self.session_factory) as uow:
                recording_service = RecordingService(uow)
                active_recordings = await recording_service.get_active_recordings()
                logger.info(f"Found {len(active_recordings)} total active recordings")

                # Filter by schedule_id
                schedule_recordings = []
                for rec in active_recordings:
                    logger.info(f"Active recording: {rec}")
                    if rec.get('schedule_id') == schedule_id:
                        schedule_recordings.append(rec)

                logger.info(f"Found {len(schedule_recordings)} active recordings for schedule {schedule_id}")

                if schedule_recordings:
                    logger.info(f"Stopping {len(schedule_recordings)} active recordings for schedule {schedule_id}")

                    for recording in schedule_recordings:
                        logger.info(f"Attempting to stop recording {recording['id']}")
                        success = await recording_service.stop_recording(recording['id'])
                        if success:
                            logger.info(f"Successfully stopped recording {recording['id']} for schedule {schedule_id}")
                        else:
                            logger.error(f"Failed to stop recording {recording['id']} for schedule {schedule_id}")
                else:
                    logger.warning(f"No active recordings found for schedule {schedule_id}")

            logger.info(f"=== stop_monitoring completed for schedule {schedule_id} ===")
            return True

        except Exception as e:
            logger.error(f"Error stopping monitoring for schedule {schedule_id}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    async def delete_schedule(self, schedule_id: int) -> bool:
        """Delete a schedule"""
        try:
            # Stop monitoring
            await self.stop_monitoring(schedule_id)

            async with AsyncSQLAlchemyUnitOfWork(self.session_factory) as uow:
                # Delete from database using repository
                success = await uow.schedules.delete(schedule_id)
                if success:
                    await uow.commit()

                logger.info(f"Deleted schedule {schedule_id}")
                return success

        except Exception as e:
            logger.error(f"Error deleting schedule {schedule_id}: {e}")
            return False

    async def get_schedule_status(self, schedule_id: int) -> Optional[Dict]:
        """Get status of a schedule"""
        try:
            # Check if monitoring task exists
            task = self._monitoring_tasks.get(schedule_id)

            if not task:
                logger.warning(f"No monitoring task found for schedule {schedule_id}")
                return None

            # Debug task state
            logger.debug(f"Task for schedule {schedule_id}: done={task.done()}, cancelled={task.cancelled()}")

            async with AsyncSQLAlchemyUnitOfWork(self.session_factory) as uow:
                # Get schedule info using repository
                schedule = await uow.schedules.get_by_id(schedule_id)

                if not schedule:
                    return None

                return {
                    "schedule_id": schedule_id,
                    "platform": schedule.platform,
                    "streamer_id": schedule.streamer_id,
                    "streamer_name": schedule.streamer_name,
                    "enabled": schedule.enabled,
                    "monitoring_active": not task.done(),
                    "last_check": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error getting schedule status for {schedule_id}: {e}")
            return None

    async def get_all_schedule_status(self) -> List[Dict]:
        """Get status of all schedules"""
        try:
            status_list = []

            for schedule_id in self._monitoring_tasks.keys():
                status = await self.get_schedule_status(schedule_id)
                if status:
                    status_list.append(status)

            return status_list

        except Exception as e:
            logger.error(f"Error getting all schedule status: {e}")
            return []

    async def trigger_check_now(self, schedule_id: int) -> bool:
        """Trigger an immediate stream check for a schedule"""
        try:
            async with AsyncSQLAlchemyUnitOfWork(self.session_factory) as uow:
                schedule = await uow.schedules.get_by_id(schedule_id)

                if not schedule:
                    logger.error(f"Schedule {schedule_id} not found")
                    return False

                # Create platform service
                platform_service = PlatformService(uow._session)

                # Check stream status immediately
                stream_info = await platform_service.get_stream_info(
                    schedule.platform,
                    schedule.streamer_id
                )

                if stream_info and stream_info.is_live:
                    recording_service = RecordingService(uow)
                    await self._start_recording_with_uow(uow, schedule, stream_info, recording_service)
                    return True
                else:
                    logger.info(f"Stream {schedule.streamer_id} is not live")
                    return False

        except Exception as e:
            logger.error(f"Error triggering check for schedule {schedule_id}: {e}")
            return False

    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return len(self._monitoring_tasks) > 0

    def get_scheduler_info(self) -> Dict:
        """Get scheduler information"""
        return {
            "running": self.is_running(),
            "monitoring_count": len(self._monitoring_tasks),
            "monitoring_interval_seconds": self._monitoring_interval
        }

    async def get_active_recordings(self) -> List[Dict]:
        """Get list of active recordings"""
        async with AsyncSQLAlchemyUnitOfWork(self.session_factory) as uow:
            recording_service = RecordingService(uow)
            return await recording_service.get_active_recordings()

    async def stop_all_recordings(self) -> bool:
        """Stop all active recordings"""
        async with AsyncSQLAlchemyUnitOfWork(self.session_factory) as uow:
            recording_service = RecordingService(uow)
            return await recording_service.stop_all_recordings()