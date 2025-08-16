"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Streamlink Dashboard"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./streamlink_dashboard.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # File Storage
    RECORDINGS_DIR: str = "./recordings"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024 * 1024  # 10GB
    
    # Streamlink
    STREAMLINK_PATH: str = "streamlink"
    DEFAULT_QUALITY: str = "best"
    
    # Scheduler
    SCHEDULER_TIMEZONE: str = "UTC"
    SCHEDULER_MAX_INSTANCES: int = 1
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Basic Auth (for internal network)
    BASIC_AUTH_USERNAME: str = "admin"
    BASIC_AUTH_PASSWORD: str = "admin123"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure recordings directory exists
os.makedirs(settings.RECORDINGS_DIR, exist_ok=True)
