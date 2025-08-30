# Streamlink Dashboard

A web-based dashboard application for real-time streaming recording using Streamlink.

## Project Overview

Streamlink Dashboard is a web application that automatically records and manages live streams from various streaming platforms. Users can set up scheduled jobs to automatically record streams from their favorite streamers and manage recorded files through a web dashboard.

## Key Features

### 🎥 Real-time Streaming Recording
- **Streamlink-based**: Stable and efficient streaming recording
- **Multi-platform Support**: Twitch, YouTube, Sooplive, Chzzk(치지직)
- **Platform-specific Customization**: Optimized Streamlink arguments for each platform

### 📅 Scheduling System
- **APScheduler-based**: Robust job scheduling and management
- **Platform Strategy Pattern**: Extensible platform support with strategy pattern
- **Flexible Configuration**: Quality settings, custom arguments, and monitoring intervals
- **Automatic Stream Detection**: Periodic checks for live streams

### 🖥️ Web Dashboard
- **Modern React UI**: Built with Next.js 15 and Tailwind CSS
- **Real-time Monitoring**: Live recording status and file size updates
- **File Management**: Recording list, favorites, and file operations
- **Responsive Design**: Mobile-friendly interface

### ⭐ Favorites System
- **Like/Favorite**: Mark important recorded files as favorites
- **Protection Feature**: Favorite files are excluded from automatic deletion

### 🔄 Rotation Policy System
- **Reusable Policies**: Create and share rotation policies across schedules
- **Multiple Strategies**: Time-based (age), count-based (quantity), size-based (storage)
- **Priority System**: Policy priority and favorite file protection
- **Flexible Assignment**: Apply policies to multiple recording schedules

### 🐳 Deployment & Infrastructure
- **Docker Support**: Containerized deployment environment
- **Lightweight Database**: Built-in DB without separate container
- **Extensible Architecture**: Modular structure for easy addition of new platforms

## Technology Stack

### Backend
- **Language**: Python 3.10+ (Required)
- **Web Framework**: FastAPI
- **Streaming**: Streamlink
- **Scheduler**: APScheduler
- **Database**: SQLite (Built-in DB)

### Frontend
- **Language**: TypeScript
- **Framework**: Next.js 15
- **UI Library**: Tailwind CSS with Headless UI
- **State Management**: Zustand
- **Data Fetching**: React Query (@tanstack/react-query)

### Infrastructure
- **Container**: Docker & Docker Compose
- **File System**: Local storage or network storage
- **Logging**: Structured logging system

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js App   │    │   FastAPI       │    │  APScheduler    │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Jobs)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   App Data      │    │   SQLite DB     │    │  Streamlink     │
│  (Volume Mount) │    │   (Metadata)    │    │   Process       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Platform Support Strategy

### Abstraction Layer
- **Platform Interface**: Common interface that all platforms must implement
- **Strategy Pattern**: Stream URL acquisition strategy for each platform
- **Plugin System**: Plugin architecture for adding new platforms

### Supported Platforms
- **Twitch**: Direct stream detection and recording
- **YouTube**: Live stream support with optimized settings
- **Sooplive**: Korean streaming platform support
- **Chzzk (치지직)**: Naver's streaming platform support
- **Extensible Architecture**: Easy addition of new platforms via strategy pattern

## Configuration & Customization

### Platform Configuration
Managed through the web dashboard:
- **Twitch**: Stream quality and custom Streamlink arguments
- **YouTube**: Live stream settings and API configuration
- **Sooplive**: Korean platform-specific settings
- **Chzzk**: Naver streaming platform support

### Recording Schedules
- **Per-schedule Settings**: Quality, custom arguments, rotation policies
- **Monitoring Intervals**: Configurable stream check frequency
- **File Management**: Automatic naming and organization

### Rotation Policies
- **Reusable Policies**: Create once, apply to multiple schedules
- **Multiple Conditions**: Age, count, and size-based cleanup
- **Smart Cleanup**: Preserve favorites and recent files

## Development & Deployment

### Quick Start

**⚠️ Important: This project requires Python 3.10+ and Linux/macOS/Docker environment**

#### Development Mode
```bash
# Backend (Terminal 1)
cd backend
./run.sh  # Auto-setup venv and start server

# Frontend (Terminal 2) 
cd frontend
npm install
npm run dev
```

#### Docker Deployment
```bash
# Build and run with Docker
docker build -t streamlink-dashboard .
docker run -d -p 8000:8000 -v $(pwd)/app_data:/app/app_data --name streamlink-dashboard streamlink-dashboard

# Access at http://localhost:8000
# Default login: admin/admin123
```

### Manual Setup

**Requirements:**
- Python 3.10+ (Required)
- Linux/macOS/Docker environment (Windows not supported for development)

```bash
# Create virtual environment (Python 3.10 required)
python3.10 -m venv backend/venv
source backend/venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run development server
cd backend && ./run.sh
```

### Environment Setup Guide

For detailed environment setup instructions, see [Environment Setup Guide](docs/ENVIRONMENT_SETUP.md)

### Production Deployment

#### Docker (Recommended)
```bash
# Build image
docker build -t streamlink-dashboard .

# Run with volume mount for data persistence
docker run -d \
  --name streamlink-dashboard \
  -p 8000:8000 \
  -v $(pwd)/app_data:/app/app_data \
  streamlink-dashboard
```

#### NAS Deployment (Synology)
```bash
# Run on Synology NAS
docker run -d \
  --name streamlink-dashboard \
  -p 8000:8000 \
  -v /volume1/streamlink-data:/app/app_data \
  streamlink-dashboard
```

## Authentication

### Authentication
- **HTTP Basic Auth**: Simple username/password authentication
- **JWT Tokens**: Secure session management
- **Default Admin**: admin/admin123 (change after first login)
- **Role-based Access**: Admin and user roles supported

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

### Docker Logging
```bash
# View application logs
docker logs streamlink-dashboard

# Follow logs in real-time
docker logs -f streamlink-dashboard

# View recent logs
docker logs --tail=100 streamlink-dashboard

# View error logs only
docker logs streamlink-dashboard 2>&1 | grep ERROR
```

### Log Management
- **Structured Logging**: JSON format for easy parsing
- **Log Rotation**: Automatic log file rotation
- **Error Tracking**: Comprehensive error logging and monitoring

## Key Files & Structure

```
├── backend/               # Python FastAPI backend
│   ├── app/
│   │   ├── api/v1/       # REST API endpoints
│   │   ├── services/     # Business logic (scheduler, streamlink)
│   │   ├── database/     # SQLAlchemy models and DB setup
│   │   └── schemas/      # Pydantic schemas
│   └── run.sh            # Development server script
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── app/          # Next.js 15 App Router
│   │   ├── components/   # React components
│   │   ├── lib/          # API client and utilities
│   │   └── store/        # Zustand state management
├── app_data/             # Docker volume mount point
│   ├── database/         # SQLite database
│   ├── recordings/       # Recorded video files
│   ├── logs/             # Application logs
│   └── config/           # Configuration files
└── Dockerfile            # Multi-stage Docker build
```

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
