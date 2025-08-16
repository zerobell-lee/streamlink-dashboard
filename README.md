# Streamlink Dashboard

A web-based dashboard application for real-time streaming recording using Streamlink.

## Project Overview

Streamlink Dashboard is a web application that automatically records and manages live streams from various streaming platforms. Users can set up scheduled jobs to automatically record streams from their favorite streamers and manage recorded files through a web dashboard.

## Key Features

### 🎥 Real-time Streaming Recording
- **Streamlink-based**: Stable and efficient streaming recording
- **Multi-platform Support**: Twitch, YouTube, AfreecaTV, and other platforms
- **Platform-specific Customization**: Optimized Streamlink arguments for each platform

### 📅 Scheduling System
- **Automatic Recording Schedule**: Automatically detect and record streams from specified streamers
- **Platform Strategy Pattern**: Abstract stream URL acquisition methods for each platform
- **Flexible Configuration**: Recording time, quality, storage location, and detailed settings

### 🖥️ Web Dashboard
- **File Explorer Style UI**: Intuitive and familiar file management interface
- **Real-time Monitoring**: Live recording status and progress monitoring
- **File Management**: Basic functions for recorded files (play, download, delete)

### ⭐ Favorites System
- **Like/Favorite**: Mark important recorded files as favorites
- **Protection Feature**: Favorite files are excluded from automatic deletion

### 🔄 Automatic Management System
- **Rotation Settings**: Automatic file management based on various conditions
  - Time-based: Automatic deletion after specified period (e.g., 30 days)
  - Count-based: Maximum file count limit
  - Size-based: Maximum storage capacity limit
- **Smart Cleanup**: Preserve favorite files while removing unnecessary ones

### 🐳 Deployment & Infrastructure
- **Docker Support**: Containerized deployment environment
- **Lightweight Database**: Built-in DB without separate container
- **Extensible Architecture**: Modular structure for easy addition of new platforms

## Technology Stack

### Backend
- **Language**: Python
- **Web Framework**: FastAPI
- **Streaming**: Streamlink
- **Scheduler**: APScheduler
- **Database**: SQLite (Built-in DB)

### Frontend
- **Language**: TypeScript
- **Framework**: React
- **UI Library**: Material-UI
- **File Management**: Custom File Explorer component

### Infrastructure
- **Container**: Docker & Docker Compose
- **File System**: Local storage or network storage
- **Logging**: Structured logging system

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Dashboard │    │  Scheduler API  │    │  Streamlink     │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Engine        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File Storage  │    │   SQLite DB     │    │ Platform        │
│   (Recordings)  │    │   (Metadata)    │    │ Strategies      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Platform Support Strategy

### Abstraction Layer
- **Platform Interface**: Common interface that all platforms must implement
- **Strategy Pattern**: Stream URL acquisition strategy for each platform
- **Plugin System**: Plugin architecture for adding new platforms

### Supported Platforms
- **Twitch**: Stream information acquisition through official API
- **YouTube**: Using YouTube Data API
- **AfreecaTV**: Web scraping based approach
- **Other Platforms**: Extensible structure for additional support

## Configuration & Customization

### Streamlink Configuration
```yaml
platforms:
  twitch:
    streamlink_args:
      - "--twitch-disable-hosting"
      - "--twitch-disable-ads"
  youtube:
    streamlink_args:
      - "--youtube-live-from-start"
```

### Rotation Configuration
```yaml
rotation:
  time_based:
    enabled: true
    days: 30
  count_based:
    enabled: true
    max_files: 100
  size_based:
    enabled: true
    max_size_gb: 50
  preserve_favorites: true
```

## Development & Deployment

### Local Development Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

### Docker Deployment
```bash
# Build Docker image
docker build -t streamlink-dashboard .

# Run container
docker run -p 8080:8080 -v /recordings:/app/recordings streamlink-dashboard
```

### NAS Deployment (Synology)
```bash
# Pull and run on Synology NAS
docker run -d \
  --name streamlink-dashboard \
  -p 8080:8080 \
  -v /volume1/recordings:/app/recordings \
  -v /volume1/data:/app/data \
  streamlink-dashboard
```

## Authentication

### Basic Authentication
- **Simple Setup**: Username/password authentication for internal network access
- **No Complex Setup**: No need for external authentication services
- **Secure for Internal Use**: Suitable for home/office network environments

## Configuration Management

### Database-based Configuration
- **Dynamic Settings**: All configurations stored in SQLite database
- **No Container Recreation**: Change settings without rebuilding containers
- **Web Interface**: Manage all settings through the dashboard
- **NAS Friendly**: Perfect for Synology NAS environments

### Configuration Categories
- **Platform Settings**: API keys, stream quality, custom arguments
- **Recording Settings**: Storage paths, file naming, rotation policies
- **System Settings**: Log levels, scheduler intervals, notification settings
- **User Settings**: Dashboard preferences, favorite management

## Logging & Monitoring

### Docker-based Logging
```bash
# View application logs
docker logs streamlink-dashboard

# Follow logs in real-time
docker logs -f streamlink-dashboard

# View logs for specific time period
docker logs --since="2023-01-01T00:00:00" streamlink-dashboard

# View error logs only
docker logs streamlink-dashboard 2>&1 | grep ERROR
```

### Log Management
- **Structured Logging**: JSON format for easy parsing
- **Log Rotation**: Automatic log file rotation
- **Error Tracking**: Comprehensive error logging and monitoring

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
