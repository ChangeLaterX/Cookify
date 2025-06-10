#!/bin/bash

# Cookify Backend Docker Setup Script

echo "🐳 Cookify Backend Docker Setup"
echo "==============================="

# Überprüfe ob Docker läuft
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker ist nicht gestartet. Bitte starte Docker zuerst."
    exit 1
fi

# Überprüfe ob .env existiert
if [ ! -f ".env" ]; then
    echo "⚠️  .env Datei nicht gefunden. Kopiere .env.example zu .env..."
    cp .env.example .env
    echo "📝 Bitte bearbeite die .env Datei mit deinen Supabase-Credentials:"
    echo "   - VITE_SUPABASE_URL"
    echo "   - VITE_SUPABASE_ANON_KEY"
    echo ""
    read -p "Drücke Enter wenn du die .env Datei konfiguriert hast..."
fi

# Build und starte Container
echo "🔨 Building Docker Image..."
docker-compose build

echo "🚀 Starting Cookify API..."
docker-compose up -d

echo ""
echo "✅ Cookify API läuft jetzt!"
echo "🌐 API verfügbar unter: http://localhost:8000"
echo "📋 Health Check: http://localhost:8000/health"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Container Status:"
docker-compose ps

echo ""
echo "📝 Nützliche Befehle:"
echo "  docker-compose logs -f          # Logs anzeigen"
echo "  docker-compose stop             # Container stoppen"
echo "  docker-compose down             # Container stoppen und entfernen"
echo "  docker-compose restart          # Container neustarten"
