#!/bin/bash

# Backup Script for Cookify Backend
# Creates backups of code, data and configurations

set -e

echo "💾 Cookify Backend Backup"
echo "========================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Navigate to backend directory
cd "$(dirname "$0")/.."

# Default values
BACKUP_TYPE="full"
BACKUP_DIR="../backups"
COMPRESS=true
CLEANUP_DAYS=30

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            BACKUP_TYPE="$2"
            shift 2
            ;;
        -d|--dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        --no-compress)
            COMPRESS=false
            shift
            ;;
        --cleanup-days)
            CLEANUP_DAYS="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -t, --type             Backup type (full, code, data, config)"
            echo "  -d, --dir              Backup directory (default: ../backups)"
            echo "  --no-compress          Don't compress backup files"
            echo "  --cleanup-days         Days to keep old backups (default: 30)"
            echo "  -h, --help             Show this help message"
            echo ""
            echo "Backup types:"
            echo "  full                   Complete backup (code + data + config)"
            echo "  code                   Source code and dependencies"
            echo "  data                   Data files and uploads"
            echo "  config                 Configuration files only"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create backup directory
mkdir -p "$BACKUP_DIR"
BACKUP_DIR=$(realpath "$BACKUP_DIR")

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="cookify_backend_${BACKUP_TYPE}_${TIMESTAMP}"

print_status "Creating $BACKUP_TYPE backup: $BACKUP_NAME"
print_status "Backup directory: $BACKUP_DIR"

# Create temporary backup directory
TEMP_BACKUP_DIR="/tmp/$BACKUP_NAME"
mkdir -p "$TEMP_BACKUP_DIR"

# Function to create backup manifest
create_manifest() {
    local manifest_file="$TEMP_BACKUP_DIR/backup_manifest.json"
    
    python3 -c "
import json
import os
from datetime import datetime
import subprocess

def get_git_info():
    try:
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                                       stderr=subprocess.DEVNULL).decode().strip()
        commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], 
                                       stderr=subprocess.DEVNULL).decode().strip()
        return {'branch': branch, 'commit': commit}
    except:
        return {'branch': 'unknown', 'commit': 'unknown'}

manifest = {
    'backup_info': {
        'name': '$BACKUP_NAME',
        'type': '$BACKUP_TYPE',
        'timestamp': datetime.now().isoformat(),
        'created_by': os.getenv('USER', 'unknown'),
        'hostname': os.uname().nodename
    },
    'git_info': get_git_info(),
    'environment': {
        'python_version': os.sys.version,
        'working_directory': os.getcwd()
    },
    'contents': []
}

with open('$manifest_file', 'w') as f:
    json.dump(manifest, f, indent=2)

print('Manifest created: $manifest_file')
"
}

# Function to backup code
backup_code() {
    print_status "Backing up source code..."
    
    local code_dir="$TEMP_BACKUP_DIR/code"
    mkdir -p "$code_dir"
    
    # Copy source code (excluding certain directories)
    rsync -av --exclude='venv' \
              --exclude='__pycache__' \
              --exclude='*.pyc' \
              --exclude='.git' \
              --exclude='logs' \
              --exclude='static/uploads' \
              --exclude='data/cache' \
              . "$code_dir/"
    
    # Copy requirements
    cp requirements.txt "$code_dir/" 2>/dev/null || true
    
    # Export pip freeze
    if [ -d "venv" ]; then
        source venv/bin/activate
        pip freeze > "$code_dir/requirements_frozen.txt"
    fi
    
    print_success "Source code backed up"
}

# Function to backup data
backup_data() {
    print_status "Backing up data files..."
    
    local data_dir="$TEMP_BACKUP_DIR/data"
    mkdir -p "$data_dir"
    
    # Backup data directory
    if [ -d "data" ]; then
        cp -r data/ "$data_dir/" 2>/dev/null || true
    fi
    
    # Backup static uploads
    if [ -d "static/uploads" ]; then
        mkdir -p "$data_dir/static"
        cp -r static/uploads/ "$data_dir/static/" 2>/dev/null || true
    fi
    
    # Backup logs (recent ones)
    if [ -d "logs" ]; then
        mkdir -p "$data_dir/logs"
        find logs/ -name "*.log" -mtime -7 -exec cp {} "$data_dir/logs/" \; 2>/dev/null || true
    fi
    
    # Create database export info (for Supabase)
    if [ -f ".env" ]; then
        source .env
        if [ ! -z "$SUPABASE_URL" ]; then
            cat > "$data_dir/database_info.txt" << EOF
Database Backup Information
===========================
Date: $(date)
Type: Supabase Database
URL: $SUPABASE_URL

Note: Supabase databases must be backed up through the Supabase dashboard.
This backup contains metadata and local data files only.

To restore database:
1. Access Supabase dashboard
2. Go to Settings > Database
3. Use the backup/restore functionality
EOF
        fi
    fi
    
    print_success "Data files backed up"
}

# Function to backup configuration
backup_config() {
    print_status "Backing up configuration files..."
    
    local config_dir="$TEMP_BACKUP_DIR/config"
    mkdir -p "$config_dir"
    
    # Copy configuration files
    cp .env.example "$config_dir/" 2>/dev/null || true
    cp docker-compose.yml "$config_dir/" 2>/dev/null || true
    cp Dockerfile "$config_dir/" 2>/dev/null || true
    
    # Copy environment files (without sensitive data)
    for env_file in .env.*; do
        if [ -f "$env_file" ]; then
            # Remove sensitive values
            sed 's/=.*/=***REDACTED***/' "$env_file" > "$config_dir/${env_file##*/}.template"
        fi
    done
    
    # Copy alembic configuration if exists
    if [ -f "alembic.ini" ]; then
        cp alembic.ini "$config_dir/"
    fi
    
    # Copy any script configurations
    if [ -d "scripts" ]; then
        cp -r scripts/ "$config_dir/"
    fi
    
    print_success "Configuration files backed up"
}

# Create manifest
create_manifest

# Perform backup based on type
case $BACKUP_TYPE in
    full)
        backup_code
        backup_data
        backup_config
        ;;
    code)
        backup_code
        ;;
    data)
        backup_data
        ;;
    config)
        backup_config
        ;;
    *)
        print_error "Unknown backup type: $BACKUP_TYPE"
        exit 1
        ;;
esac

# Create final backup file
FINAL_BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

if [ "$COMPRESS" = true ]; then
    print_status "Compressing backup..."
    tar -czf "$FINAL_BACKUP_PATH.tar.gz" -C "/tmp" "$BACKUP_NAME"
    FINAL_BACKUP_PATH="$FINAL_BACKUP_PATH.tar.gz"
    print_success "Backup compressed: $FINAL_BACKUP_PATH"
else
    mv "$TEMP_BACKUP_DIR" "$FINAL_BACKUP_PATH"
    print_success "Backup created: $FINAL_BACKUP_PATH"
fi

# Calculate backup size
BACKUP_SIZE=$(du -sh "$FINAL_BACKUP_PATH" | cut -f1)

# Cleanup temporary directory
rm -rf "$TEMP_BACKUP_DIR" 2>/dev/null || true

# Cleanup old backups
if [ "$CLEANUP_DAYS" -gt 0 ]; then
    print_status "Cleaning up backups older than $CLEANUP_DAYS days..."
    find "$BACKUP_DIR" -name "cookify_backend_*" -mtime +$CLEANUP_DAYS -delete 2>/dev/null || true
    print_success "Old backups cleaned up"
fi

# Generate backup summary
print_status "Generating backup summary..."

SUMMARY_FILE="$BACKUP_DIR/backup_summary.txt"
cat >> "$SUMMARY_FILE" << EOF
Backup Summary
==============
Date: $(date)
Type: $BACKUP_TYPE
Name: $BACKUP_NAME
Size: $BACKUP_SIZE
Path: $FINAL_BACKUP_PATH

EOF

echo ""
print_success "🎉 Backup completed successfully!"
echo ""
echo "Backup Summary:"
echo "==============="
echo "Type: $BACKUP_TYPE"
echo "Name: $BACKUP_NAME"
echo "Size: $BACKUP_SIZE"
echo "Path: $FINAL_BACKUP_PATH"
echo ""
echo "To restore this backup:"
if [ "$COMPRESS" = true ]; then
    echo "tar -xzf '$FINAL_BACKUP_PATH' -C /destination/path/"
else
    echo "cp -r '$FINAL_BACKUP_PATH' /destination/path/"
fi
echo ""
echo "Summary logged to: $SUMMARY_FILE"
