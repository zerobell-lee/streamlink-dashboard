#!/bin/bash
# Version synchronization check script for streamlink-dashboard
# This script verifies that backend and frontend versions are synchronized

set -e

echo "Checking version synchronization..."

# Check if required files exist
if [ ! -f "backend/.env" ]; then
    echo "ERROR: backend/.env file not found"
    exit 1
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "ERROR: frontend/.env.local file not found"
    exit 1
fi

# Extract versions from files
BACKEND_VERSION=$(grep "^VERSION=" backend/.env | cut -d'=' -f2)
FRONTEND_VERSION=$(grep "^NEXT_PUBLIC_APP_VERSION=" frontend/.env.local | cut -d'=' -f2)

# Validate that versions were found
if [ -z "$BACKEND_VERSION" ]; then
    echo "ERROR: VERSION not found in backend/.env"
    exit 1
fi

if [ -z "$FRONTEND_VERSION" ]; then
    echo "ERROR: NEXT_PUBLIC_APP_VERSION not found in frontend/.env.local"
    exit 1
fi

# Compare versions
echo "Backend version: $BACKEND_VERSION"
echo "Frontend version: $FRONTEND_VERSION"

if [ "$BACKEND_VERSION" != "$FRONTEND_VERSION" ]; then
    echo "ERROR: Version mismatch detected!"
    echo "Backend: $BACKEND_VERSION"
    echo "Frontend: $FRONTEND_VERSION"
    echo "Please synchronize versions using: ./scripts/update-version.sh <version>"
    exit 1
else
    echo "SUCCESS: Versions are synchronized ($BACKEND_VERSION)"
    exit 0
fi