# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Streamlink Dashboard is a full-stack web application for automatic streaming recording management using Streamlink. It consists of a FastAPI backend with a React/Next.js frontend.

### Architecture

```
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── api/v1/    # API endpoints (recordings, schedules, platforms, users, system, scheduler)
│   │   ├── core/      # Authentication, config, and core utilities
│   │   ├── database/  # SQLAlchemy models and database setup
│   │   ├── schemas/   # Pydantic schemas for API serialization
│   │   └── services/  # Business logic services (scheduler, streamlink, platforms)
│   └── main.py        # FastAPI application entry point
└── frontend/          # Next.js React frontend
    └── src/
        ├── app/       # Next.js 15 App Router pages and layouts
        ├── components/# React components (Sidebar, Header, RecordingList)
        ├── lib/       # API client and utilities
        ├── store/     # Zustand state management
        └── types/     # TypeScript type definitions
```

## Development Commands

### Backend (Python 3.10+ required)

```bash
cd backend

# Development setup (recommended)
./run.sh                    # Auto-setup venv, install deps, and start server

# Manual setup
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
pytest                      # Run all tests
pytest tests/specific_test.py  # Run specific test file
```

### Frontend (Node.js/Next.js)

```bash
cd frontend

# Development
npm install
npm run dev                 # Start development server with Turbopack
npm run build               # Build for production
npm run start               # Start production server
npm run lint                # Run ESLint
```

## Key Technical Details

### Backend Architecture

- **Platform Strategy Pattern**: Extensible platform support through `PlatformStrategyFactory` with strategies for Twitch, YouTube, and Sooplive
- **Scheduler Service**: APScheduler-based job management for automated recording
- **Authentication**: HTTP Basic Auth with admin/user roles
- **Database**: SQLite with SQLAlchemy async ORM and Alembic migrations
- **File Management**: RotationPolicy entities manage cleanup rules, applied per-schedule basis

### Frontend Architecture

- **Next.js 15**: App Router with TypeScript
- **State Management**: Zustand for auth and application state
- **API Integration**: React Query (@tanstack/react-query) for server state
- **Styling**: Tailwind CSS with Headless UI components
- **UI Library**: Lucide React icons, custom File Explorer component

### Platform Integration

Each platform implements the `PlatformStrategy` interface:
- **Stream Detection**: Platform-specific methods to check if streams are live
- **Streamlink Configuration**: Platform-optimized recording arguments
- **URL Resolution**: Convert streamer IDs to recordable stream URLs

### Database Schema

**Core Domain Entities** (see `docs/class_diagram.puml` for complete architecture):

- **User**: Authentication with admin/user roles and session management
- **PlatformConfig**: Platform-specific configurations (Twitch, YouTube, Sooplive) 
- **SystemConfig**: Global system-wide key-value configuration storage
- **RotationPolicy**: **Reusable file cleanup policies** with multiple strategies:
  - `policy_type`: 'time' (age-based), 'count' (quantity-based), 'size' (storage-based)
  - Priority system, favorite protection, configurable thresholds
  - **1:N relationship with RecordingSchedule** - policies can be shared across schedules
- **RecordingSchedule**: Individual streamer recording configurations
  - **References RotationPolicy via `rotation_policy_id` FK** 
  - Platform, streamer info, quality settings, custom arguments
- **Recording**: Actual recording file metadata with favorite marking
- **RecordingJob**: Job execution tracking with status and error handling

**Key Relationships**:
```
RotationPolicy ||--o{ RecordingSchedule : applies_to
RecordingSchedule ||--o{ Recording : produces  
RecordingSchedule ||--o{ RecordingJob : executes
User ||--o{ RecordingSchedule : manages
```

### Important Patterns

1. **Async/Await**: All database operations use async SQLAlchemy
2. **Dependency Injection**: FastAPI's dependency system for database sessions and auth
3. **Service Layer**: Business logic separated into service classes
4. **Type Safety**: Full TypeScript coverage in frontend, Pydantic schemas in backend
5. **Error Handling**: Structured error responses with proper HTTP status codes

### Environment Notes

- **Python 3.10+ Required**: Backend will not work with older Python versions
- **Linux/macOS Recommended**: Development environment optimized for Unix systems
- **Docker Support**: Available for containerized deployment
- **Default Admin**: admin/admin123 (created automatically on first run)

## Documentation

**Primary Documentation Location**: `/docs/`
- `class_diagram.puml` - **CORE REFERENCE** for domain entities and relationships
- `system_architecture.puml` - High-level system architecture and service layers  
- `database_schema.puml` - Database schema with table definitions
- `use_cases/` - Use case diagrams for different user roles

**Backend-Specific Documentation**: `/backend/docs/`
- `MIGRATIONS.md` - Database migration procedures

**IMPORTANT**: Always refer to `/docs/class_diagram.puml` first when understanding system architecture. This diagram shows the correct entity relationships and business methods.