# Streamlink Dashboard - Architecture Documentation

## System Architecture Overview

Streamlink Dashboard is designed based on a modular microservice architecture. Each component operates independently while collaborating to form the complete system.

## Core Components

### 1. Web Dashboard (Frontend)
- **Technology**: React + TypeScript
- **Role**: User interface provision
- **Key Features**:
  - File Explorer style recording file management
  - Real-time recording status monitoring
  - Schedule management and configuration
  - Favorites system

### 2. API Gateway (Backend)
- **Technology**: FastAPI + Python
- **Role**: Entry point for all requests
- **Key Features**:
  - RESTful API provision
  - Basic authentication and authorization
  - Request routing and load balancing

### 3. Scheduler Service
- **Technology**: APScheduler + Python
- **Role**: Recording job scheduling
- **Key Features**:
  - Streamer online status monitoring
  - Automatic recording job start/stop
  - Job status management

### 4. Streamlink Engine
- **Technology**: Streamlink + Python
- **Role**: Actual streaming recording execution
- **Key Features**:
  - Platform-specific stream URL acquisition
  - Real-time stream download
  - Recording quality and format management

### 5. Platform Strategy Layer
- **Technology**: Strategy Pattern + Python
- **Role**: Platform-specific stream information acquisition
- **Key Features**:
  - Platform-specific API integration
  - Stream URL extraction logic
  - Platform-specific authentication handling

### 6. File Management Service
- **Technology**: Python + SQLite
- **Role**: File system and metadata management
- **Key Features**:
  - Recording file storage and management
  - Metadata database management
  - Automatic cleanup (Rotation) system

### 7. Configuration Management Service
- **Technology**: Python + SQLite
- **Role**: Dynamic configuration management
- **Key Features**:
  - Database-based configuration storage
  - Runtime configuration updates
  - Web interface for configuration management

## Database Design

### SQLite Schema

```sql
-- Scheduled recording jobs
CREATE TABLE recording_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform VARCHAR(50) NOT NULL,
    streamer_name VARCHAR(100) NOT NULL,
    streamer_id VARCHAR(100),
    quality VARCHAR(20) DEFAULT 'best',
    output_path VARCHAR(500),
    streamlink_args TEXT,
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recorded file information
CREATE TABLE recordings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id INTEGER,
    platform VARCHAR(50) NOT NULL,
    streamer_name VARCHAR(100) NOT NULL,
    title VARCHAR(500),
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    duration INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    quality VARCHAR(20),
    is_favorite BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (schedule_id) REFERENCES recording_schedules(id)
);

-- Platform-specific configurations
CREATE TABLE platform_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform VARCHAR(50) UNIQUE NOT NULL,
    api_key VARCHAR(500),
    api_secret VARCHAR(500),
    base_url VARCHAR(200),
    config_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System configurations (database-based)
CREATE TABLE system_configs (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    description VARCHAR(500),
    category VARCHAR(50) DEFAULT 'general',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User authentication (Basic Auth)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recording job status
CREATE TABLE recording_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (schedule_id) REFERENCES recording_schedules(id)
);
```

## Platform Strategy Pattern Implementation

### Base Interface

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class PlatformStrategy(ABC):
    @abstractmethod
    def get_stream_url(self, streamer_id: str) -> Optional[str]:
        """Returns the current live stream URL for the streamer"""
        pass
    
    @abstractmethod
    def is_live(self, streamer_id: str) -> bool:
        """Checks if the streamer is currently live"""
        pass
    
    @abstractmethod
    def get_stream_info(self, streamer_id: str) -> Dict[str, Any]:
        """Returns stream information (title, viewer count, etc.)"""
        pass
    
    @abstractmethod
    def get_streamlink_args(self) -> list:
        """Returns platform-specific Streamlink arguments"""
        pass
```

### Platform-specific Implementation Examples

```python
class TwitchStrategy(PlatformStrategy):
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_base = "https://api.twitch.tv/helix"
    
    def get_stream_url(self, streamer_id: str) -> Optional[str]:
        # Stream URL acquisition through Twitch API
        pass
    
    def is_live(self, streamer_id: str) -> bool:
        # Live status check through Twitch API
        pass
    
    def get_stream_info(self, streamer_id: str) -> Dict[str, Any]:
        # Return stream title, viewer count, etc.
        pass
    
    def get_streamlink_args(self) -> list:
        return [
            "--twitch-disable-hosting",
            "--twitch-disable-ads",
            "--twitch-low-latency"
        ]

class YouTubeStrategy(PlatformStrategy):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_base = "https://www.googleapis.com/youtube/v3"
    
    def get_stream_url(self, streamer_id: str) -> Optional[str]:
        # Stream URL acquisition through YouTube Data API
        pass
    
    def is_live(self, streamer_id: str) -> bool:
        # Live status check through YouTube Data API
        pass
    
    def get_stream_info(self, streamer_id: str) -> Dict[str, Any]:
        # Return stream information
        pass
    
    def get_streamlink_args(self) -> list:
        return [
            "--youtube-live-from-start",
            "--youtube-live-chunk-time"
        ]
```

## File Management and Rotation System

### Rotation Policy

```python
class RotationPolicy:
    def __init__(self, config: Dict[str, Any]):
        self.time_based = config.get('time_based', {})
        self.count_based = config.get('count_based', {})
        self.size_based = config.get('size_based', {})
        self.preserve_favorites = config.get('preserve_favorites', True)
    
    def should_delete_file(self, recording: Dict[str, Any]) -> bool:
        # Preserve favorite files
        if self.preserve_favorites and recording.get('is_favorite'):
            return False
        
        # Time-based policy
        if self.time_based.get('enabled'):
            days_old = (datetime.now() - recording['created_at']).days
            if days_old > self.time_based.get('days', 30):
                return True
        
        return False
    
    def get_files_to_delete(self, recordings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Return list of files to delete based on policy
        pass
```

## Authentication System

### Basic Authentication Implementation

```python
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import hashlib
import secrets

security = HTTPBasic()

class BasicAuthService:
    def __init__(self, db_service):
        self.db_service = db_service
    
    def verify_credentials(self, credentials: HTTPBasicCredentials) -> bool:
        """Verify username and password"""
        user = self.db_service.get_user_by_username(credentials.username)
        if not user:
            return False
        
        # Verify password hash
        password_hash = hashlib.sha256(credentials.password.encode()).hexdigest()
        return user.password_hash == password_hash
    
    def get_current_user(self, credentials: HTTPBasicCredentials = Depends(security)):
        """Get current authenticated user"""
        if not self.verify_credentials(credentials):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials.username
```

## Configuration Management

### Database-based Configuration Service

```python
class ConfigurationService:
    def __init__(self, db_service):
        self.db_service = db_service
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value from database"""
        config = self.db_service.get_system_config(key)
        return config.value if config else default
    
    def set_config(self, key: str, value: Any, description: str = None, category: str = "general"):
        """Set configuration value in database"""
        self.db_service.set_system_config(key, value, description, category)
    
    def get_configs_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all configurations for a specific category"""
        return self.db_service.get_system_configs_by_category(category)
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all configurations organized by category"""
        configs = self.db_service.get_all_system_configs()
        organized = {}
        for config in configs:
            if config.category not in organized:
                organized[config.category] = {}
            organized[config.category][config.key] = config.value
        return organized
```

## API Design

### RESTful API Endpoints

```
GET    /api/schedules          # Get schedule list
POST   /api/schedules          # Create new schedule
PUT    /api/schedules/{id}     # Update schedule
DELETE /api/schedules/{id}     # Delete schedule

GET    /api/recordings         # Get recording file list
GET    /api/recordings/{id}    # Get recording file details
DELETE /api/recordings/{id}    # Delete recording file
POST   /api/recordings/{id}/favorite  # Toggle favorite

GET    /api/status             # Get system status
GET    /api/status/live        # Get currently recording jobs

GET    /api/platforms          # Get supported platforms list
GET    /api/platforms/{name}/config  # Get platform configuration
PUT    /api/platforms/{name}/config  # Update platform configuration

GET    /api/config             # Get system configurations
PUT    /api/config             # Update system configurations
GET    /api/config/categories  # Get configuration categories

GET    /api/auth/status        # Get authentication status
POST   /api/auth/logout        # Logout (for session management)
```

### WebSocket Events

```javascript
// Real-time status updates
socket.on('recording_started', (data) => {
    // Recording started notification
});

socket.on('recording_finished', (data) => {
    // Recording finished notification
});

socket.on('recording_error', (data) => {
    // Recording error notification
});

socket.on('schedule_updated', (data) => {
    // Schedule change notification
});

socket.on('config_updated', (data) => {
    // Configuration change notification
});
```

## Security Considerations

### Authentication and Authorization
- Basic authentication for internal network access
- Password hashing using SHA-256
- Session management for web interface
- API key management (platform-specific)

### Data Protection
- Sensitive information encrypted storage
- API keys and secrets stored in database
- Log file sanitization for sensitive information

### File System Security
- File upload validation
- Path traversal attack prevention
- File access permission control

## Performance Optimization

### Caching Strategy
- In-memory caching for frequently accessed configurations
- Stream status caching to reduce API calls
- Browser caching optimization

### Database Optimization
- Index optimization
- Query optimization
- Connection pooling

### Asynchronous Processing
- Background job processing with APScheduler
- Asynchronous file I/O
- Event-driven architecture

## Monitoring and Logging

### Logging System
- Structured logging (JSON format)
- Log level management
- Log rotation

### Monitoring
- System resource monitoring
- API response time measurement
- Error rate tracking
- Recording success rate monitoring

### Notification System
- Email notifications
- Webhook notifications
- Telegram bot integration

## NAS Environment Considerations

### Synology NAS Specific
- Volume path mapping (`/volume1/recordings`)
- Docker container management through DSM
- Resource limitations and optimization
- Backup and restore procedures

### Container Management
- Single container deployment
- Volume mounting for persistent data
- Environment variable management
- Log management through Docker commands

### Configuration Management
- Database-based configuration for easy updates
- Web interface for configuration changes
- No container recreation required for settings changes
- Backup and restore of configuration data
