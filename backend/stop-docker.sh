#!/bin/bash

# Cookify Backend Docker Stop Script

echo "🛑 Stopping Cookify Backend..."

cd "$(dirname "$0")"

# Stop and remove containers
docker  compose down

echo "✅ Cookify Backend stopped!"
echo ""
echo "📊 Remaining containers:"
docker ps --filter "name=cookify"
