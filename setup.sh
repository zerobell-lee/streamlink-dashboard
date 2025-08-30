#!/bin/bash

# Streamlink Dashboard Environment Setup Script
# This script sets up the development environment for Linux/macOS

set -e

echo "🚀 Streamlink Dashboard Environment Setup"
echo "=========================================="

# Check if Python 3.10 is available
if ! command -v python3.10 &> /dev/null; then
    echo "❌ Python 3.10 is required but not found."
    echo "Please install Python 3.10 first:"
    echo ""
    echo "Ubuntu/Debian:"
    echo "  sudo apt update"
    echo "  sudo apt install software-properties-common"
    echo "  sudo add-apt-repository ppa:deadsnakes/ppa"
    echo "  sudo apt update"
    echo "  sudo apt install python3.10 python3.10-venv python3.10-dev"
    echo ""
    echo "macOS:"
    echo "  brew install python@3.10"
    echo ""
    exit 1
fi

echo "✅ Python 3.10 found: $(python3.10 --version)"

# Install system dependencies
echo "📦 Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    sudo apt-get update
    sudo apt-get install -y build-essential libsqlite3-dev sqlite3 ffmpeg curl python3-dev python3.10-dev
elif command -v brew &> /dev/null; then
    # macOS
    brew install sqlite ffmpeg
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    sudo yum install -y gcc sqlite-devel sqlite ffmpeg curl python3-devel
elif command -v dnf &> /dev/null; then
    # Fedora
    sudo dnf install -y gcc sqlite-devel sqlite ffmpeg curl python3-devel
else
    echo "⚠️  Could not detect package manager. Please install manually:"
    echo "   - build-essential (gcc, make, etc.)"
    echo "   - libsqlite3-dev"
    echo "   - sqlite3"
    echo "   - ffmpeg"
    echo "   - python3-dev"
fi

# Check if SQLite3 module is available in Python
echo "🔍 Checking SQLite3 availability..."
if ! python3.10 -c "import sqlite3; print('SQLite3 available')" 2>/dev/null; then
    echo "⚠️  SQLite3 module not available in Python 3.10"
    echo "This might be due to pyenv installation without SQLite support."
    echo ""
    echo "Solutions:"
    echo "1. Reinstall Python 3.10 with SQLite support:"
    echo "   CONFIGURE_OPTS='--enable-loadable-sqlite-extensions' pyenv install 3.10.18"
    echo ""
    echo "2. Or use system Python 3.10 instead of pyenv"
    echo ""
    echo "3. Or use Docker (recommended):"
    echo "   docker-compose up --build"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ SQLite3 module is available"
fi

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ] || [ ! -d "backend" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Create unified data directory structure
echo "📁 Creating app_data directory structure..."
mkdir -p app_data/recordings
mkdir -p app_data/database
mkdir -p app_data/logs
mkdir -p app_data/config

# Setup backend environment
echo "🐍 Setting up backend environment..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3.10 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install streamlink
echo "Installing streamlink..."
pip install streamlink

# Make run script executable
chmod +x run.sh

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# Application settings
DEBUG=true
LOG_LEVEL=INFO

# Database settings
APP_DATA_DIR=/app_data
DATABASE_URL=sqlite+aiosqlite:///$$APP_DATA_DIR/database/streamlink_dashboard.db

# Streamlink settings
STREAMLINK_PATH=streamlink
DEFAULT_QUALITY=best

# Authentication
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=admin123

# Scheduler settings
SCHEDULER_TIMEZONE=UTC
AUTO_START_SCHEDULER=true
EOF
fi

cd ..

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo ""
echo "1. start the development server:"
echo "   cd backend && ./run.sh"
echo ""
echo "2. Access the application:"
echo "   http://localhost:8000"
echo "   API docs: http://localhost:8000/docs"
echo ""
echo "� If your encounter SQLite issues, use Docker instead!"
echo "📚 For more information, see docs/ENVIRONMENT_SETUP.md"