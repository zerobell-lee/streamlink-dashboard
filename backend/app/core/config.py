"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Streamlink Dashboard"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
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
