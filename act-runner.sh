#!/bin/bash
# ACT Helper Script für Cookify Backend Tests
# Usage: ./act-runner.sh [job-name] [options]

set -e

PROJECT_DIR="/home/cipher/dev/Cookify"
ENV_FILE="$PROJECT_DIR/.env.act"

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktion für farbige Ausgabe
print_colored() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Hilfe anzeigen
show_help() {
    print_colored $BLUE "🚀 ACT RUNNER FÜR COOKIFY BACKEND"
    echo "================================"
    echo ""
    echo "Usage: $0 [job-name] [act-options]"
    echo ""
    print_colored $YELLOW "📋 VERFÜGBARE JOBS:"
    echo "  code-quality      - Code-Formatierung, Linting, Security"
    echo "  unit-tests        - Unit Tests für alle Domains"
    echo "  security-tests    - Sicherheitsscans"
    echo "  integration-tests - Integration Tests (benötigt DB)"
    echo "  performance-tests - Performance & Benchmarks"
    echo "  coverage-report   - Coverage-Analyse"
    echo "  endpoint-tests    - API-Endpoint Tests"
    echo "  docker-tests      - Docker Build Tests"
    echo "  test-summary      - Zusammenfassung aller Tests"
    echo "  all               - Alle Jobs ausführen"
    echo ""
    print_colored $YELLOW "🔧 BEISPIELE:"
    echo "  $0 code-quality              # Nur Code Quality"
    echo "  $0 unit-tests --verbose      # Unit Tests mit Details"
    echo "  $0 all --reuse              # Alle Jobs, Container wiederverwenden"
    echo "  $0 code-quality -n          # Dry-run"
    echo ""
    print_colored $YELLOW "💡 NÜTZLICHE FLAGS:"
    echo "  -n, --dryrun    : Nur anzeigen, was ausgeführt würde"
    echo "  --verbose       : Detaillierte Ausgabe"
    echo "  --reuse         : Container wiederverwenden (schneller)"
    echo "  --pull          : Images immer neu pullen"
    echo ""
}

# Job validieren
validate_job() {
    local job=$1
    local valid_jobs=("code-quality" "unit-tests" "security-tests" "integration-tests" "performance-tests" "coverage-report" "endpoint-tests" "docker-tests" "test-summary" "all")
    
    for valid_job in "${valid_jobs[@]}"; do
        if [[ "$job" == "$valid_job" ]]; then
            return 0
        fi
    done
    return 1
}

# Hauptlogik
main() {
    cd "$PROJECT_DIR"
    
    # Keine Argumente -> Hilfe anzeigen
    if [[ $# -eq 0 ]]; then
        show_help
        exit 0
    fi
    
    local job_name=$1
    shift # Entferne ersten Parameter
    
    # Hilfe anzeigen
    if [[ "$job_name" == "--help" ]] || [[ "$job_name" == "-h" ]]; then
        show_help
        exit 0
    fi
    
    # Job validieren
    if ! validate_job "$job_name"; then
        print_colored $RED "❌ Unbekannter Job: $job_name"
        echo ""
        show_help
        exit 1
    fi
    
    # Umgebungsdatei prüfen
    if [[ ! -f "$ENV_FILE" ]]; then
        print_colored $RED "❌ Environment-Datei nicht gefunden: $ENV_FILE"
        exit 1
    fi
    
    # Docker prüfen
    if ! docker info >/dev/null 2>&1; then
        print_colored $RED "❌ Docker ist nicht verfügbar oder nicht gestartet"
        exit 1
    fi
    
    print_colored $GREEN "🚀 STARTE ACT JOB: $job_name"
    print_colored $BLUE "📁 Projekt-Verzeichnis: $PROJECT_DIR"
    print_colored $BLUE "🔧 Environment-Datei: $ENV_FILE"
    echo ""
    
    # ACT-Befehl zusammenbauen
    local act_cmd="act --env-file '$ENV_FILE'"
    
    if [[ "$job_name" != "all" ]]; then
        act_cmd="$act_cmd -j $job_name"
    fi
    
    # Zusätzliche Parameter hinzufügen
    act_cmd="$act_cmd $*"
    
    print_colored $YELLOW "🔄 Ausführung: $act_cmd"
    echo ""
    
    # ACT ausführen
    eval $act_cmd
    
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        print_colored $GREEN "✅ Job '$job_name' erfolgreich abgeschlossen!"
    else
        print_colored $RED "❌ Job '$job_name' fehlgeschlagen (Exit Code: $exit_code)"
    fi
    
    return $exit_code
}

# Script ausführen
main "$@"
