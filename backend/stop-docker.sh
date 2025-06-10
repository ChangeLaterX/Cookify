#!/bin/bash

# Cookify Backend Docker Stop Script

echo "🛑 Stopping Cookify Backend..."

cd "$(dirname "$0")"

# Stoppe und entferne Container
docker-compose down

echo "✅ Cookify Backend gestoppt!"
echo ""
echo "📊 Verbleibende Container:"
docker ps --filter "name=cookify"
