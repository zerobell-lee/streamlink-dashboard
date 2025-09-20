"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import logging
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Streamlink Dashboard"
    DEBUG: bool = True
    VERSION: str = os.getenv("VERSION", "0.5.0")

    APP_DATA_DIR: str = os.getenv("APP_DATA_DIR", "/app/app_data")
    
    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{APP_DATA_DIR}/database/streamlink_dashboard.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"]
    
    # File Storage
    
    RECORDINGS_DIR: str = f"{APP_DATA_DIR}/recordings"
    LOGS_DIR: str = f"{APP_DATA_DIR}/logs"
    CONFIG_DIR: str = f"{APP_DATA_DIR}/config"
    
    # Streamlink
    STREAMLINK_PATH: str = "streamlink"
    DEFAULT_QUALITY: str = "best"
    
    # Scheduler
    SCHEDULER_TIMEZONE: str = "UTC"
    SCHEDULER_MAX_INSTANCES: int = 1
    AUTO_START_SCHEDULER: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Advanced Logging Configuration
    ENABLE_FILE_LOGGING: bool = True
    ENABLE_JSON_LOGGING: bool = False
    LOG_MAX_FILES_PER_CATEGORY: int = 10
    LOG_MAX_FILE_SIZE_MB: int = 50
    LOG_RETENTION_DAYS: int = 30
    
    # Log Categories (enabled by default)
    LOG_CATEGORY_APP: bool = True
    LOG_CATEGORY_DATABASE: bool = True  
    LOG_CATEGORY_API: bool = True
    LOG_CATEGORY_SCHEDULER: bool = True
    LOG_CATEGORY_ERROR: bool = True
    
    # Basic Auth (for internal network)
    BASIC_AUTH_USERNAME: str = "admin"
    BASIC_AUTH_PASSWORD: str = "admin123"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


def ensure_app_directories() -> None:
    """
    Ensure all required application directories exist.
    This function creates all necessary directories for the application to function properly,
    including database, recordings, logs, and config directories.
    """
    # List of all required directories
    required_directories = [
        settings.APP_DATA_DIR,
        settings.RECORDINGS_DIR,
        settings.LOGS_DIR,
        settings.CONFIG_DIR,
        f"{settings.APP_DATA_DIR}/database"  # Explicit database directory
    ]
    
    for directory in required_directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logging.info(f"Ensured directory exists: {directory}")
        except PermissionError as e:
            error_msg = f"Failed to create directory {directory}: Permission denied - {e}"
            logging.error(error_msg)
            raise RuntimeError(error_msg) from e
        except OSError as e:
            error_msg = f"Failed to create directory {directory}: {e}"
            logging.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    logging.info("All required application directories have been ensured")


# Initialize directories on module import
ensure_app_directories()
