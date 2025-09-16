#!/bin/bash
# Version update script for streamlink-dashboard
# This script updates version in both backend and frontend configuration files

set -e

# Check if version argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 0.6.0"
    exit 1
fi

NEW_VERSION="$1"

# Validate version format (basic semantic versioning check)
if ! echo "$NEW_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9\-\.]+)?$'; then
    echo "ERROR: Invalid version format. Expected: X.Y.Z or X.Y.Z-suffix"
    echo "Examples: 1.0.0, 0.5.0, 1.0.0-beta.1"
    exit 1
fi

echo "Updating version to: $NEW_VERSION"

# Check if required files exist
if [ ! -f "backend/.env" ]; then
    echo "ERROR: backend/.env file not found"
    exit 1
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "ERROR: frontend/.env.local file not found"
    exit 1
fi

# Create backup files
echo "Creating backup files..."
cp "backend/.env" "backend/.env.backup.$(date +%Y%m%d_%H%M%S)"
cp "frontend/.env.local" "frontend/.env.local.backup.$(date +%Y%m%d_%H%M%S)"

# Update backend version
echo "Updating backend version..."
if grep -q "^VERSION=" "backend/.env"; then
    sed -i "s/^VERSION=.*/VERSION=$NEW_VERSION/" "backend/.env"
    echo "Backend version updated to: $NEW_VERSION"
else
    echo "VERSION=$NEW_VERSION" >> "backend/.env"
    echo "Backend version added: $NEW_VERSION"
fi

# Update frontend version
echo "Updating frontend version..."
if grep -q "^NEXT_PUBLIC_APP_VERSION=" "frontend/.env.local"; then
    sed -i "s/^NEXT_PUBLIC_APP_VERSION=.*/NEXT_PUBLIC_APP_VERSION=$NEW_VERSION/" "frontend/.env.local"
    echo "Frontend version updated to: $NEW_VERSION"
else
    echo "NEXT_PUBLIC_APP_VERSION=$NEW_VERSION" >> "frontend/.env.local"
    echo "Frontend version added: $NEW_VERSION"
fi

# Update .env.example if it exists
if [ -f ".env.example" ]; then
    echo "Updating .env.example..."
    sed -i "s/^VERSION=.*/VERSION=$NEW_VERSION/" ".env.example" 2>/dev/null || true
    sed -i "s/^NEXT_PUBLIC_APP_VERSION=.*/NEXT_PUBLIC_APP_VERSION=$NEW_VERSION/" ".env.example" 2>/dev/null || true
    echo ".env.example updated"
fi

echo ""
echo "SUCCESS: Version update completed!"
echo "New version: $NEW_VERSION"
echo ""
echo "Verifying synchronization..."

# Run version sync check
if [ -f "scripts/check-version-sync.sh" ]; then
    bash scripts/check-version-sync.sh
else
    echo "WARNING: check-version-sync.sh not found, skipping verification"
fi