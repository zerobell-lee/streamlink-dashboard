"""
API v1 router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import recordings, schedules, platforms, users, system, scheduler, auth, logs

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(recordings.router, prefix="/recordings", tags=["recordings"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(platforms.router, prefix="/platforms", tags=["platforms"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(scheduler.router, prefix="/scheduler", tags=["scheduler"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
