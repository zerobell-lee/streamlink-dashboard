# Backend only Dockerfile
FROM python:3.10.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libsqlite3-dev \
    sqlite3 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install streamlink
RUN pip install streamlink

# Copy requirements and install Python dependencies
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY ./backend .

# Create data directories
RUN mkdir -p /app/app_data/recordings \
    && mkdir -p /app/app_data/database \
    && mkdir -p /app/app_data/logs \
    && mkdir -p /app/app_data/config

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV APP_DATA_DIR=/app/app_data

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]