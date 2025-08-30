# Streamlink Dashboard Backend

A FastAPI-based backend for managing streaming platform recordings with automated scheduling and file rotation policies.

## Features

- **Multi-platform Support**: Twitch, YouTube, Sooplive
- **Automated Recording**: Schedule-based recording with APScheduler
- **File Rotation**: Automatic cleanup based on time, count, and size policies
- **RESTful API**: Complete CRUD operations for schedules and policies
- **Real-time Monitoring**: Live status updates and progress tracking

## Installation

1. Clone the repository
2. Navigate to the backend directory
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy `.env.example` to `.env`
2. Update the configuration values in `.env`
3. Run database migrations:
   ```bash
   alembic upgrade head
   ```

## Running the Application

### Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v --asyncio-mode=auto

# Run specific test file
python -m pytest tests/test_recording_schedule.py -v --asyncio-mode=auto

# Run specific test
python -m pytest tests/test_recording_schedule.py::TestRecordingSchedule::test_create_recording_schedule_success -v --asyncio-mode=auto
```

### Test Coverage
```bash
# Install coverage tool
pip install pytest-cov

# Run tests with coverage
python -m pytest tests/ --cov=app --cov-report=html --asyncio-mode=auto
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/                 # API endpoints
│   ├── core/               # Configuration and settings
│   ├── database/           # Database models and migrations
│   ├── services/           # Business logic services
│   └── main.py            # Application entry point
├── tests/                 # Test files
├── alembic/               # Database migrations
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Key Components

### Services
- **PlatformService**: Handles different streaming platforms
- **SchedulerService**: Manages recording schedules
- **RotationService**: Implements file cleanup policies
- **StreamlinkService**: Interfaces with Streamlink CLI

### Models
- **RecordingSchedule**: Defines recording schedules
- **RotationPolicy**: File cleanup policies
- **Recording**: Individual recording instances
- **User**: User management

## Development

### Adding New Tests
1. Create test files in the `tests/` directory
2. Use the provided fixtures in `conftest.py`
3. Follow the naming convention: `test_*.py`
4. Use `@pytest.mark.asyncio` for async tests

### Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## License

This project is licensed under the MIT License.
