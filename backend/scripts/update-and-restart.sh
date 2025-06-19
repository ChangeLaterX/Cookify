#!/bin/bash

# Update and restart backend on server
# This script stops the backend, pulls latest changes from dev branch, and restarts

set -e  # Exit on any error

echo "=== Backend Update and Restart Script ==="
echo "Starting at $(date)"

# Navigate to backend directory
BACKEND_DIR="/server/Cookify/backend"
echo "Navigating to $BACKEND_DIR"
cd "$BACKEND_DIR"

# Stop backend containers
echo "Stopping backend containers..."
if [ -f "stop-docker.sh" ]; then
    sh stop-docker.sh
    echo "Backend stopped successfully"
else
    echo "Warning: stop-docker.sh not found, attempting docker-compose down..."
    docker-compose down 2>/dev/null || echo "No containers to stop"
fi

# Git operations
echo "Updating code from git..."
git checkout dev
echo "Switched to dev branch"

git pull
echo "Pulled latest changes"

# Optional: Show recent commits
echo "Recent commits:"
git log --oneline -5

# Start backend containers
echo "Starting backend containers..."
if [ -f "start-docker.sh" ]; then
    sh start-docker.sh
    echo "Backend started successfully"
else
    echo "Warning: start-docker.sh not found, attempting docker-compose up..."
    docker-compose up -d
fi

# Wait a moment and check container status
echo "Checking container status..."
sleep 5
docker-compose ps

echo "=== Update and restart completed at $(date) ==="
echo "Backend should be available shortly"
