# Streamlink Dashboard - Deployment Guide

## Deployment Overview

Streamlink Dashboard is designed for Docker-based deployment and can operate stably in various environments, with special consideration for NAS environments.

## Deployment Environment

### Supported Environments
- **Linux**: Ubuntu 20.04+, CentOS 8+, Debian 11+
- **Windows**: Windows 10/11 (Docker Desktop)
- **macOS**: macOS 10.15+ (Docker Desktop)
- **NAS**: Synology DSM, QNAP QTS, TrueNAS
- **Cloud**: AWS, GCP, Azure, DigitalOcean

### System Requirements
- **CPU**: Minimum 2 cores, recommended 4+ cores
- **Memory**: Minimum 4GB, recommended 8GB+
- **Storage**: Minimum 50GB, expandable based on recording file storage needs
- **Network**: Stable internet connection (upload/download)

## Docker Deployment

### 1. Docker Installation

#### Ubuntu/Debian
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

#### Windows/macOS
- Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop)

### 2. Project Setup

```bash
# Clone project
git clone https://github.com/your-username/streamlink-dashboard.git
cd streamlink-dashboard

# Create environment variables file
cp .env.example .env
```

### 3. Environment Variables Setup

```bash
# Edit .env file
nano .env
```

```env
# Application settings
APP_NAME=Streamlink Dashboard
APP_ENV=production
APP_DEBUG=false
APP_URL=http://localhost:8080

# Database settings
DATABASE_URL=sqlite:///./data/streamlink.db

# File storage settings
STORAGE_PATH=/app/recordings
MAX_STORAGE_SIZE=100GB

# Basic authentication
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=your_secure_password

# Logging settings
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# Scheduler settings
SCHEDULER_INTERVAL=60  # seconds
```

### 4. Docker Compose Deployment

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 5. Docker Compose File Example

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile.prod
    container_name: streamlink-dashboard
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./recordings:/app/recordings
      - ./logs:/app/logs
    environment:
      - APP_ENV=production
      - DATABASE_URL=sqlite:///./data/streamlink.db
    env_file:
      - .env
    networks:
      - streamlink-network

networks:
  streamlink-network:
    driver: bridge

volumes:
  data:
  recordings:
  logs:
```

## NAS Deployment (Synology)

### Synology DSM Setup

#### 1. Docker Package Installation
- Open Package Center in DSM
- Install Docker package
- Launch Docker application

#### 2. Container Deployment
```bash
# Pull and run on Synology NAS
docker run -d \
  --name streamlink-dashboard \
  -p 8080:8080 \
  -v /volume1/recordings:/app/recordings \
  -v /volume1/data:/app/data \
  -v /volume1/logs:/app/logs \
  --restart unless-stopped \
  streamlink-dashboard
```

#### 3. Volume Path Mapping
- **Recordings**: `/volume1/recordings` → `/app/recordings`
- **Database**: `/volume1/data` → `/app/data`
- **Logs**: `/volume1/logs` → `/app/logs`

### DSM Docker GUI Management
- Use DSM Docker interface for container management
- Monitor resource usage through DSM
- Easy container start/stop/restart

## Authentication Setup

### Basic Authentication Configuration

#### 1. Initial Setup
```bash
# Set initial admin credentials
docker exec -it streamlink-dashboard python -c "
from app.services.auth_service import AuthService
from app.services.db_service import DatabaseService

db = DatabaseService()
auth = AuthService(db)

# Create admin user
auth.create_user('admin', 'your_secure_password')
print('Admin user created successfully')
"
```

#### 2. Web Interface Management
- Access web interface at `http://your-nas-ip:8080`
- Use Basic Auth credentials to log in
- Manage users through web interface

#### 3. Password Management
```bash
# Change admin password
docker exec -it streamlink-dashboard python -c "
from app.services.auth_service import AuthService
from app.services.db_service import DatabaseService

db = DatabaseService()
auth = AuthService(db)

# Update admin password
auth.update_user_password('admin', 'new_secure_password')
print('Password updated successfully')
"
```

## Configuration Management

### Database-based Configuration

#### 1. Web Interface Configuration
- All settings managed through web dashboard
- No container recreation required for settings changes
- Real-time configuration updates

#### 2. Configuration Categories
- **Platform Settings**: API keys, stream quality, custom arguments
- **Recording Settings**: Storage paths, file naming, rotation policies
- **System Settings**: Log levels, scheduler intervals, notification settings
- **User Settings**: Dashboard preferences, favorite management

#### 3. Configuration Backup
```bash
# Backup configuration database
docker exec streamlink-dashboard sqlite3 /app/data/streamlink.db ".backup '/tmp/config_backup.db'"
docker cp streamlink-dashboard:/tmp/config_backup.db ./config_backup_$(date +%Y%m%d_%H%M%S).db

# Restore configuration
docker cp ./config_backup_20231201_120000.db streamlink-dashboard:/tmp/restore.db
docker exec streamlink-dashboard sqlite3 /app/data/streamlink.db ".restore '/tmp/restore.db'"
```

## Logging and Monitoring

### Docker-based Logging

#### 1. Basic Log Commands
```bash
# View application logs
docker logs streamlink-dashboard

# Follow logs in real-time
docker logs -f streamlink-dashboard

# View logs for specific time period
docker logs --since="2023-01-01T00:00:00" streamlink-dashboard

# View error logs only
docker logs streamlink-dashboard 2>&1 | grep ERROR

# View logs with timestamps
docker logs -t streamlink-dashboard

# View last 100 lines
docker logs --tail 100 streamlink-dashboard
```

#### 2. Log Analysis
```bash
# Check for recording errors
docker logs streamlink-dashboard | grep -i "recording.*error"

# Check for authentication issues
docker logs streamlink-dashboard | grep -i "auth\|login"

# Check for disk space issues
docker logs streamlink-dashboard | grep -i "disk\|space\|full"

# Check for network issues
docker logs streamlink-dashboard | grep -i "network\|connection\|timeout"
```

#### 3. Log Rotation
```bash
# Create log rotation script
cat > /volume1/scripts/rotate_logs.sh << 'EOF'
#!/bin/bash
# Rotate logs older than 30 days
find /volume1/logs -name "*.log" -mtime +30 -delete
echo "Log rotation completed: $(date)" >> /volume1/logs/rotation.log
EOF

chmod +x /volume1/scripts/rotate_logs.sh

# Add to crontab (run weekly)
# 0 2 * * 0 /volume1/scripts/rotate_logs.sh
```

## Backup and Recovery

### Backup Strategy

#### 1. Database Backup
```bash
#!/bin/bash
# /volume1/scripts/backup_db.sh

BACKUP_DIR="/volume1/backups/streamlink-dashboard"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker exec streamlink-dashboard sqlite3 /app/data/streamlink.db ".backup '/tmp/backup.db'"
docker cp streamlink-dashboard:/tmp/backup.db $BACKUP_DIR/database_$DATE.db

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz -C /volume1/data .

# Remove old backups (older than 30 days)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE" >> /volume1/logs/backup.log
```

#### 2. Recovery Procedure
```bash
#!/bin/bash
# /volume1/scripts/restore_db.sh

BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Stop container
docker stop streamlink-dashboard

# Restore database
docker cp $BACKUP_FILE streamlink-dashboard:/tmp/restore.db
docker exec streamlink-dashboard sqlite3 /app/data/streamlink.db ".restore '/tmp/restore.db'"

# Start container
docker start streamlink-dashboard

echo "Restore completed from: $BACKUP_FILE" >> /volume1/logs/restore.log
```

## Performance Optimization

### System Tuning

#### 1. Docker Optimization
```bash
# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize kernel parameters
echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" >> /etc/sysctl.conf
sysctl -p
```

#### 2. Container Resource Limits
```yaml
# docker-compose.prod.yml additions
services:
  app:
    # Existing settings...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
```

## Security Configuration

### Basic Security Setup

#### 1. Firewall Configuration
```bash
# UFW firewall setup (Ubuntu/Debian)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8080/tcp
sudo ufw deny 22/tcp  # Block direct SSH if using key-based auth
```

#### 2. Docker Security
```yaml
# docker-compose.prod.yml additions
services:
  app:
    # Existing settings...
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /var/tmp
    user: "1000:1000"
```

#### 3. Network Security
- Use internal network access only
- Implement Basic Auth for web interface
- Regular password updates
- Monitor access logs

## Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker logs streamlink-dashboard

# Check container status
docker ps -a

# Restart container
docker restart streamlink-dashboard

# Check resource usage
docker stats streamlink-dashboard
```

#### 2. Disk Space Issues
```bash
# Check disk usage
df -h

# Clean Docker system
docker system prune -a

# Clean old log files
find /volume1/logs -name "*.log" -mtime +7 -delete

# Check recording file sizes
du -sh /volume1/recordings/*
```

#### 3. Network Issues
```bash
# Check port availability
netstat -tlnp | grep :8080

# Check firewall status
sudo ufw status

# Check Docker network
docker network ls
```

#### 4. Authentication Issues
```bash
# Check authentication logs
docker logs streamlink-dashboard | grep -i "auth\|login\|password"

# Reset admin password
docker exec -it streamlink-dashboard python -c "
from app.services.auth_service import AuthService
from app.services.db_service import DatabaseService
db = DatabaseService()
auth = AuthService(db)
auth.update_user_password('admin', 'new_password')
print('Password reset completed')
"
```

### Log Analysis Commands

```bash
# Monitor real-time logs
docker logs -f streamlink-dashboard

# Search for specific errors
docker logs streamlink-dashboard | grep -i "error\|exception\|failed"

# Check recording status
docker logs streamlink-dashboard | grep -i "recording\|stream\|live"

# Monitor resource usage
docker stats streamlink-dashboard

# Check container health
docker inspect streamlink-dashboard | grep -A 10 "Health"
```

## Updates and Maintenance

### Application Updates

```bash
#!/bin/bash
# /volume1/scripts/update.sh

cd /volume1/streamlink-dashboard

# Create backup
./scripts/backup_db.sh

# Pull latest code
git pull origin main

# Build new image
docker-compose -f docker-compose.prod.yml build

# Restart services
docker-compose -f docker-compose.prod.yml up -d

echo "Update completed: $(date)" >> /volume1/logs/update.log
```

### Regular Maintenance

```bash
#!/bin/bash
# /volume1/scripts/weekly_maintenance.sh

# Clean Docker system
docker system prune -f

# Clean old log files
find /volume1/logs -name "*.log" -mtime +30 -delete

# Optimize database
docker exec streamlink-dashboard sqlite3 /app/data/streamlink.db "VACUUM;"

# Create backup
./scripts/backup_db.sh

echo "Weekly maintenance completed: $(date)" >> /volume1/logs/maintenance.log
```

### Monitoring Scripts

```bash
#!/bin/bash
# /volume1/scripts/monitor.sh

# Check if container is running
if ! docker ps | grep -q "streamlink-dashboard"; then
    echo "$(date): Container is down, restarting..." >> /volume1/logs/monitor.log
    docker start streamlink-dashboard
fi

# Check disk usage
DISK_USAGE=$(df /volume1/recordings | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "$(date): Disk usage is ${DISK_USAGE}%" >> /volume1/logs/monitor.log
    # Send notification or trigger cleanup
fi

# Check for errors in logs
ERROR_COUNT=$(docker logs --since="1h" streamlink-dashboard 2>&1 | grep -c "ERROR")
if [ $ERROR_COUNT -gt 10 ]; then
    echo "$(date): High error count detected: ${ERROR_COUNT}" >> /volume1/logs/monitor.log
fi
```
