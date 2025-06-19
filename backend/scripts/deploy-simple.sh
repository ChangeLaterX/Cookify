#!/bin/bash

# ===================================================================
# SIMPLE COOKIFY DEVELOPMENT SERVER DEPLOYMENT
# Based on your original script, but optimized
# ===================================================================

set -e

echo "🚀 Deploying Cookify Development Server..."

# Stop backend
echo "📦 Stopping backend..."
cd /server/Cookify/backend
docker-compose -f docker-compose.dev.yml down --remove-orphans || echo "No containers to stop"

# Check git and update
echo "📥 Updating code..."
git checkout dev
git pull origin dev

# Show what changed
echo "📝 Recent changes:"
git log --oneline -5

# Build and start backend
echo "🔨 Building and starting backend..."
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d

# Wait a moment for startup
echo "⏳ Waiting for startup..."
sleep 10

# Check if it's running
echo "📊 Container status:"
docker-compose -f docker-compose.dev.yml ps

# Show URLs
echo "✅ Deployment complete!"
echo "🌐 API available at:"
echo "  - https://dev.krija.info:8000"
echo "  - https://dev.krija.info:8000/docs"
echo "  - https://dev.krija.info:8000/api/health"

# Show logs option
echo ""
echo "📋 To view logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "🛑 To stop: docker-compose -f docker-compose.dev.yml down"
