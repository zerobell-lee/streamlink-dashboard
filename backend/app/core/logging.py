"""
Advanced Logging Configuration for Streamlink Dashboard
Provides file-based logging with categorization, rotation, and filtering
"""
import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path

from app.core.config import settings


class CategoryFilter(logging.Filter):
    """Filter logs based on category patterns"""
    
    def __init__(self, category: str, include_patterns: list = None, exclude_patterns: list = None):
        super().__init__()
        self.category = category
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
    
    def filter(self, record):
        """Filter log records based on patterns"""
        logger_name = record.name.lower()
        message = record.getMessage().lower()
        
        # Exclude patterns (highest priority)
        for pattern in self.exclude_patterns:
            if pattern.lower() in logger_name or pattern.lower() in message:
                return False
        
        # Include patterns (if specified)
        if self.include_patterns:
            for pattern in self.include_patterns:
                if pattern.lower() in logger_name or pattern.lower() in message:
                    return True
            return False
        
        return True


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'platform'):
            log_data['platform'] = record.platform
        if hasattr(record, 'streamer'):
            log_data['streamer'] = record.streamer
            
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_data, ensure_ascii=False)


class LoggingConfig:
    """Advanced logging configuration manager"""
    
    # Log categories and their patterns
    CATEGORIES = {
        "app": {
            "include_patterns": ["app.", "main", "streamlink"],
            "exclude_patterns": ["sqlalchemy", "uvicorn.access"]
        },
        "database": {
            "include_patterns": ["sqlalchemy"],
            "exclude_patterns": []
        },
        "api": {
            "include_patterns": ["uvicorn.access", "fastapi", "api."],
            "exclude_patterns": []
        },
        "scheduler": {
            "include_patterns": ["scheduler", "apscheduler"],
            "exclude_patterns": []
        },
        "error": {
            "include_patterns": [],
            "exclude_patterns": [],
            "min_level": "ERROR"
        }
    }
    
    def __init__(self):
        self.logs_dir = Path(settings.LOGS_DIR)
        self.logs_dir.mkdir(exist_ok=True)
        self.handlers: Dict[str, logging.Handler] = {}
        
    def create_file_handler(self, category: str, level: str = "INFO") -> logging.Handler:
        """Create a rotating file handler for a category"""
        log_file = self.logs_dir / f"{category}.log"
        
        # Create rotating file handler (50MB max, keep 10 files)
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10,
            encoding='utf-8'
        )
        
        # Set formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        handler.setLevel(getattr(logging, level.upper()))
        
        # Add category filter
        if category in self.CATEGORIES:
            cat_config = self.CATEGORIES[category]
            category_filter = CategoryFilter(
                category,
                cat_config.get("include_patterns"),
                cat_config.get("exclude_patterns")
            )
            handler.addFilter(category_filter)
            
            # Set minimum level for error category
            if category == "error":
                handler.setLevel(logging.ERROR)
        
        return handler
    
    def create_json_handler(self, category: str, level: str = "INFO") -> logging.Handler:
        """Create a JSON formatted file handler"""
        log_file = self.logs_dir / f"{category}.json"
        
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=50 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        
        handler.setFormatter(JSONFormatter())
        handler.setLevel(getattr(logging, level.upper()))
        
        # Add category filter
        if category in self.CATEGORIES:
            cat_config = self.CATEGORIES[category]
            category_filter = CategoryFilter(
                category,
                cat_config.get("include_patterns"),
                cat_config.get("exclude_patterns")
            )
            handler.addFilter(category_filter)
        
        return handler
    
    def setup_database_logging(self):
        """Configure database logging to reduce noise"""
        # Reduce SQLAlchemy logging verbosity
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
        
        # Only show SQL statements in DEBUG mode
        if settings.DEBUG and settings.LOG_LEVEL.upper() == "DEBUG":
            logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    
    def setup_logging(self, 
                     enable_file_logging: bool = True,
                     enable_json_logging: bool = False,
                     log_level: str = "INFO",
                     categories: Optional[Dict[str, bool]] = None) -> None:
        """Setup comprehensive logging system"""
        
        # Default categories
        if categories is None:
            categories = {cat: True for cat in self.CATEGORIES.keys()}
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers to avoid duplicates
        root_logger.handlers.clear()
        
        # Always add console handler with reduced verbosity
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        
        # Filter console output to reduce noise
        console_filter = CategoryFilter(
            "console",
            exclude_patterns=["sqlalchemy.engine", "uvicorn.access"] if log_level.upper() != "DEBUG" else []
        )
        console_handler.addFilter(console_filter)
        root_logger.addHandler(console_handler)
        
        # Add file handlers for each enabled category
        if enable_file_logging:
            for category, enabled in categories.items():
                if not enabled:
                    continue
                    
                # Create file handler
                file_handler = self.create_file_handler(category, log_level)
                root_logger.addHandler(file_handler)
                self.handlers[f"file_{category}"] = file_handler
                
                # Create JSON handler if enabled
                if enable_json_logging:
                    json_handler = self.create_json_handler(category, log_level)
                    root_logger.addHandler(json_handler)
                    self.handlers[f"json_{category}"] = json_handler
        
        # Setup database logging configuration
        self.setup_database_logging()
        
        # Log configuration summary
        enabled_cats = [cat for cat, enabled in categories.items() if enabled]
        logging.info(f"Logging system initialized - Level: {log_level}, Categories: {enabled_cats}")
        if enable_file_logging:
            logging.info(f"File logging enabled - Directory: {self.logs_dir}")
        if enable_json_logging:
            logging.info("JSON logging enabled for structured analysis")
    
    def get_log_files(self) -> Dict[str, Dict[str, Any]]:
        """Get information about existing log files"""
        log_files = {}
        
        for log_file in self.logs_dir.glob("*.log"):
            try:
                stat = log_file.stat()
                log_files[log_file.name] = {
                    "path": str(log_file),
                    "size": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "exists": True
                }
            except Exception as e:
                log_files[log_file.name] = {
                    "path": str(log_file),
                    "error": str(e),
                    "exists": False
                }
        
        return log_files
    
    def clean_old_logs(self, max_age_days: int = 30):
        """Clean up old log files"""
        import time
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        cleaned_files = []
        
        for log_file in self.logs_dir.glob("*.log*"):
            try:
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    cleaned_files.append(str(log_file))
            except Exception as e:
                logging.warning(f"Could not clean log file {log_file}: {e}")
        
        if cleaned_files:
            logging.info(f"Cleaned {len(cleaned_files)} old log files")
        
        return cleaned_files


# Global logging configuration instance
logging_config = LoggingConfig()


def setup_logging(enable_file_logging: bool = True,
                 enable_json_logging: bool = False,
                 log_level: str = None,
                 categories: Optional[Dict[str, bool]] = None):
    """Setup application logging"""
    if log_level is None:
        log_level = settings.LOG_LEVEL
    
    logging_config.setup_logging(
        enable_file_logging=enable_file_logging,
        enable_json_logging=enable_json_logging,
        log_level=log_level,
        categories=categories
    )


def get_category_logger(category: str, extra_context: Optional[Dict] = None):
    """Get a logger with category-specific context"""
    logger = logging.getLogger(f"app.{category}")
    
    if extra_context:
        # Create adapter for extra context
        return logging.LoggerAdapter(logger, extra_context)
    
    return logger


# Convenience functions for common logging scenarios
def log_api_request(method: str, path: str, user_id: Optional[str] = None, status_code: Optional[int] = None):
    """Log API request with structured data"""
    logger = get_category_logger("api")
    extra = {"request_method": method, "request_path": path}
    if user_id:
        extra["user_id"] = user_id
    if status_code:
        extra["status_code"] = status_code
    
    logger.info(f"{method} {path}" + (f" -> {status_code}" if status_code else ""), extra=extra)


def log_recording_event(event: str, platform: str, streamer: str, **kwargs):
    """Log recording-related events with context"""
    logger = get_category_logger("app")
    extra = {"platform": platform, "streamer": streamer, **kwargs}
    
    logger.info(f"Recording {event}: {platform}/{streamer}", extra=extra)


def log_scheduler_event(event: str, job_id: Optional[str] = None, **kwargs):
    """Log scheduler events with context"""
    logger = get_category_logger("scheduler")
    extra = {"event": event}
    if job_id:
        extra["job_id"] = job_id
    extra.update(kwargs)
    
    logger.info(f"Scheduler {event}" + (f" (job: {job_id})" if job_id else ""), extra=extra)