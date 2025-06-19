#!/bin/bash

# Backend Development Setup Script
# Sets up the backend development environment

set -e

echo "🐍 Cookify Backend Development Setup"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Navigate to backend directory
cd "$(dirname "$0")/.."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

print_success "Python 3 found: $(python3 --version)"

# Display active conda environment
if command -v conda &> /dev/null; then
    ACTIVE_CONDA_ENV=$(conda info --envs | grep '*' | awk '{print $1}')
    if [ -n "$ACTIVE_CONDA_ENV" ]; then
        print_warning "Active Conda environment: $ACTIVE_CONDA_ENV"
        print_warning "Please deactivate the Conda environment before continuing."
        exit 1
    fi
else
    print_warning "Conda is not installed. Continuing without Conda."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python Virtual Environment..."
    python3 -m venv venv
    print_success "Virtual Environment created"
else
    print_warning "Virtual Environment already exists"
fi

# Activate virtual environment
print_status "Activating Virtual Environment..."
source venv/bin/activate

# Upgrade pip
print_status "Updating pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing Python Dependencies..."
pip install -r requirements.txt

# Install development dependencies
print_status "Installing Development Dependencies..."
pip install pytest-cov black flake8 mypy isort pre-commit

print_success "All Dependencies installed"

# Setup environment file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Created .env file from .env.example. Please configure your environment variables."
    else
        print_status "Creating default .env file..."
        cat > .env << EOF
# Cookify Backend Environment Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Database
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=Cookify Backend

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000","http://localhost:8080","http://127.0.0.1:8080"]

# OCR Settings
OCR_LANGUAGE=deu+eng
OCR_CONFIG=--oem 3 --psm 6
EOF
        print_warning "Default .env file created. Please configure your environment variables."
    fi
else
    print_warning ".env file already exists"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p static/uploads
mkdir -p static/exports
mkdir -p data/cache
print_success "Directories created"

# Setup pre-commit hooks
print_status "Configuring Pre-Commit Hooks..."
if [ ! -f ".pre-commit-config.yaml" ]; then
    cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
EOF
fi

pre-commit install
print_success "Pre-Commit Hooks installed"

# Run initial tests to verify setup
print_status "Running test setup..."
if [ -d "tests" ]; then
    python -m pytest tests/ --tb=short -v || print_warning "Some tests failed - this is normal during initial setup"
else
    print_warning "No tests/ directory found"
fi

echo ""
print_success "🎉 Backend Development Setup completed!"
echo ""
echo "Next steps:"
echo "1. Configure the .env file with your credentials"
echo "2. Start the server: uvicorn main:app --reload"
echo "3. Or use Docker: ./start-docker.sh"
echo ""
echo "Useful commands:"
echo "- source venv/bin/activate  # Activate Virtual Environment"
echo "- uvicorn main:app --reload # Start Development Server"
echo "- pytest                   # Run tests"
echo "- black .                  # Format code"
echo "- flake8 .                 # Linting"
echo "- ./scripts/run-tests.sh   # Run all tests"
