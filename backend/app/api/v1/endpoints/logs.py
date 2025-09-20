"""
Enhanced Log Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import aiofiles

from app.database.database import get_db
from app.database.models import User
from app.core.auth import get_current_user
from app.core.logging import logging_config
from pydantic import BaseModel, validator

router = APIRouter()


class LogSearchRequest(BaseModel):
    """Request model for log search"""
    query: str = ""
    category: Optional[str] = None
    level: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = 1000

    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 10000:
            raise ValueError('Limit must be between 1 and 10000')
        return v


class LogStreamConfig(BaseModel):
    """Configuration for real-time log streaming"""
    categories: List[str] = []
    levels: List[str] = []
    include_patterns: List[str] = []
    exclude_patterns: List[str] = []


@router.get("/categories")
async def get_log_categories(
    current_user: User = Depends(get_current_user)
):
    """Get available log categories"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    return {
        "categories": list(logging_config.CATEGORIES.keys()),
        "category_info": logging_config.CATEGORIES
    }


@router.get("/files")
async def get_log_files_enhanced(
    current_user: User = Depends(get_current_user)
):
    """Get enhanced information about log files"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        log_files = logging_config.get_log_files()

        # Add additional metadata
        enhanced_files = {}
        for filename, info in log_files.items():
            if info.get('exists', False):
                file_path = Path(info['path'])

                # Count lines and estimate records
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        line_count = sum(1 for _ in f)

                    enhanced_files[filename] = {
                        **info,
                        "line_count": line_count,
                        "category": filename.split('.')[0],
                        "is_json": filename.endswith('.json'),
                        "can_search": True
                    }
                except Exception as e:
                    enhanced_files[filename] = {
                        **info,
                        "error": f"Could not read file: {str(e)}",
                        "can_search": False
                    }
            else:
                enhanced_files[filename] = info

        return {
            "log_files": enhanced_files,
            "logs_directory": str(logging_config.logs_dir),
            "total_files": len(enhanced_files)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get log files information: {str(e)}"
        )


@router.get("/files/{filename}/content")
async def get_log_file_content_paginated(
    filename: str,
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(100, ge=1, le=1000, description="Lines per page"),
    reverse: bool = Query(True, description="Show newest entries first"),
    current_user: User = Depends(get_current_user)
):
    """Get paginated log file content"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    log_file_path = logging_config.logs_dir / filename

    if not log_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log file '{filename}' not found"
        )

    # Security check
    if not str(log_file_path).startswith(str(logging_config.logs_dir)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        async with aiofiles.open(log_file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            lines = content.splitlines()

        total_lines = len(lines)

        # Reverse if needed (newest first)
        if reverse:
            lines = lines[::-1]

        # Calculate pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_lines = lines[start_idx:end_idx]

        # If reversed, we need to reverse back the page for proper order
        if reverse:
            page_lines = page_lines[::-1]

        total_pages = (total_lines + per_page - 1) // per_page

        return {
            "filename": filename,
            "total_lines": total_lines,
            "total_pages": total_pages,
            "current_page": page,
            "per_page": per_page,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "content": page_lines,
            "reversed": reverse
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read log file: {str(e)}"
        )


@router.post("/search")
async def search_logs(
    request: LogSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Search through log files with filters"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        results = []
        search_pattern = re.compile(request.query, re.IGNORECASE) if request.query else None

        # Determine which files to search
        search_files = []
        if request.category:
            # Search specific category
            for suffix in ['.log', '.json']:
                file_path = logging_config.logs_dir / f"{request.category}{suffix}"
                if file_path.exists():
                    search_files.append(file_path)
        else:
            # Search all log files
            search_files = list(logging_config.logs_dir.glob("*.log"))
            search_files.extend(list(logging_config.logs_dir.glob("*.json")))

        for log_file in search_files:
            try:
                async with aiofiles.open(log_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    lines = content.splitlines()

                for line_num, line in enumerate(lines, 1):
                    # Skip empty lines
                    if not line.strip():
                        continue

                    # Apply filters
                    if search_pattern and not search_pattern.search(line):
                        continue

                    # Parse log entry for additional filtering
                    log_entry = _parse_log_line(line, log_file.name)

                    # Filter by log level
                    if request.level and log_entry.get('level') != request.level.upper():
                        continue

                    # Filter by time range
                    if request.start_time or request.end_time:
                        entry_time = log_entry.get('timestamp')
                        if entry_time:
                            try:
                                if isinstance(entry_time, str):
                                    entry_time = datetime.fromisoformat(entry_time.replace('Z', '+00:00'))

                                if request.start_time and entry_time < request.start_time:
                                    continue
                                if request.end_time and entry_time > request.end_time:
                                    continue
                            except Exception:
                                # If timestamp parsing fails, include the entry
                                pass

                    results.append({
                        "file": log_file.name,
                        "line_number": line_num,
                        "content": line,
                        "parsed": log_entry
                    })

                    # Limit results
                    if len(results) >= request.limit:
                        break

                if len(results) >= request.limit:
                    break

            except Exception as e:
                # Log file read error, continue with other files
                continue

        return {
            "results": results,
            "total_found": len(results),
            "search_params": request.dict(),
            "truncated": len(results) >= request.limit
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/analytics")
async def get_log_analytics(
    hours: int = Query(24, ge=1, le=168, description="Hours to analyze"),
    current_user: User = Depends(get_current_user)
):
    """Get log analytics and statistics"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        analytics = {
            "time_range": {
                "start": cutoff_time.isoformat(),
                "end": datetime.now().isoformat(),
                "hours": hours
            },
            "by_level": {},
            "by_category": {},
            "by_hour": {},
            "error_patterns": [],
            "total_entries": 0
        }

        # Process all log files
        log_files = list(logging_config.logs_dir.glob("*.log"))
        log_files.extend(list(logging_config.logs_dir.glob("*.json")))

        for log_file in log_files:
            try:
                async with aiofiles.open(log_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    lines = content.splitlines()

                category = log_file.stem

                for line in lines:
                    if not line.strip():
                        continue

                    log_entry = _parse_log_line(line, log_file.name)
                    entry_time = log_entry.get('timestamp')

                    # Filter by time
                    if entry_time:
                        try:
                            if isinstance(entry_time, str):
                                entry_time = datetime.fromisoformat(entry_time.replace('Z', '+00:00'))

                            if entry_time < cutoff_time:
                                continue
                        except Exception:
                            continue

                    analytics["total_entries"] += 1

                    # Count by level
                    level = log_entry.get('level', 'UNKNOWN')
                    analytics["by_level"][level] = analytics["by_level"].get(level, 0) + 1

                    # Count by category
                    analytics["by_category"][category] = analytics["by_category"].get(category, 0) + 1

                    # Count by hour
                    if entry_time:
                        hour_key = entry_time.strftime('%Y-%m-%d %H:00')
                        analytics["by_hour"][hour_key] = analytics["by_hour"].get(hour_key, 0) + 1

                    # Collect error patterns
                    if level in ['ERROR', 'CRITICAL']:
                        message = log_entry.get('message', line)
                        if len(analytics["error_patterns"]) < 50:  # Limit error patterns
                            analytics["error_patterns"].append({
                                "timestamp": entry_time.isoformat() if entry_time else None,
                                "level": level,
                                "message": message[:200] + "..." if len(message) > 200 else message,
                                "category": category
                            })

            except Exception:
                continue

        return analytics

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics generation failed: {str(e)}"
        )


@router.websocket("/stream")
async def log_stream_websocket(
    websocket: WebSocket,
    categories: str = Query("", description="Comma-separated categories to monitor"),
    levels: str = Query("", description="Comma-separated log levels to include")
):
    """Real-time log streaming via WebSocket"""
    await websocket.accept()

    try:
        # Parse filter parameters
        category_filter = [c.strip() for c in categories.split(',') if c.strip()] if categories else []
        level_filter = [l.strip().upper() for l in levels.split(',') if l.strip()] if levels else []

        # Monitor log files for changes
        monitored_files = {}

        # Get initial file positions
        log_files = list(logging_config.logs_dir.glob("*.log"))
        for log_file in log_files:
            if log_file.exists():
                monitored_files[str(log_file)] = log_file.stat().st_size

        while True:
            try:
                # Check for file changes
                for file_path, last_size in list(monitored_files.items()):
                    log_file = Path(file_path)
                    if not log_file.exists():
                        continue

                    current_size = log_file.stat().st_size
                    if current_size > last_size:
                        # File has grown, read new content
                        try:
                            with open(log_file, 'r', encoding='utf-8') as f:
                                f.seek(last_size)
                                new_content = f.read()

                            monitored_files[file_path] = current_size

                            # Process new lines
                            for line in new_content.splitlines():
                                if not line.strip():
                                    continue

                                log_entry = _parse_log_line(line, log_file.name)

                                # Apply filters
                                category = log_file.stem
                                if category_filter and category not in category_filter:
                                    continue

                                level = log_entry.get('level', '')
                                if level_filter and level not in level_filter:
                                    continue

                                # Send to client
                                await websocket.send_json({
                                    "timestamp": datetime.now().isoformat(),
                                    "file": log_file.name,
                                    "category": category,
                                    "content": line,
                                    "parsed": log_entry
                                })

                        except Exception as e:
                            # Error reading file, continue monitoring
                            continue

                # Check for new files
                current_files = list(logging_config.logs_dir.glob("*.log"))
                for log_file in current_files:
                    file_path = str(log_file)
                    if file_path not in monitored_files and log_file.exists():
                        monitored_files[file_path] = log_file.stat().st_size

                # Wait before next check
                await asyncio.sleep(1)

            except Exception as e:
                await websocket.send_json({
                    "error": f"Monitoring error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
                await asyncio.sleep(5)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "error": f"Stream error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        except:
            pass


def _parse_log_line(line: str, filename: str) -> Dict[str, Any]:
    """Parse a log line to extract structured information"""
    try:
        # Try JSON parsing first
        if filename.endswith('.json'):
            return json.loads(line)

        # Parse standard log format: timestamp - name - level - message
        parts = line.split(' - ', 3)
        if len(parts) >= 4:
            timestamp_str, logger_name, level, message = parts
            try:
                # Try to parse timestamp
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                return {
                    "timestamp": timestamp.isoformat(),
                    "logger": logger_name,
                    "level": level,
                    "message": message
                }
            except ValueError:
                pass

        # Fallback: try to extract level from line
        level_match = re.search(r'\b(DEBUG|INFO|WARNING|ERROR|CRITICAL)\b', line)
        level = level_match.group(1) if level_match else 'INFO'

        return {
            "timestamp": None,
            "logger": None,
            "level": level,
            "message": line
        }

    except Exception:
        return {
            "timestamp": None,
            "logger": None,
            "level": "INFO",
            "message": line
        }