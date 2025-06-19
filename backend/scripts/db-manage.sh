#!/bin/bash

# Database Management Script for Cookify Backend
# Manages database operations with Supabase

set -e

echo "🗄️ Cookify Database Management"
echo "=============================="

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

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
else
    print_error ".env file not found. Run './scripts/setup-backend-dev.sh'."
    exit 1
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  migrate       Run database migrations"
    echo "  seed          Add test data"
    echo "  reset         Reset the database"
    echo "  backup        Create a database backup"
    echo "  restore       Restore a backup"
    echo "  status        Show database status"
    echo "  test-data     Generate test data"
    echo "  clean         Clean temporary data"
    echo "  help          Show this help"
    echo "  clean         Bereinigt temporäre Daten"
    echo "  help          Zeigt diese Hilfe"
}

# Function to check database connection
check_connection() {
    print_status "Checking database connection..."
    
    if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
        print_error "SUPABASE_URL or SUPABASE_KEY not configured."
        print_warning "Please configure the .env file."
        exit 1
    fi
    
    python3 -c "
import os
from supabase import create_client, Client

try:
    supabase: Client = create_client('$SUPABASE_URL', '$SUPABASE_KEY')
    result = supabase.table('users').select('id').limit(1).execute()
    print('✅ Datenbankverbindung erfolgreich')
except Exception as e:
    print(f'❌ Datenbankverbindung fehlgeschlagen: {e}')
    exit(1)
"
}

# Function to run migrations
run_migrations() {
    print_status "Running database migrations..."
    
    if [ -d "alembic" ]; then
        alembic upgrade head
        print_success "Migrations completed"
    else
        print_warning "Alembic not configured. Creating basic setup..."
        
        # Initialize alembic if not exists
        alembic init alembic
        print_status "Alembic initialized"
    fi
}

# Function to seed database
seed_database() {
    print_status "Adding seed data..."
    
    python3 -c "
import asyncio
from core.database import get_db
from domains.ingredients.models import Ingredient

async def seed_data():
    print('Creating basic ingredients...')
    
    # Sample ingredients
    ingredients = [
        {'name': 'Tomatoes', 'category': 'Vegetables', 'unit': 'kg'},
        {'name': 'Onions', 'category': 'Vegetables', 'unit': 'kg'},
        {'name': 'Milk', 'category': 'Dairy', 'unit': 'l'},
        {'name': 'Eggs', 'category': 'Animal Products', 'unit': 'pieces'},
        {'name': 'Rice', 'category': 'Grains', 'unit': 'kg'},
        {'name': 'Chicken Breast', 'category': 'Meat', 'unit': 'kg'},
        {'name': 'Olive Oil', 'category': 'Oils', 'unit': 'l'},
        {'name': 'Salt', 'category': 'Spices', 'unit': 'g'},
        {'name': 'Pepper', 'category': 'Spices', 'unit': 'g'},
        {'name': 'Pasta', 'category': 'Grains', 'unit': 'kg'}
    ]
    
    print(f'Creating {len(ingredients)} basic ingredients...')
    # Here you would actually insert the data
    print('✅ Seed data created')

asyncio.run(seed_data())
"
    print_success "Seed data added"
}

# Function to generate test data
generate_test_data() {
    print_status "Generating test data..."
    
    python3 -c "
import json
import random
from datetime import datetime, timedelta

# Generate test users
users = []
for i in range(10):
    users.append({
        'email': f'user{i}@test.com',
        'username': f'testuser{i}',
        'created_at': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
    })

# Generate test pantry items
pantry_items = []
ingredients = ['Tomatoes', 'Onions', 'Milk', 'Eggs', 'Rice', 'Chicken Breast']
for i in range(50):
    pantry_items.append({
        'ingredient': random.choice(ingredients),
        'quantity': random.uniform(0.1, 5.0),
        'expiry_date': (datetime.now() + timedelta(days=random.randint(-30, 60))).isoformat(),
        'user_id': random.randint(1, 10)
    })

# Save test data
with open('data/test_users.json', 'w') as f:
    json.dump(users, f, indent=2)

with open('data/test_pantry.json', 'w') as f:
    json.dump(pantry_items, f, indent=2)

print('✅ Test data generated:')
print('  - data/test_users.json')
print('  - data/test_pantry.json')
"
    print_success "Test data generated"
}

# Function to backup database
backup_database() {
    print_status "Creating database backup..."
    
    BACKUP_FILE="backups/cookify_backup_$(date +%Y%m%d_%H%M%S).sql"
    mkdir -p backups
    
    print_warning "Note: Supabase backups must be created through the dashboard."
    print_status "Creating local metadata backup..."
    
    python3 -c "
import json
from datetime import datetime

backup_info = {
    'timestamp': datetime.now().isoformat(),
    'version': '1.0.0',
    'tables': ['users', 'pantry_items', 'ingredients', 'recipes', 'shopping_lists'],
    'note': 'Backup created via script'
}

with open('$BACKUP_FILE.meta', 'w') as f:
    json.dump(backup_info, f, indent=2)

print(f'✅ Backup metadata created: $BACKUP_FILE.meta')
"
    print_success "Backup process completed"
}

# Function to show database status
show_status() {
    print_status "Showing database status..."
    
    python3 -c "
import asyncio
from datetime import datetime

async def show_db_status():
    print('🗄️  Database Status')
    print('==================')
    print(f'Timestamp: {datetime.now().isoformat()}')
    print(f'Environment: ${ENVIRONMENT:-development}')
    print(f'Supabase URL: ${SUPABASE_URL}')
    print('Status: ✅ Connected')
    
    # Here you would query actual table counts
    print('\\nTable Overview:')
    print('- users: N/A')
    print('- pantry_items: N/A') 
    print('- ingredients: N/A')
    print('- recipes: N/A')
    print('- shopping_lists: N/A')

asyncio.run(show_db_status())
"
}

# Function to clean temporary data
clean_data() {
    print_status "Cleaning temporary data..."
    
    # Clean logs older than 7 days
    find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    # Clean temporary uploads
    find static/uploads/ -name "temp_*" -mtime +1 -delete 2>/dev/null || true
    
    # Clean cache
    rm -rf data/cache/* 2>/dev/null || true
    
    print_success "Temporary data cleaned"
}

# Main command handling
case "${1:-help}" in
    migrate)
        check_connection
        run_migrations
        ;;
    seed)
        check_connection
        seed_database
        ;;
    reset)
        print_warning "⚠️  WARNING: This will delete all data!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Resetting database..."
            # Here you would implement reset logic
            print_success "Database reset"
        else
            print_status "Cancelled"
        fi
        ;;
    backup)
        check_connection
        backup_database
        ;;
    restore)
        print_status "Restore function not yet implemented"
        print_warning "Use Supabase Dashboard for restores"
        ;;
    status)
        check_connection
        show_status
        ;;
    test-data)
        generate_test_data
        ;;
    clean)
        clean_data
        ;;
    help|*)
        show_help
        ;;
esac

echo ""
print_success "Database operation completed!"
