#!/bin/bash

# ===================================================================
# COOKIFY DEVELOPMENT SERVER DEPLOYMENT SCRIPT
# Optimized for /server/Cookify/backend
# ===================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="/server/Cookify/backend"
BRANCH="dev"
COMPOSE_FILE="docker-compose.dev.yml"
CONTAINER_NAME="cookify_api_dev"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Change to backend directory
cd "$BACKEND_DIR" || {
    log_error "Cannot access $BACKEND_DIR"
    exit 1
}

log_info "🚀 Starting Cookify Development Deployment..."
log_info "Working directory: $(pwd)"
log_info "Target branch: $BRANCH"

# === STEP 1: Stop existing containers ===
log_info "📦 Stopping existing containers..."
if docker-compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null; then
    log_success "Containers stopped successfully"
else
    log_warning "No running containers found or error stopping"
fi

# === STEP 2: Update code from Git ===
log_info "📥 Updating code from Git..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    log_error "Not a git repository!"
    exit 1
fi

# Switch to dev branch
if git checkout "$BRANCH"; then
    log_success "Switched to branch: $BRANCH"
else
    log_error "Failed to checkout branch: $BRANCH"
    exit 1
fi

# Get current commit before pull
OLD_COMMIT=$(git rev-parse HEAD)
OLD_COMMIT_SHORT=$(git rev-parse --short HEAD)

# Pull latest changes
if git pull origin "$BRANCH"; then
    NEW_COMMIT=$(git rev-parse HEAD)
    NEW_COMMIT_SHORT=$(git rev-parse --short HEAD)
    
    if [ "$OLD_COMMIT" != "$NEW_COMMIT" ]; then
        log_success "Updated from $OLD_COMMIT_SHORT to $NEW_COMMIT_SHORT"
        log_info "Recent changes:"
        git log --oneline "$OLD_COMMIT..$NEW_COMMIT" | head -5
    else
        log_info "No new changes (already up to date)"
    fi
else
    log_error "Failed to pull from origin/$BRANCH"
    exit 1
fi

# === STEP 3: Check and prepare environment ===
log_info "⚙️ Preparing environment..."

# Check if .env.development exists
if [ ! -f ".env.development" ]; then
    log_warning ".env.development not found, creating from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env.development
        log_info "Please edit .env.development with your configuration"
    else
        log_error "No environment template found!"
        exit 1
    fi
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# === STEP 4: Build and start containers ===
log_info "🔨 Building and starting containers..."

# Build with no cache to ensure latest changes
if docker-compose -f "$COMPOSE_FILE" build --no-cache; then
    log_success "Container built successfully"
else
    log_error "Failed to build container"
    exit 1
fi

# Start services
if docker-compose -f "$COMPOSE_FILE" up -d; then
    log_success "Services started successfully"
else
    log_error "Failed to start services"
    exit 1
fi

# === STEP 5: Wait for health check ===
log_info "🏥 Waiting for application to become healthy..."

HEALTH_CHECK_TIMEOUT=60
HEALTH_CHECK_INTERVAL=5
elapsed=0
healthy=false

while [[ $elapsed -lt $HEALTH_CHECK_TIMEOUT ]]; do
    if docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null | grep -q "healthy"; then
        healthy=true
        break
    fi
    
    if docker ps --filter "name=$CONTAINER_NAME" --filter "status=running" --quiet | grep -q .; then
        log_info "Container running, waiting for health check... (${elapsed}s/${HEALTH_CHECK_TIMEOUT}s)"
    else
        log_error "Container is not running!"
        log_info "Recent logs:"
        docker-compose -f "$COMPOSE_FILE" logs --tail=20 cookify-api-dev
        exit 1
    fi
    
    sleep $HEALTH_CHECK_INTERVAL
    elapsed=$((elapsed + HEALTH_CHECK_INTERVAL))
done

if [[ $healthy == true ]]; then
    log_success "Application is healthy and ready!"
else
    log_warning "Application may not be fully healthy yet"
    log_info "Recent logs:"
    docker-compose -f "$COMPOSE_FILE" logs --tail=20 cookify-api-dev
fi

# === STEP 6: Show deployment info ===
log_info "📊 Deployment Status:"
echo
echo "🌐 API URLs:"
echo "  - Main API: https://dev.krija.info:8000"
echo "  - Health: https://dev.krija.info:8000/api/health"  
echo "  - Docs: https://dev.krija.info:8000/docs"
echo
echo "📦 Container Info:"
docker-compose -f "$COMPOSE_FILE" ps
echo
echo "💾 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" "$CONTAINER_NAME" 2>/dev/null || echo "Stats not available"
echo

# === STEP 7: Run quick smoke test ===
log_info "🧪 Running quick smoke test..."

# Test health endpoint
if curl -f --max-time 10 "http://localhost:8000/api/health" >/dev/null 2>&1; then
    log_success "Health check endpoint responding"
else
    log_warning "Health check endpoint not responding (may be normal during startup)"
fi

log_success "🎉 Deployment completed successfully!"
log_info "Monitor logs with: docker-compose -f $COMPOSE_FILE logs -f"
log_info "Stop services with: docker-compose -f $COMPOSE_FILE down"

# Optional: Run security tests
if [ -f "scripts/test-ocr-security.sh" ]; then
    read -p "Run OCR security tests? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "🔒 Running security tests..."
        bash scripts/test-ocr-security.sh
    fi
fi
