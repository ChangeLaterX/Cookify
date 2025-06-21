#!/bin/bash

# Enhanced Docker Deployment Script for Cookify API
# Provides secure, production-ready deployment with health checks

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
CONTAINER_NAME="cookify_api"
IMAGE_NAME="cookify-api:latest"
HEALTH_CHECK_TIMEOUT=60
HEALTH_CHECK_INTERVAL=5

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

check_requirements() {
    log_info "Checking requirements..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if .env file exists
    if [[ ! -f .env ]]; then
        log_warning ".env file not found. Creating template..."
        create_env_template
    fi
    
    log_success "Requirements check passed"
}

create_env_template() {
    cat > .env << EOF
# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Application Configuration
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO

# Security Settings
JWT_SECRET=your_jwt_secret_here_min_32_chars
SESSION_SECRET_KEY=your_session_secret_here_min_32_chars

# OCR Security Settings
OCR_MAX_IMAGE_SIZE_BYTES=5242880
OCR_PROCESSING_TIMEOUT=30
RATE_LIMIT_OCR_ATTEMPTS=10
RATE_LIMIT_OCR_WINDOW_MINUTES=5

# CORS Settings (adjust for your frontend)
CORS_ORIGINS=["http://localhost:3000"]
TRUSTED_HOSTS=["localhost","127.0.0.1"]
EOF
    
    log_warning "Please edit .env file with your actual configuration values"
}

build_image() {
    log_info "Building Docker image..."
    
    # Enable BuildKit for better performance
    export DOCKER_BUILDKIT=1
    
    if docker-compose build --no-cache cookify-api; then
        log_success "Docker image built successfully"
    else
        log_error "Failed to build Docker image"
        exit 1
    fi
}

stop_existing() {
    log_info "Stopping existing containers..."
    
    if docker-compose down --remove-orphans; then
        log_success "Existing containers stopped"
    else
        log_warning "No existing containers found or failed to stop"
    fi
}

start_services() {
    log_info "Starting services..."
    
    # Create necessary directories
    mkdir -p logs
    
    if docker-compose up -d; then
        log_success "Services started successfully"
    else
        log_error "Failed to start services"
        exit 1
    fi
}

wait_for_health() {
    log_info "Waiting for application to become healthy..."
    
    local elapsed=0
    local healthy=false
    
    while [[ $elapsed -lt $HEALTH_CHECK_TIMEOUT ]]; do
        if docker inspect --format='{{.State.Health.Status}}' $CONTAINER_NAME 2>/dev/null | grep -q "healthy"; then
            healthy=true
            break
        fi
        
        if docker ps --filter "name=$CONTAINER_NAME" --filter "status=running" --quiet | grep -q .; then
            log_info "Container is running, waiting for health check... (${elapsed}s/${HEALTH_CHECK_TIMEOUT}s)"
        else
            log_error "Container is not running"
            show_logs
            exit 1
        fi
        
        sleep $HEALTH_CHECK_INTERVAL
        elapsed=$((elapsed + HEALTH_CHECK_INTERVAL))
    done
    
    if [[ $healthy == true ]]; then
        log_success "Application is healthy and ready to serve requests"
    else
        log_error "Application failed to become healthy within ${HEALTH_CHECK_TIMEOUT} seconds"
        show_logs
        exit 1
    fi
}

show_logs() {
    log_info "Recent container logs:"
    docker-compose logs --tail=50 cookify-api
}

show_status() {
    log_info "Current status:"
    echo
    docker-compose ps
    echo
    
    # Show resource usage
    if docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" $CONTAINER_NAME 2>/dev/null; then
        echo
    fi
    
    # Show health status
    local health_status=$(docker inspect --format='{{.State.Health.Status}}' $CONTAINER_NAME 2>/dev/null || echo "unknown")
    echo "Health Status: $health_status"
    
    # Show API endpoint
    echo "API URL: http://localhost:8000"
    echo "Health Check: http://localhost:8000/api/health"
    echo "API Docs: http://localhost:8000/docs"
}

run_security_tests() {
    log_info "Running security tests..."
    
    if [[ -f scripts/test-ocr-security.sh ]]; then
        bash scripts/test-ocr-security.sh
    else
        log_warning "Security test script not found"
    fi
}

cleanup() {
    log_info "Cleaning up Docker resources..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused networks
    docker network prune -f
    
    log_success "Cleanup completed"
}

# Main deployment function
deploy() {
    log_info "Starting Cookify API deployment..."
    
    check_requirements
    stop_existing
    build_image
    start_services
    wait_for_health
    show_status
    
    log_success "Deployment completed successfully!"
    log_info "You can now access the API at http://localhost:8000"
}

# Command line interface
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "start")
        start_services
        wait_for_health
        show_status
        ;;
    "stop")
        stop_existing
        ;;
    "restart")
        stop_existing
        start_services
        wait_for_health
        show_status
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "test")
        run_security_tests
        ;;
    "cleanup")
        cleanup
        ;;
    "build")
        build_image
        ;;
    *)
        echo "Usage: $0 {deploy|start|stop|restart|status|logs|test|cleanup|build}"
        echo
        echo "Commands:"
        echo "  deploy   - Full deployment (build, start, health check)"
        echo "  start    - Start services"
        echo "  stop     - Stop services"  
        echo "  restart  - Restart services"
        echo "  status   - Show current status"
        echo "  logs     - Show recent logs"
        echo "  test     - Run security tests"
        echo "  cleanup  - Clean up Docker resources"
        echo "  build    - Build Docker image only"
        exit 1
        ;;
esac
