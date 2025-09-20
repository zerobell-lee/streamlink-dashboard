"""
Service Container for Dependency Injection
"""
import logging
from typing import Optional

from app.database.database import AsyncSessionLocal
from app.repositories.unit_of_work import AsyncSQLAlchemyUnitOfWork
from app.services.recording_service import RecordingService
from app.services.scheduler_service_v2 import SchedulerServiceV2

logger = logging.getLogger(__name__)


class ServiceContainer:
    """Container for managing service dependencies and lifecycle"""

    def __init__(self):
        self._scheduler_service: Optional[SchedulerServiceV2] = None
        self._session_factory = AsyncSessionLocal

    def get_session_factory(self):
        """Get database session factory"""
        return self._session_factory

    def get_uow_factory(self):
        """Get Unit of Work factory"""
        return lambda: AsyncSQLAlchemyUnitOfWork(self._session_factory)

    def get_recording_service(self, uow: AsyncSQLAlchemyUnitOfWork) -> RecordingService:
        """Get RecordingService instance with UoW"""
        return RecordingService(uow)

    def get_scheduler_service(self) -> SchedulerServiceV2:
        """Get SchedulerService singleton instance"""
        if self._scheduler_service is None:
            logger.info("Creating new SchedulerServiceV2 instance")
            self._scheduler_service = SchedulerServiceV2(self._session_factory)
        return self._scheduler_service

    async def start_services(self):
        """Start all services"""
        logger.info("Starting services in container")
        scheduler = self.get_scheduler_service()
        await scheduler.start()
        logger.info("All services started successfully")

    async def stop_services(self):
        """Stop all services"""
        logger.info("Stopping services in container")
        if self._scheduler_service:
            await self._scheduler_service.stop()
            self._scheduler_service = None
        logger.info("All services stopped successfully")


# Global service container instance
service_container = ServiceContainer()


def get_service_container() -> ServiceContainer:
    """Get the global service container"""
    return service_container