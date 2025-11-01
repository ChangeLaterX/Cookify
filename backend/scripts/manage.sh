#!/bin/bash

# Cookify Backend Script Manager
# Central access to all backend scripts

set -e

echo "🛠️ Cookify Backend Script Manager"
echo "================================="

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

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Available Commands:"
    echo "=================="
    echo ""
    echo "Development & Setup:"
    echo "  setup              Setup development environment"
    echo "  test               Run tests with various options"
    echo "  monitor            Monitor backend health and performance"
    echo ""
    echo "Database Management:"
    echo "  db                 Database operations (migrate, seed, backup, etc.)"
    echo ""
    echo "Deployment & Operations:"
    echo "  deploy             Deploy to staging/production"
    echo "  backup             Create backups of code, data, and config"
    echo ""
    echo "Analysis & Debugging:"
    echo "  logs               Analyze log files"
    echo "  perf-config        Configure performance tests"
    echo ""
    echo "Utility:"
    echo "  list               List all available scripts"
    echo "  help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup                    # Setup development environment"
    echo "  $0 test --coverage          # Run tests with coverage"
    echo "  $0 db migrate               # Run database migrations"
    echo "  $0 deploy --env staging     # Deploy to staging"
    echo "  $0 monitor --continuous     # Start continuous monitoring"
    echo "  $0 logs --type errors       # Analyze error logs"
    echo "  $0 backup --type full       # Create full backup"
    echo ""
    echo "For detailed help on specific commands, use:"
    echo "  $0 [COMMAND] --help"
}

# Function to list all scripts
list_scripts() {
    echo "Available Backend Scripts:"
    echo "=========================="
    echo ""
    
    if [ -d "scripts" ]; then
        for script in scripts/*.sh; do
            if [ -f "$script" ] && [ -x "$script" ]; then
                script_name=$(basename "$script" .sh)
                echo "  $script_name"
                
                # Try to extract description from script
                description=$(head -10 "$script" | grep "^#" | grep -v "#!/bin/bash" | head -1 | sed 's/^# *//' || echo "")
                if [ ! -z "$description" ]; then
                    echo "    $description"
                fi
                echo ""
            fi
        done
    fi
    
    # Also list root scripts
    echo "Root Backend Scripts:"
    echo "===================="
    for script in *.sh; do
        if [ -f "$script" ] && [ -x "$script" ]; then
            script_name=$(basename "$script" .sh)
            echo "  $script_name"
            
            description=$(head -10 "$script" | grep "^#" | grep -v "#!/bin/bash" | head -1 | sed 's/^# *//' || echo "")
            if [ ! -z "$description" ]; then
                echo "    $description"
            fi
            echo ""
        fi
    done
}

# Function to check script availability
check_script() {
    local script_path="$1"
    
    if [ ! -f "$script_path" ]; then
        print_error "Script not found: $script_path"
        return 1
    fi
    
    if [ ! -x "$script_path" ]; then
        print_warning "Making script executable: $script_path"
        chmod +x "$script_path"
    fi
    
    return 0
}

# Main command handling
case "${1:-help}" in
    setup)
        shift
        script_path="scripts/setup-backend-dev.sh"
        if check_script "$script_path"; then
            exec "$script_path" "$@"
        fi
        ;;
    test)
        shift
        script_path="scripts/run-tests.sh"
        if check_script "$script_path"; then
            exec "$script_path" "$@"
        fi
        ;;
    monitor)
        shift
        script_path="scripts/monitor.sh"
        if check_script "$script_path"; then
            exec "$script_path" "$@"
        fi
        ;;
    db)
        shift
        script_path="scripts/db-manage.sh"
        if check_script "$script_path"; then
            exec "$script_path" "$@"
        fi
        ;;
    deploy)
        shift
        script_path="scripts/deploy.sh"
        if check_script "$script_path"; then
            exec "$script_path" "$@"
        fi
        ;;
    backup)
        shift
        script_path="scripts/backup.sh"
        if check_script "$script_path"; then
            exec "$script_path" "$@"
        fi
        ;;
    logs)
        shift
        script_path="scripts/analyze-logs.sh"
        if check_script "$script_path"; then
            exec "$script_path" "$@"
        fi
        ;;
    perf-config)
        shift
        script_path="scripts/configure_performance_tests.sh"
        if check_script "$script_path"; then
            exec "$script_path" "$@"
        fi
        ;;
    list)
        list_scripts
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        if [ ! -z "$1" ]; then
            print_error "Unknown command: $1"
            echo ""
        fi
        show_help
        exit 1
        ;;
esac
