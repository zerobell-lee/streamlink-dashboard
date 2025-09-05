<div align="center">

# 🎮 Streamlink Dashboard

*Your ultimate streaming recording companion*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://hub.docker.com/r/zerobell/streamlink-dashboard)
[![FastAPI](https://img.shields.io/badge/FastAPI-109989?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

<p>
    <a href="https://www.buymeacoffee.com/zerobell">
      <img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee" alt="Buy Me a Coffee">
    </a>
</p>

---

**🚀 Never miss your favorite streams again!** Automatically record live streams from multiple platforms with a sleek, modern web dashboard.

</div>

A powerful web-based dashboard application for automated streaming recording using Streamlink. Built with modern technologies and designed for seamless stream management.

## Project Overview

Streamlink Dashboard is a web application that automatically records and manages live streams from various streaming platforms. Users can set up scheduled jobs to automatically record streams from their favorite streamers and manage recorded files through a web dashboard.

## ✨ Key Features

<div align="center">

| 🎥 **Smart Recording** | 📅 **Auto Scheduling** | 🖥️ **Modern Dashboard** |
|:---:|:---:|:---:|
| Multi-platform support<br/>Quality control<br/>Stream detection | Flexible job management<br/>Custom intervals<br/>Strategy patterns | React + Next.js 15<br/>Real-time updates<br/>Mobile-friendly |

</div>

### 🎬 **Real-time Streaming Recording**
- 🔥 **Streamlink-based**: Rock-solid and efficient recording engine
- 🌍 **Multi-platform Support**: Twitch, YouTube, Sooplive, Chzzk(치지직)
- ⚙️ **Platform-specific Optimization**: Tailored Streamlink arguments for each platform
- 📺 **Quality Control**: Choose your preferred stream quality

### 🤖 **Intelligent Scheduling System**
- ⚡ **APScheduler-powered**: Enterprise-grade job scheduling
- 🎯 **Strategy Pattern**: Clean, extensible platform architecture
- 🛠️ **Flexible Configuration**: Quality, custom args, monitoring intervals
- 🔍 **Auto Stream Detection**: Smart periodic checks for live streams

### 🎨 **Modern Web Dashboard**
- 🚀 **Next.js 15 + TypeScript**: Cutting-edge React stack
- 💅 **Tailwind CSS**: Beautiful, responsive design
- ⚡ **Real-time Updates**: Live recording status and progress
- 📱 **Mobile-friendly**: Works perfectly on all devices

### ⭐ **Smart Favorites System**
- 💖 **One-click Favorites**: Mark your most important recordings
- 🛡️ **Auto-protection**: Favorites are safe from cleanup policies
- 🏷️ **Easy Management**: Organize and find your best content

### 🔄 **Advanced Rotation Policies**
- 🔧 **Reusable Templates**: Create once, apply everywhere
- 📊 **Multiple Strategies**: Time, count, or size-based cleanup
- 🎛️ **Smart Priority**: Protect favorites and recent files
- 🎯 **Flexible Assignment**: Mix and match policies per schedule

### 🐳 **Production-Ready Deployment**
- 🚢 **Docker-first**: One-command deployment
- 🗃️ **Built-in Database**: No external dependencies
- 📈 **Scalable Architecture**: Easy to extend and customize
- 🔧 **NAS-friendly**: Perfect for Synology and QNAP

## 🛠️ Technology Stack

<div align="center">

### 🐍 **Backend Powerhouse**
```
Python 3.10+  │  FastAPI  │  Streamlink  │  APScheduler  │  SQLite
```

### ⚛️ **Modern Frontend**
```
TypeScript  │  Next.js 15  │  Tailwind CSS  │  Zustand  │  React Query
```

### 🚀 **Infrastructure**
```
Docker  │  SQLAlchemy  │  Pydantic  │  Alembic  │  Uvicorn
```

</div>

| Component | Technology | Purpose |
|-----------|------------|---------|
| 🔧 **Backend Framework** | FastAPI | High-performance async API |
| 🎬 **Recording Engine** | Streamlink | Reliable stream recording |
| ⏰ **Job Scheduler** | APScheduler | Robust background tasks |
| 🗄️ **Database** | SQLite + SQLAlchemy | Lightweight, async ORM |
| ⚛️ **Frontend Framework** | Next.js 15 + TypeScript | Modern React with SSR |
| 🎨 **UI Framework** | Tailwind CSS + Headless UI | Beautiful, accessible components |
| 📦 **State Management** | Zustand | Simple, scalable state |
| 🔄 **Data Fetching** | TanStack Query | Smart server state management |
| 🐳 **Deployment** | Docker + Compose | Container-ready deployment |

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

## 🚀 Quick Start

<div align="center">

**🎯 Get up and running in 2 minutes!**

</div>

> **⚠️ Requirements**: Python 3.10+, Linux/macOS/Docker environment

### 🐳 **One-Click Docker Deployment** (Recommended)

```bash
# 1️⃣ Clone and build
git clone https://github.com/your-username/streamlink-dashboard.git
cd streamlink-dashboard
docker build -t streamlink-dashboard .

# 2️⃣ Run with persistent data
docker run -d \
  --name streamlink-dashboard \
  -p 8000:8000 \
  -v $(pwd)/app_data:/app/app_data \
  streamlink-dashboard

# 3️⃣ Open your browser
echo "🎉 Dashboard ready at: http://localhost:8000"
echo "🔑 Default login: admin/admin123"
```

### 👨‍💻 **Development Mode**

```bash
# 🔧 Backend (Terminal 1)
cd backend
./run.sh  # 🪄 Auto-setup venv and start server

# ⚛️ Frontend (Terminal 2) 
cd frontend
npm install && npm run dev  # 🚀 Start with Turbopack
```

<div align="center">

**🎊 That's it! Your streaming dashboard is ready to go!**

Open http://localhost:3000 (dev) or http://localhost:8000 (docker)

</div>

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

## 🤝 Contributing

We'd love your help making Streamlink Dashboard even better! 

<div align="center">

**Found a bug? 🐛 Have an idea? 💡 Want to contribute? 🚀**

</div>

### 📝 **How to Contribute**

1. 🍴 **Fork** the repository
2. 🌿 **Create** your feature branch (`git checkout -b feature/amazing-feature`)
3. ✨ **Commit** your changes (`git commit -m 'Add some amazing feature'`)
4. 📤 **Push** to the branch (`git push origin feature/amazing-feature`)
5. 🎯 **Open** a Pull Request

### 🎯 **Areas We'd Love Help With**

- 🆕 **New Platform Support**: Add support for more streaming platforms
- 🎨 **UI/UX Improvements**: Make the dashboard even more beautiful
- 🧪 **Testing**: Help us achieve better test coverage
- 📚 **Documentation**: Improve guides and examples
- 🐛 **Bug Fixes**: Fix issues and improve stability
- ⚡ **Performance**: Optimize recording and dashboard performance

---

## 📄 License

<div align="center">

**MIT License** - feel free to use this project however you'd like! 

See the [LICENSE](LICENSE) file for full details.

</div>

### 📚 **Third-Party Licenses**

This project stands on the shoulders of giants! Check out [THIRD-PARTY-LICENSES.md](THIRD-PARTY-LICENSES.md) for complete license information.

**Quick Summary:**
- ✅ **Project**: MIT License  
- ✅ **Backend Dependencies**: MIT, Apache-2.0, BSD compatible
- ✅ **Frontend Dependencies**: MIT compatible
- 🎉 **All dependencies are MIT-compatible** - ready for open source!

---

<div align="center">

**⭐ Star this repo if you found it helpful!**

**☕ [Buy me a coffee](https://www.buymeacoffee.com/zerobell)** if you want to support development!

Made with ❤️ for the streaming community

</div>
