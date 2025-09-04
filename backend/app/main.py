"""
Streamlink Dashboard - FastAPI Main Application
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from contextlib import asynccontextmanager
import uvicorn
from typing import Optional
import logging
import os
import httpx
import asyncio
import subprocess

from app.core.config import settings, ensure_app_directories

# Configure advanced logging system
from app.core.logging import setup_logging

# Setup logging with categories based on settings
categories = {
    "app": settings.LOG_CATEGORY_APP,
    "database": settings.LOG_CATEGORY_DATABASE,
    "api": settings.LOG_CATEGORY_API,  
    "scheduler": settings.LOG_CATEGORY_SCHEDULER,
    "error": settings.LOG_CATEGORY_ERROR
}

setup_logging(
    enable_file_logging=settings.ENABLE_FILE_LOGGING,
    enable_json_logging=settings.ENABLE_JSON_LOGGING,
    log_level=settings.LOG_LEVEL,
    categories=categories
)

from app.database.database import engine, get_db, AsyncSessionLocal
from app.database.models import Base
from app.core.auth import get_current_user
from app.api.v1.api import api_router
from app.services.scheduler_service import SchedulerService


# Global scheduler service instance
scheduler_service: Optional[SchedulerService] = None

# Create database tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global scheduler_service
    
    # Startup
    # Ensure all required directories exist before any database operations
    try:
        ensure_app_directories()
        logging.info("Directory initialization completed successfully")
    except Exception as e:
        logging.error(f"Failed to initialize directories: {e}")
        raise  # Critical error, should stop application startup
    
    try:
        async with engine.begin() as conn:
            # Create tables if they don't exist
            await conn.run_sync(Base.metadata.create_all)
        
        # Clean up orphaned recordings from previous server shutdown
        async with AsyncSessionLocal() as db:
            from app.database.models import Recording
            from sqlalchemy import select
            from datetime import datetime
            import os
            
            # Find recordings that are still in 'recording' status (orphaned from server shutdown)
            result = await db.execute(
                select(Recording).where(Recording.status == "recording")
            )
            orphaned_recordings = result.scalars().all()
            
            # Also find cancelled recordings that have actual files
            result_cancelled = await db.execute(
                select(Recording).where(Recording.status == "cancelled")
            )
            cancelled_recordings = result_cancelled.scalars().all()
            
            # Also check completed recordings with wrong file size (excluding active recordings)
            result_completed = await db.execute(
                select(Recording).where(Recording.status == "completed", Recording.file_size == 0)
            )
            completed_with_zero_size = result_completed.scalars().all()
            
            recovered_recordings = []
            
            # Process cancelled recordings
            for recording in cancelled_recordings:
                if recording.file_path and os.path.exists(recording.file_path):
                    try:
                        file_size = os.path.getsize(recording.file_path)
                        if file_size > 0:  # File exists and has content
                            recording.status = "completed"
                            recording.file_size = file_size
                            if not recording.end_time:
                                recording.end_time = datetime.now()
                            recovered_recordings.append(recording)
                    except OSError:
                        # File might be inaccessible, skip
                        continue
            
            # Process completed recordings with wrong file size
            for recording in completed_with_zero_size:
                if recording.file_path and os.path.exists(recording.file_path):
                    try:
                        file_size = os.path.getsize(recording.file_path)
                        if file_size > 0:  # File exists and has content
                            recording.file_size = file_size
                            recovered_recordings.append(recording)
                    except OSError:
                        # File might be inaccessible, skip
                        continue
            
            if orphaned_recordings:
                logging.warning(f"Found {len(orphaned_recordings)} orphaned recordings from previous shutdown")
                
                for recording in orphaned_recordings:
                    recording.status = "completed"
                    recording.end_time = datetime.now()
                    
                    # Update file size if file exists
                    if recording.file_path and os.path.exists(recording.file_path):
                        try:
                            file_size = os.path.getsize(recording.file_path)
                            recording.file_size = file_size
                            logging.info(f"Marked orphaned recording {recording.id} as completed (file size: {file_size} bytes)")
                        except OSError:
                            logging.info(f"Marked orphaned recording {recording.id} as completed (file not accessible)")
                    else:
                        logging.info(f"Marked orphaned recording {recording.id} as completed")
            
            if recovered_recordings:
                cancelled_count = sum(1 for r in recovered_recordings if r.status == "completed" and r.end_time)
                filesize_fix_count = len(recovered_recordings) - cancelled_count
                
                if cancelled_count > 0:
                    logging.warning(f"Found {cancelled_count} cancelled recordings with actual files")
                if filesize_fix_count > 0:
                    logging.warning(f"Found {filesize_fix_count} recordings with incorrect file size")
                
                for recording in recovered_recordings:
                    if recording.end_time and recording.end_time.year == datetime.now().year:  # Recently updated
                        logging.info(f"Recovered cancelled recording {recording.id} as completed (file size: {recording.file_size} bytes)")
                    else:
                        logging.info(f"Fixed file size for recording {recording.id} (file size: {recording.file_size} bytes)")
            
            if orphaned_recordings or recovered_recordings:
                await db.commit()
                total_recovered = len(orphaned_recordings) + len(recovered_recordings)
                logging.info(f"Marked {total_recovered} recordings as completed")
                
    except Exception as e:
        # In test environment, tables might already be created
        logging.warning(f"Could not create database tables: {e}")
    
    # Start Next.js server
    await start_nextjs()
    
    # Initialize scheduler service and create default data
    try:
        async with AsyncSessionLocal() as db:
            # Create default platform configurations
            from app.services.platform_service import PlatformService
            platform_service = PlatformService(db)
            await platform_service.create_default_configs()
            
            
            # Create default admin user if not exists
            from app.database.models import User
            from sqlalchemy import select
            result = await db.execute(select(User).where(User.username == "admin"))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                import hashlib
                password_hash = hashlib.sha256("admin123".encode()).hexdigest()
                admin_user = User(
                    username="admin",
                    password_hash=password_hash,
                    is_admin=True
                )
                db.add(admin_user)
                await db.commit()
                logging.info("Created default admin user (admin/admin123)")
            
            # Initialize scheduler
            scheduler_service = SchedulerService(db)
            if settings.AUTO_START_SCHEDULER:
                await scheduler_service.start()
                logging.info("Scheduler started automatically")
                
    except Exception as e:
        logging.warning(f"Could not initialize scheduler service: {e}")
    
    yield
    
    # Shutdown
    logging.info("Shutting down application...")
    
    # Stop Next.js server
    global nextjs_process
    if nextjs_process:
        try:
            nextjs_process.terminate()
            nextjs_process.wait(timeout=5)
            logging.info("Next.js server stopped")
        except Exception as e:
            logging.warning(f"Error stopping Next.js server: {e}")
            try:
                nextjs_process.kill()
            except:
                pass
    
    if scheduler_service:
        try:
            # Stop all active recordings first
            from app.services.streamlink_service import StreamlinkService
            async with AsyncSessionLocal() as db:
                streamlink_service = StreamlinkService(db)
                await streamlink_service.stop_all_recordings()
                logging.info("Stopped all active recordings")
            
            # Stop scheduler
            await scheduler_service.stop()
            logging.info("Scheduler stopped")
        except Exception as e:
            logging.warning(f"Error stopping scheduler: {e}")
    
    # Force kill any remaining subprocesses
    try:
        import psutil
        current_process = psutil.Process()
        children = current_process.children(recursive=True)
        
        for child in children:
            try:
                if "streamlink" in child.name().lower():
                    logging.info(f"Force killing streamlink process: {child.pid}")
                    child.kill()
            except Exception as e:
                logging.warning(f"Error killing process {child.pid}: {e}")
    except ImportError:
        logging.warning("psutil not available, cannot force kill subprocesses")
    except Exception as e:
        logging.warning(f"Error in subprocess cleanup: {e}")
    
    await engine.dispose()
    logging.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Streamlink Dashboard",
    description="A web-based dashboard for managing Streamlink recordings",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Security
security = HTTPBasic()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Request Logging Middleware
from app.core.logging import log_api_request
import time

@app.middleware("http")
async def log_requests(request, call_next):
    """Log API requests with response time and status"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Only log API requests (not frontend proxy requests)
    if request.url.path.startswith("/api/"):
        process_time = time.time() - start_time
        
        # Try to get user info from auth header
        user_id = None
        try:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # For now, just log that it's an authenticated request
                user_id = "authenticated"
        except Exception:
            pass
            
        # Log the API request
        log_api_request(
            method=request.method,
            path=request.url.path,
            user_id=user_id,
            status_code=response.status_code
        )
        
        # Also log response time if it's slow
        if process_time > 1.0:  # Log slow requests (>1 second)
            from app.core.logging import get_category_logger
            logger = get_category_logger("api")
            logger.warning(f"Slow API request: {request.method} {request.url.path} took {process_time:.2f}s")
    
    return response

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Proxy to Next.js standalone server

# Start Next.js server
nextjs_process = None

async def start_nextjs():
    global nextjs_process
    if os.path.exists("/app/frontend/server.js"):
        try:
            nextjs_process = subprocess.Popen(
                ["node", "server.js"],
                cwd="/app/frontend",
                env={**os.environ, "PORT": "3000", "HOSTNAME": "0.0.0.0"}
            )
            # Wait a bit for server to start
            await asyncio.sleep(2)
            logging.info("Next.js server started on port 3000")
        except Exception as e:
            logging.error(f"Failed to start Next.js server: {e}")

# Proxy non-API requests to Next.js
@app.middleware("http") 
async def proxy_to_nextjs(request, call_next):
    # Handle API requests normally
    if request.url.path.startswith("/api/") or request.url.path.startswith("/health"):
        return await call_next(request)
    
    # Proxy everything else to Next.js
    try:
        async with httpx.AsyncClient() as client:
            proxy_url = f"http://localhost:3000{request.url.path}"
            if request.url.query:
                proxy_url += f"?{request.url.query}"
            
            # Remove problematic headers
            headers = dict(request.headers)
            headers.pop("host", None)
            headers.pop("content-length", None)
            
            response = await client.request(
                method=request.method,
                url=proxy_url,
                headers=headers,
                content=await request.body()
            )
            
            # Filter response headers
            response_headers = dict(response.headers)
            response_headers.pop("content-length", None)
            response_headers.pop("transfer-encoding", None)
            response_headers.pop("content-encoding", None)
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers
            )
    except Exception as e:
        logging.error(f"Proxy error: {e}")
        return await call_next(request)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "streamlink-dashboard"}

# Serve React app for all non-API routes
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serve React app for all routes that don't start with /api"""
    # Skip API routes, docs, and health check
    if (full_path.startswith("api/") or 
        full_path.startswith("docs") or 
        full_path.startswith("redoc") or 
        full_path == "health"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Use absolute path for Docker container
    if os.path.exists("/app/frontend/build"):
        static_dir = "/app/frontend/build"
    else:
        # Fallback for local development
        static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "build")
    
    index_file = os.path.join(static_dir, "index.html")
    
    if os.path.exists(index_file):
        return FileResponse(index_file)
    else:
        return {
            "message": "Streamlink Dashboard API",
            "version": "1.0.0",
            "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
            "note": "Frontend not built. Run 'npm run build' in frontend directory."
        }

# Root endpoint - serve React app
@app.get("/")
async def root():
    """Root endpoint - serve React app"""
    # Use absolute path for Docker container
    if os.path.exists("/app/frontend/build"):
        static_dir = "/app/frontend/build"
    else:
        # Fallback for local development
        static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "build")
    
    index_file = os.path.join(static_dir, "index.html")
    
    if os.path.exists(index_file):
        return FileResponse(index_file)
    else:
        return {
            "message": "Streamlink Dashboard API",
            "version": "1.0.0",
            "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
            "note": "Frontend not built. Run 'npm run build' in frontend directory."
        }

# Simple scheduler status endpoint (no auth required)
@app.get("/scheduler-status")
async def scheduler_status():
    """Get basic scheduler status without authentication"""
    if scheduler_service:
        return {
            "scheduler_running": scheduler_service.is_running(),
            "scheduler_info": scheduler_service.get_scheduler_info()
        }
    else:
        return {
            "scheduler_running": False,
            "error": "Scheduler service not initialized"
        }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
