#!/bin/bash

# Cookify Backend Docker Setup Script

echo "🐳 Cookify Backend Docker Setup"
echo "==============================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying .env.example to .env..."
    cp .env.example .env
    echo "📝 Please edit the .env file with your Supabase credentials:"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_KEY"
    echo ""
    read -p "Press Enter once you have configured the .env file..."
fi

# Build and start containers
echo "🔨 Building Docker Image..."
docker compose build

echo "🚀 Starting Cookify API..."
docker compose up -d

echo ""
echo "✅ Cookify API is now running!"
echo "🌐 API available at: http://localhost:8000"
echo "📋 Health Check: http://localhost:8000/health"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Container Status:"
docker compose ps

echo ""
echo "📝 Useful Commands:"
echo "  docker-compose logs -f          # View logs"
echo "  docker-compose stop             # Stop containers"
echo "  docker-compose down             # Stop and remove containers"
echo "  docker-compose restart          # Restart containers"
