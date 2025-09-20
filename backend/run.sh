#!/bin/bash

# Create and activate virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment with Python 3.10..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip first
echo "Upgrading pip..."
pip install --upgrade pip

# Install/upgrade requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Check if uvicorn is installed
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "Installing uvicorn..."
    pip install uvicorn[standard]
fi

# Install streamlink if not available
if ! command -v streamlink &> /dev/null; then
    echo "Installing streamlink..."
    pip install -U streamlink
fi

# Run the FastAPI server
echo "Starting FastAPI server..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000