#!/bin/bash

# Backend Monitoring and Health Check Script
# Monitors backend health and performance

set -e

echo "📊 Cookify Backend Monitoring"
echo "============================="

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
CONTINUOUS=false
INTERVAL=30
LOG_FILE="logs/monitoring_$(date +%Y%m%d).log"
ALERT_THRESHOLD_CPU=80
ALERT_THRESHOLD_MEMORY=80

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--continuous)
            CONTINUOUS=true
            shift
            ;;
        -i|--interval)
            INTERVAL="$2"
            shift 2
            ;;
        -l|--log)
            LOG_FILE="$2"
            shift 2
            ;;
        --cpu-threshold)
            ALERT_THRESHOLD_CPU="$2"
            shift 2
            ;;
        --memory-threshold)
            ALERT_THRESHOLD_MEMORY="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -c, --continuous       Run continuously"
            echo "  -i, --interval         Monitoring interval in seconds (default: 30)"
            echo "  -l, --log              Log file path"
            echo "  --cpu-threshold        CPU alert threshold % (default: 80)"
            echo "  --memory-threshold     Memory alert threshold % (default: 80)"
            echo "  -h, --help             Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Ensure logs directory exists
mkdir -p logs

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to check system resources
check_system_resources() {
    print_status "Checking system resources..."
    
    # CPU usage
    CPU_USAGE=$(python3 -c "import psutil; print(f'{psutil.cpu_percent(interval=1):.1f}')")
    
    # Memory usage
    MEMORY_INFO=$(python3 -c "
import psutil
mem = psutil.virtual_memory()
print(f'{mem.percent:.1f} {mem.used//1024//1024} {mem.total//1024//1024}')
")
    MEMORY_PERCENT=$(echo $MEMORY_INFO | awk '{print $1}')
    MEMORY_USED=$(echo $MEMORY_INFO | awk '{print $2}')
    MEMORY_TOTAL=$(echo $MEMORY_INFO | awk '{print $3}')
    
    # Disk usage
    DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    
    echo "System Resources:"
    echo "=================="
    echo "CPU Usage: ${CPU_USAGE}%"
    echo "Memory Usage: ${MEMORY_PERCENT}% (${MEMORY_USED}MB / ${MEMORY_TOTAL}MB)"
    echo "Disk Usage: ${DISK_USAGE}%"
    
    # Check thresholds
    if (( $(echo "$CPU_USAGE > $ALERT_THRESHOLD_CPU" | bc -l) )); then
        print_warning "⚠️  High CPU usage: ${CPU_USAGE}%"
        log_message "ALERT: High CPU usage: ${CPU_USAGE}%"
    fi
    
    if (( $(echo "$MEMORY_PERCENT > $ALERT_THRESHOLD_MEMORY" | bc -l) )); then
        print_warning "⚠️  High memory usage: ${MEMORY_PERCENT}%"
        log_message "ALERT: High memory usage: ${MEMORY_PERCENT}%"
    fi
}

# Function to check application health
check_app_health() {
    print_status "Checking application health..."
    
    # Check if FastAPI is running
    if pgrep -f "uvicorn" > /dev/null; then
        print_success "✅ FastAPI process is running"
        
        # Get process info
        UVICORN_PID=$(pgrep -f "uvicorn" | head -1)
        PROCESS_INFO=$(python3 -c "
import psutil
try:
    p = psutil.Process($UVICORN_PID)
    print(f'PID: {p.pid}, CPU: {p.cpu_percent():.1f}%, Memory: {p.memory_info().rss//1024//1024}MB')
except:
    print('Process info unavailable')
")
        echo "FastAPI Process: $PROCESS_INFO"
    else
        print_error "❌ FastAPI process not running"
        log_message "ERROR: FastAPI process not running"
    fi
    
    # Check health endpoint
    if command -v curl &> /dev/null; then
        HEALTH_URL="http://localhost:8000/health"
        
        if curl -f -s "$HEALTH_URL" > /dev/null; then
            print_success "✅ Health endpoint responding"
            
            # Get detailed health info
            HEALTH_RESPONSE=$(curl -s "$HEALTH_URL" 2>/dev/null || echo '{}')
            echo "Health Response: $HEALTH_RESPONSE"
        else
            print_error "❌ Health endpoint not responding"
            log_message "ERROR: Health endpoint not responding"
        fi
    else
        print_warning "curl not available, skipping endpoint check"
    fi
}

# Function to check database connectivity
check_database() {
    print_status "Checking database connectivity..."
    
    if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
        print_warning "Supabase credentials not configured"
        return
    fi
    
    python3 -c "
import sys
import time
from supabase import create_client, Client

try:
    start_time = time.time()
    supabase: Client = create_client('$SUPABASE_URL', '$SUPABASE_KEY')
    result = supabase.table('users').select('id').limit(1).execute()
    response_time = (time.time() - start_time) * 1000
    
    print(f'✅ Database connection successful ({response_time:.0f}ms)')
    
    if response_time > 1000:
        print('⚠️  Slow database response time')
        
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
"
}

# Function to check log files for errors
check_logs() {
    print_status "Checking recent logs for errors..."
    
    if [ -d "logs" ]; then
        # Check for errors in last 100 lines of recent log files
        ERROR_COUNT=$(find logs/ -name "*.log" -mtime -1 -exec tail -100 {} \; | grep -i "error\|exception\|critical" | wc -l)
        
        if [ "$ERROR_COUNT" -gt 0 ]; then
            print_warning "⚠️  Found $ERROR_COUNT error entries in recent logs"
            
            # Show recent errors
            echo "Recent errors:"
            find logs/ -name "*.log" -mtime -1 -exec tail -100 {} \; | grep -i "error\|exception\|critical" | tail -5
        else
            print_success "✅ No recent errors in logs"
        fi
    else
        print_warning "No logs directory found"
    fi
}

# Function to check disk space
check_disk_space() {
    print_status "Checking disk space..."
    
    # Check main disk
    DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$DISK_USAGE" -gt 90 ]; then
        print_error "❌ Critical disk space: ${DISK_USAGE}% used"
        log_message "CRITICAL: Disk space critical: ${DISK_USAGE}%"
    elif [ "$DISK_USAGE" -gt 80 ]; then
        print_warning "⚠️  High disk usage: ${DISK_USAGE}%"
        log_message "WARNING: High disk usage: ${DISK_USAGE}%"
    else
        print_success "✅ Disk space OK: ${DISK_USAGE}% used"
    fi
    
    # Check log directory size
    if [ -d "logs" ]; then
        LOG_SIZE=$(du -sh logs/ | cut -f1)
        echo "Log directory size: $LOG_SIZE"
        
        # Check if logs are too large
        LOG_SIZE_MB=$(du -sm logs/ | cut -f1)
        if [ "$LOG_SIZE_MB" -gt 1000 ]; then
            print_warning "⚠️  Log directory is large: ${LOG_SIZE}MB"
        fi
    fi
}

# Function to generate monitoring report
generate_report() {
    REPORT_FILE="logs/health_report_$(date +%Y%m%d_%H%M%S).json"
    
    python3 -c "
import json
import psutil
from datetime import datetime

# Gather system info
cpu_percent = psutil.cpu_percent(interval=1)
memory = psutil.virtual_memory()
disk = psutil.disk_usage('.')

report = {
    'timestamp': datetime.now().isoformat(),
    'system': {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'memory_used_mb': memory.used // 1024 // 1024,
        'memory_total_mb': memory.total // 1024 // 1024,
        'disk_percent': (disk.used / disk.total) * 100,
        'disk_free_gb': disk.free // 1024 // 1024 // 1024
    },
    'alerts': []
}

# Add alerts
if cpu_percent > $ALERT_THRESHOLD_CPU:
    report['alerts'].append(f'High CPU usage: {cpu_percent}%')

if memory.percent > $ALERT_THRESHOLD_MEMORY:
    report['alerts'].append(f'High memory usage: {memory.percent}%')

with open('$REPORT_FILE', 'w') as f:
    json.dump(report, f, indent=2)

print(f'Report saved: $REPORT_FILE')
"
}

# Main monitoring function
run_monitoring() {
    echo "🔍 Starting health check at $(date)"
    echo "========================================"
    
    check_system_resources
    echo ""
    
    check_app_health
    echo ""
    
    check_database
    echo ""
    
    check_logs
    echo ""
    
    check_disk_space
    echo ""
    
    generate_report
    
    log_message "Health check completed"
    print_success "✅ Health check completed"
}

# Main execution
if [ "$CONTINUOUS" = true ]; then
    print_status "Starting continuous monitoring (interval: ${INTERVAL}s)"
    print_status "Press Ctrl+C to stop"
    
    while true; do
        run_monitoring
        echo ""
        print_status "Waiting ${INTERVAL} seconds..."
        sleep "$INTERVAL"
        echo ""
    done
else
    run_monitoring
fi

echo ""
echo "Monitoring log: $LOG_FILE"
