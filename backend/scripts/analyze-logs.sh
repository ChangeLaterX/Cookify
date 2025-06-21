#!/bin/bash

# Log Analysis Script for Cookify Backend
# Analyzes backend logs for debugging and monitoring

set -e

echo "📋 Cookify Backend Log Analysis"
echo "==============================="

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
ANALYSIS_TYPE="summary"
TIME_RANGE="24h"
LOG_LEVEL="all"
OUTPUT_FILE=""
EXPORT_FORMAT="text"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            ANALYSIS_TYPE="$2"
            shift 2
            ;;
        -r|--range)
            TIME_RANGE="$2"
            shift 2
            ;;
        -l|--level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -f|--format)
            EXPORT_FORMAT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -t, --type             Analysis type (summary, errors, performance, requests)"
            echo "  -r, --range            Time range (1h, 6h, 24h, 7d, 30d)"
            echo "  -l, --level            Log level filter (all, debug, info, warning, error, critical)"
            echo "  -o, --output           Output file path"
            echo "  -f, --format           Export format (text, json, csv)"
            echo "  -h, --help             Show this help message"
            echo ""
            echo "Analysis types:"
            echo "  summary                General log summary"
            echo "  errors                 Error analysis and patterns"
            echo "  performance            Performance metrics analysis"
            echo "  requests               HTTP request analysis"
            echo "  users                  User activity analysis"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if logs directory exists
if [ ! -d "logs" ]; then
    print_error "No logs directory found. Run the application first to generate logs."
    exit 1
fi

# Convert time range to find command format
case $TIME_RANGE in
    1h)
        FIND_TIME="-mmin -60"
        ;;
    6h)
        FIND_TIME="-mmin -360"
        ;;
    24h)
        FIND_TIME="-mtime -1"
        ;;
    7d)
        FIND_TIME="-mtime -7"
        ;;
    30d)
        FIND_TIME="-mtime -30"
        ;;
    *)
        print_error "Invalid time range: $TIME_RANGE"
        exit 1
        ;;
esac

print_status "Analyzing logs for the last $TIME_RANGE"

# Function to get log files in time range
get_log_files() {
    find logs/ -name "*.log" $FIND_TIME 2>/dev/null | sort
}

# Function to filter by log level
filter_by_level() {
    local input="$1"
    
    case $LOG_LEVEL in
        all)
            echo "$input"
            ;;
        debug)
            echo "$input" | grep -i "\[DEBUG\]" || true
            ;;
        info)
            echo "$input" | grep -i "\[INFO\]" || true
            ;;
        warning)
            echo "$input" | grep -i "\[WARNING\]\|\[WARN\]" || true
            ;;
        error)
            echo "$input" | grep -i "\[ERROR\]" || true
            ;;
        critical)
            echo "$input" | grep -i "\[CRITICAL\]\|\[FATAL\]" || true
            ;;
        *)
            echo "$input"
            ;;
    esac
}

# Function to perform summary analysis
analyze_summary() {
    print_status "Performing summary analysis..."
    
    local log_files=$(get_log_files)
    
    if [ -z "$log_files" ]; then
        print_warning "No log files found in the specified time range"
        return
    fi
    
    echo "Log Summary Analysis"
    echo "===================="
    echo "Time Range: $TIME_RANGE"
    echo "Log Level Filter: $LOG_LEVEL"
    echo ""
    
    # Count log entries by level
    echo "Log Entries by Level:"
    echo "--------------------"
    local all_logs=$(cat $log_files 2>/dev/null || true)
    
    echo "DEBUG:    $(echo "$all_logs" | grep -c "\[DEBUG\]" || echo 0)"
    echo "INFO:     $(echo "$all_logs" | grep -c "\[INFO\]" || echo 0)"
    echo "WARNING:  $(echo "$all_logs" | grep -c "\[WARNING\]\|\[WARN\]" || echo 0)"
    echo "ERROR:    $(echo "$all_logs" | grep -c "\[ERROR\]" || echo 0)"
    echo "CRITICAL: $(echo "$all_logs" | grep -c "\[CRITICAL\]\|\[FATAL\]" || echo 0)"
    echo ""
    
    # Most active endpoints
    echo "Most Active Endpoints:"
    echo "---------------------"
    echo "$all_logs" | grep -o "\"[A-Z]* [^\"]*\"" | sort | uniq -c | sort -nr | head -10 || true
    echo ""
    
    # Response codes
    echo "HTTP Response Codes:"
    echo "-------------------"
    echo "$all_logs" | grep -o " [0-9]\{3\} " | sort | uniq -c | sort -nr || true
    echo ""
    
    # Recent errors
    echo "Recent Errors (last 10):"
    echo "------------------------"
    echo "$all_logs" | grep -i "\[ERROR\]\|\[CRITICAL\]" | tail -10 || echo "No errors found"
}

# Function to analyze errors
analyze_errors() {
    print_status "Performing error analysis..."
    
    local log_files=$(get_log_files)
    local all_logs=$(cat $log_files 2>/dev/null || true)
    local errors=$(echo "$all_logs" | grep -i "\[ERROR\]\|\[CRITICAL\]\|exception\|traceback" || true)
    
    echo "Error Analysis"
    echo "=============="
    echo ""
    
    if [ -z "$errors" ]; then
        print_success "No errors found in the specified time range!"
        return
    fi
    
    # Error count
    local error_count=$(echo "$errors" | wc -l)
    echo "Total Errors: $error_count"
    echo ""
    
    # Error patterns
    echo "Common Error Patterns:"
    echo "---------------------"
    echo "$errors" | grep -o "Exception: [^,]*" | sort | uniq -c | sort -nr | head -10 || true
    echo ""
    
    # Recent errors with context
    echo "Recent Errors with Context:"
    echo "--------------------------"
    echo "$errors" | tail -20
}

# Function to analyze performance
analyze_performance() {
    print_status "Performing performance analysis..."
    
    local log_files=$(get_log_files)
    local all_logs=$(cat $log_files 2>/dev/null || true)
    
    echo "Performance Analysis"
    echo "==================="
    echo ""
    
    # Response times (if logged)
    echo "Response Time Analysis:"
    echo "----------------------"
    local response_times=$(echo "$all_logs" | grep -o "response_time: [0-9.]*" | cut -d' ' -f2 || true)
    
    if [ ! -z "$response_times" ]; then
        python3 -c "
import sys
import statistics

times = []
for line in sys.stdin:
    try:
        times.append(float(line.strip()))
    except:
        pass

if times:
    print(f'Average Response Time: {statistics.mean(times):.3f}s')
    print(f'Median Response Time: {statistics.median(times):.3f}s')
    print(f'Min Response Time: {min(times):.3f}s')
    print(f'Max Response Time: {max(times):.3f}s')
    print(f'Total Requests: {len(times)}')
else:
    print('No response time data found')
" <<< "$response_times"
    else
        print_warning "No response time data found in logs"
    fi
    echo ""
    
    # Memory usage (if logged)
    echo "Memory Usage Patterns:"
    echo "---------------------"
    echo "$all_logs" | grep -i "memory\|RAM" | tail -10 || echo "No memory usage data found"
    echo ""
    
    # Slow queries (if logged)
    echo "Slow Operations:"
    echo "---------------"
    echo "$all_logs" | grep -i "slow\|timeout" | tail -10 || echo "No slow operations found"
}

# Function to analyze requests
analyze_requests() {
    print_status "Performing request analysis..."
    
    local log_files=$(get_log_files)
    local all_logs=$(cat $log_files 2>/dev/null || true)
    
    echo "HTTP Request Analysis"
    echo "===================="
    echo ""
    
    # Request methods
    echo "Request Methods:"
    echo "---------------"
    echo "$all_logs" | grep -o "\"[A-Z]* " | sort | uniq -c | sort -nr || true
    echo ""
    
    # Response codes
    echo "Response Code Distribution:"
    echo "--------------------------"
    echo "$all_logs" | grep -o " [0-9]\{3\} " | sort | uniq -c | sort -nr || true
    echo ""
    
    # User agents (simplified)
    echo "Top User Agents:"
    echo "---------------"
    echo "$all_logs" | grep -o "User-Agent: [^\"]*" | cut -d' ' -f2- | sort | uniq -c | sort -nr | head -5 || true
    echo ""
    
    # Request frequency by hour
    echo "Request Frequency by Hour:"
    echo "-------------------------"
    echo "$all_logs" | grep -o "[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\} [0-9]\{2\}:" | sort | uniq -c || true
}

# Function to export results
export_results() {
    local content="$1"
    
    if [ ! -z "$OUTPUT_FILE" ]; then
        case $EXPORT_FORMAT in
            json)
                # Convert to JSON format
                python3 -c "
import json
import sys

result = {
    'analysis_type': '$ANALYSIS_TYPE',
    'time_range': '$TIME_RANGE',
    'log_level': '$LOG_LEVEL',
    'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
    'content': '''$content'''
}

with open('$OUTPUT_FILE', 'w') as f:
    json.dump(result, f, indent=2)

print('Results exported to: $OUTPUT_FILE')
"
                ;;
            csv)
                # Simple CSV export (limited)
                echo "timestamp,level,message" > "$OUTPUT_FILE"
                echo "$content" | grep -E "\[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\]" | \
                sed 's/\[/,/; s/\]/,/' >> "$OUTPUT_FILE" 2>/dev/null || true
                print_success "Results exported to: $OUTPUT_FILE"
                ;;
            text|*)
                echo "$content" > "$OUTPUT_FILE"
                print_success "Results exported to: $OUTPUT_FILE"
                ;;
        esac
    fi
}

# Main analysis execution
case $ANALYSIS_TYPE in
    summary)
        result=$(analyze_summary)
        ;;
    errors)
        result=$(analyze_errors)
        ;;
    performance)
        result=$(analyze_performance)
        ;;
    requests)
        result=$(analyze_requests)
        ;;
    *)
        print_error "Unknown analysis type: $ANALYSIS_TYPE"
        exit 1
        ;;
esac

# Display results
echo "$result"

# Export if requested
if [ ! -z "$OUTPUT_FILE" ]; then
    export_results "$result"
fi

echo ""
print_success "Log analysis completed!"
echo ""
echo "For more detailed analysis, try:"
echo "./scripts/analyze-logs.sh --help"
echo "./scripts/analyze-logs.sh --type errors --range 7d"
echo "./scripts/analyze-logs.sh --type performance --output report.json --format json"
