# Streamlink Dashboard - Development Guide

## Development Environment Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- Docker (optional)
- Git

### Local Development Environment Setup

#### 1. Clone Repository
```bash
git clone https://github.com/your-username/streamlink-dashboard.git
cd streamlink-dashboard
```

#### 2. Python Virtual Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source venv/bin/activate
```

#### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Install Frontend Dependencies
```bash
cd frontend
npm install
```

#### 5. Environment Variables Setup
```bash
# Create .env file
cp .env.example .env

# Edit environment variables
# Basic auth credentials, database settings, etc.
```

### Development Server Execution

#### Backend Server
```bash
# Run in development mode
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Server
```bash
cd frontend
npm run dev
```

## Project Structure

```
streamlink-dashboard/
├── app/                    # Backend application
│   ├── api/               # API routers
│   ├── core/              # Core settings and utilities
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   ├── strategies/        # Platform strategy pattern
│   ├── auth/              # Authentication services
│   └── main.py           # Application entry point
├── frontend/              # Frontend application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── utils/         # Utility functions
│   └── package.json
├── docs/                  # Documentation
├── tests/                 # Test code
├── docker/                # Docker configuration
├── requirements.txt       # Python dependencies
└── README.md
```

## Coding Conventions

### Python Coding Style

- **PEP 8** compliance
- **Black** code formatter
- **isort** import sorting
- **flake8** linter

```bash
# Code formatting
black app/
isort app/

# Linting
flake8 app/
```

### TypeScript/JavaScript Coding Style

- **ESLint** + **Prettier**
- **TypeScript** strict mode
- **React Hooks** recommended

```bash
# Code formatting
npm run format

# Linting
npm run lint
```

### Commit Message Conventions

```
type(scope): description

feat: add new feature
fix: fix bug
docs: update documentation
style: code formatting
refactor: code refactoring
test: add/update tests
chore: build process or auxiliary tool changes
```

## Platform Strategy Development Guide

### Adding New Platform

#### 1. Create Strategy Class

```python
# app/strategies/new_platform.py
from app.strategies.base import PlatformStrategy
from typing import Optional, Dict, Any

class NewPlatformStrategy(PlatformStrategy):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_base = "https://api.newplatform.com"
    
    def get_stream_url(self, streamer_id: str) -> Optional[str]:
        """Returns the current live stream URL for the streamer"""
        try:
            # API call to get stream URL
            response = self._make_api_request(f"/streams/{streamer_id}")
            if response and response.get('is_live'):
                return response.get('stream_url')
            return None
        except Exception as e:
            logger.error(f"Failed to get stream URL for {streamer_id}: {e}")
            return None
    
    def is_live(self, streamer_id: str) -> bool:
        """Checks if the streamer is currently live"""
        try:
            response = self._make_api_request(f"/streams/{streamer_id}")
            return response.get('is_live', False)
        except Exception as e:
            logger.error(f"Failed to check live status for {streamer_id}: {e}")
            return False
    
    def get_stream_info(self, streamer_id: str) -> Dict[str, Any]:
        """Returns stream information"""
        try:
            response = self._make_api_request(f"/streams/{streamer_id}")
            return {
                'title': response.get('title'),
                'viewer_count': response.get('viewer_count'),
                'started_at': response.get('started_at'),
                'thumbnail_url': response.get('thumbnail_url')
            }
        except Exception as e:
            logger.error(f"Failed to get stream info for {streamer_id}: {e}")
            return {}
    
    def get_streamlink_args(self) -> list:
        """Returns platform-specific Streamlink arguments"""
        return [
            "--new-platform-option1",
            "--new-platform-option2"
        ]
    
    def _make_api_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """API request helper method"""
        # API request implementation
        pass
```

#### 2. Register Strategy

```python
# app/strategies/__init__.py
from .new_platform import NewPlatformStrategy

STRATEGY_REGISTRY = {
    'twitch': TwitchStrategy,
    'youtube': YouTubeStrategy,
    'new_platform': NewPlatformStrategy,  # Add new platform
}
```

#### 3. Add Configuration

```python
# app/core/config.py
class Settings(BaseSettings):
    # Existing settings...
    NEW_PLATFORM_API_KEY: str = ""
```

### Platform-specific Test Writing

```python
# tests/test_strategies/test_new_platform.py
import pytest
from app.strategies.new_platform import NewPlatformStrategy

class TestNewPlatformStrategy:
    @pytest.fixture
    def strategy(self):
        return NewPlatformStrategy("test_api_key")
    
    def test_get_stream_url_success(self, strategy, mocker):
        # Success case test
        mock_response = {
            'is_live': True,
            'stream_url': 'https://stream.newplatform.com/live'
        }
        mocker.patch.object(strategy, '_make_api_request', return_value=mock_response)
        
        result = strategy.get_stream_url("test_streamer")
        assert result == 'https://stream.newplatform.com/live'
    
    def test_get_stream_url_not_live(self, strategy, mocker):
        # Not live case test
        mock_response = {'is_live': False}
        mocker.patch.object(strategy, '_make_api_request', return_value=mock_response)
        
        result = strategy.get_stream_url("test_streamer")
        assert result is None
```

## API Development Guide

### Adding New API Endpoint

#### 1. Create Router

```python
# app/api/v1/new_endpoint.py
from fastapi import APIRouter, Depends, HTTPException
from app.models.new_model import NewModel
from app.services.new_service import NewService

router = APIRouter()

@router.get("/new-endpoint")
async def get_new_data(
    service: NewService = Depends()
) -> List[NewModel]:
    """New endpoint description"""
    try:
        return await service.get_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2. Register Router

```python
# app/api/v1/__init__.py
from .new_endpoint import router as new_router

# Existing routers...
api_router.include_router(new_router, prefix="/new", tags=["new"])
```

### API Documentation

```python
@router.post("/schedules", response_model=ScheduleResponse)
async def create_schedule(
    schedule: ScheduleCreate,
    service: ScheduleService = Depends()
) -> ScheduleResponse:
    """
    Create a new recording schedule.
    
    - **platform**: Streaming platform (twitch, youtube, etc.)
    - **streamer_name**: Streamer name
    - **quality**: Recording quality (best, 720p, 480p, etc.)
    """
    return await service.create_schedule(schedule)
```

## Authentication Development

### Basic Authentication Implementation

```python
# app/auth/basic_auth.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import hashlib

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

## Configuration Management Development

### Database-based Configuration Service

```python
# app/services/config_service.py
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

## Frontend Development Guide

### Creating New Component

```typescript
// frontend/src/components/NewComponent.tsx
import React from 'react';
import { useQuery } from 'react-query';
import { apiService } from '../services/api';

interface NewComponentProps {
  id: string;
  onUpdate?: (data: any) => void;
}

export const NewComponent: React.FC<NewComponentProps> = ({ id, onUpdate }) => {
  const { data, isLoading, error } = useQuery(
    ['new-data', id],
    () => apiService.getNewData(id)
  );

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div className="new-component">
      {/* Component content */}
    </div>
  );
};
```

### API Service Addition

```typescript
// frontend/src/services/api.ts
export const apiService = {
  // Existing methods...
  
  async getNewData(id: string): Promise<any> {
    const response = await fetch(`/api/new-data/${id}`);
    if (!response.ok) {
      throw new Error('Failed to fetch new data');
    }
    return response.json();
  },
  
  async createNewData(data: any): Promise<any> {
    const response = await fetch('/api/new-data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error('Failed to create new data');
    }
    return response.json();
  },
};
```

## Test Writing Guide

### Backend Tests

```python
# tests/test_api/test_schedules.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestSchedulesAPI:
    def test_create_schedule(self):
        """Schedule creation test"""
        schedule_data = {
            "platform": "twitch",
            "streamer_name": "test_streamer",
            "quality": "best"
        }
        
        response = client.post("/api/schedules", json=schedule_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["platform"] == "twitch"
        assert data["streamer_name"] == "test_streamer"
    
    def test_get_schedules(self):
        """Schedule list retrieval test"""
        response = client.get("/api/schedules")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
```

### Frontend Tests

```typescript
// frontend/src/components/__tests__/NewComponent.test.tsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { NewComponent } from '../NewComponent';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

describe('NewComponent', () => {
  it('renders loading state initially', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <NewComponent id="test-id" />
      </QueryClientProvider>
    );
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
  
  it('renders data when loaded', async () => {
    // Mock API response
    jest.spyOn(global, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ name: 'Test Data' }),
    } as Response);
    
    render(
      <QueryClientProvider client={queryClient}>
        <NewComponent id="test-id" />
      </QueryClientProvider>
    );
    
    await waitFor(() => {
      expect(screen.getByText('Test Data')).toBeInTheDocument();
    });
  });
});
```

## Debugging Guide

### Backend Debugging

```python
# Logging setup
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Debugger usage
import pdb; pdb.set_trace()

# Or use ipdb for better debugging experience
import ipdb; ipdb.set_trace()
```

### Frontend Debugging

```typescript
// Use React DevTools
// Install React DevTools extension in browser

// Console logging
console.log('Debug data:', data);

// React Query DevTools
import { ReactQueryDevtools } from 'react-query/devtools';

function App() {
  return (
    <>
      {/* App components */}
      <ReactQueryDevtools initialIsOpen={false} />
    </>
  );
}
```

## Deployment Guide

### Docker Build

```bash
# Development image build
docker build -f docker/Dockerfile.dev -t streamlink-dashboard:dev .

# Production image build
docker build -f docker/Dockerfile.prod -t streamlink-dashboard:prod .
```

### Environment-specific Configuration

```bash
# Development environment
docker-compose -f docker-compose.dev.yml up

# Production environment
docker-compose -f docker-compose.prod.yml up -d
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

## Performance Optimization Tips

### Backend Optimization

1. **Database Query Optimization**
   - Add indexes
   - Solve N+1 query problems
   - Query caching

2. **Asynchronous Processing**
   - Background job processing with APScheduler
   - Asynchronous I/O utilization

3. **Caching Strategy**
   - In-memory caching
   - Configuration caching

### Frontend Optimization

1. **Code Splitting**
   - Use React.lazy()
   - Dynamic imports

2. **Bundle Optimization**
   - Tree shaking
   - Code compression

3. **Image Optimization**
   - Use WebP format
   - Lazy loading

## Troubleshooting

### Common Issues

1. **Streamlink Errors**
   - Check platform-specific authentication
   - Verify network connection status
   - Check Streamlink version compatibility

2. **Database Errors**
   - Check SQLite file permissions
   - Database schema migration

3. **API Errors**
   - Check CORS settings
   - Verify authentication token validity
   - Check API key settings

### Log Checking

```bash
# Check application logs
docker logs streamlink-dashboard

# Check logs for specific time period
docker logs --since="2023-01-01T00:00:00" streamlink-dashboard

# Check logs in real-time
docker logs -f streamlink-dashboard

# Check error logs only
docker logs streamlink-dashboard 2>&1 | grep ERROR
```

## NAS Environment Considerations

### Synology NAS Specific

- **Volume Path Mapping**: Use `/volume1/recordings` for recordings
- **Docker Management**: Use DSM for container management
- **Resource Limitations**: Optimize for NAS resource constraints
- **Backup Procedures**: Regular backup of configuration and data

### Configuration Management

- **Database-based Settings**: All configurations stored in SQLite
- **Web Interface**: Manage settings through dashboard
- **No Container Recreation**: Change settings without rebuilding
- **Backup and Restore**: Easy backup and restore of settings

### Development Workflow

1. **Local Development**: Develop and test locally
2. **Docker Build**: Build Docker image
3. **NAS Deployment**: Deploy to Synology NAS
4. **Configuration**: Use web interface to configure settings
5. **Monitoring**: Use Docker logs for monitoring
