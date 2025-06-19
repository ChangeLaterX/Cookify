#!/bin/bash

# Deployment Script for Cookify Backend
# Automates the deployment process

set -e

echo "🚀 Cookify Backend Deployment"
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
ENVIRONMENT="staging"
SKIP_TESTS=false
SKIP_BUILD=false
DRY_RUN=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -e, --env          Target environment (staging, production)"
            echo "  --skip-tests       Skip running tests before deployment"
            echo "  --skip-build       Skip building Docker image"
            echo "  --dry-run          Show what would be done without executing"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_status "Deployment Target: $ENVIRONMENT"

if [ "$DRY_RUN" = true ]; then
    print_warning "DRY RUN - No actions will be executed"
fi

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    print_error "Invalid environment: $ENVIRONMENT. Use 'staging' or 'production'"
    exit 1
fi

# Check if git repo is clean
if [ "$DRY_RUN" = false ]; then
    if ! git diff-index --quiet HEAD --; then
        print_error "Git repository has uncommitted changes. Please commit or stash them."
        exit 1
    fi
    print_success "Git repository is clean"
fi

# Get current git info
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
GIT_COMMIT=$(git rev-parse --short HEAD)
GIT_TAG=$(git describe --tags --exact-match 2>/dev/null || echo "")

print_status "Git Branch: $GIT_BRANCH"
print_status "Git Commit: $GIT_COMMIT"
if [ -n "$GIT_TAG" ]; then
    print_status "Git Tag: $GIT_TAG"
fi

# Validate branch for production
if [[ "$ENVIRONMENT" == "production" && "$GIT_BRANCH" != "main" && -z "$GIT_TAG" ]]; then
    print_error "Production deployments must be from 'main' branch or a tagged release"
    exit 1
fi

# Load environment-specific configuration
ENV_FILE=".env.$ENVIRONMENT"
if [ -f "$ENV_FILE" ]; then
    print_status "Loading environment config: $ENV_FILE"
    export $(grep -v '^#' $ENV_FILE | xargs)
else
    print_warning "Environment file $ENV_FILE not found, using .env"
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run tests unless skipped
if [ "$SKIP_TESTS" = false ]; then
    print_status "Running tests before deployment..."
    if [ "$DRY_RUN" = false ]; then
        ./scripts/run-tests.sh --fast
        print_success "All tests passed"
    else
        print_status "[DRY RUN] Would run tests"
    fi
else
    print_warning "Skipping tests"
fi

# Check for security vulnerabilities
print_status "Checking for security vulnerabilities..."
if [ "$DRY_RUN" = false ]; then
    if command -v safety &> /dev/null; then
        safety check || print_warning "Security check found issues"
    else
        print_warning "Safety not installed, skipping security check"
    fi
else
    print_status "[DRY RUN] Would run security checks"
fi

# Build Docker image unless skipped
if [ "$SKIP_BUILD" = false ]; then
    print_status "Building Docker image..."
    
    IMAGE_TAG="cookify-backend:$ENVIRONMENT-$GIT_COMMIT"
    if [ -n "$GIT_TAG" ]; then
        IMAGE_TAG="cookify-backend:$GIT_TAG"
    fi
    
    if [ "$DRY_RUN" = false ]; then
        docker build -t $IMAGE_TAG .
        print_success "Docker image built: $IMAGE_TAG"
        
        # Tag as latest for environment
        docker tag $IMAGE_TAG cookify-backend:$ENVIRONMENT-latest
    else
        print_status "[DRY RUN] Would build Docker image: $IMAGE_TAG"
    fi
else
    print_warning "Skipping Docker build"
fi

# Database migrations
print_status "Running database migrations..."
if [ "$DRY_RUN" = false ]; then
    ./scripts/db-manage.sh migrate
    print_success "Database migrations completed"
else
    print_status "[DRY RUN] Would run database migrations"
fi

# Create deployment info
DEPLOY_INFO="deployments/deploy_${ENVIRONMENT}_$(date +%Y%m%d_%H%M%S).json"
mkdir -p deployments

if [ "$DRY_RUN" = false ]; then
    cat > $DEPLOY_INFO << EOF
{
    "environment": "$ENVIRONMENT",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "git_branch": "$GIT_BRANCH",
    "git_commit": "$GIT_COMMIT",
    "git_tag": "$GIT_TAG",
    "image_tag": "$IMAGE_TAG",
    "deployed_by": "$(whoami)",
    "hostname": "$(hostname)"
}
EOF
    print_success "Deployment info saved: $DEPLOY_INFO"
else
    print_status "[DRY RUN] Would create deployment info: $DEPLOY_INFO"
fi

# Environment-specific deployment
case $ENVIRONMENT in
    staging)
        print_status "Deploying to staging environment..."
        if [ "$DRY_RUN" = false ]; then
            # Here you would deploy to staging
            print_status "Starting staging deployment..."
            docker-compose -f docker-compose.staging.yml up -d || print_warning "Staging deployment command not found"
        else
            print_status "[DRY RUN] Would deploy to staging"
        fi
        ;;
    production)
        print_status "Deploying to production environment..."
        print_warning "⚠️  PRODUCTION DEPLOYMENT"
        
        if [ "$DRY_RUN" = false ]; then
            read -p "Are you sure you want to deploy to PRODUCTION? (yes/no): " -r
            if [[ ! $REPLY =~ ^yes$ ]]; then
                print_status "Deployment cancelled"
                exit 0
            fi
            
            # Here you would deploy to production
            print_status "Starting production deployment..."
            # docker-compose -f docker-compose.prod.yml up -d
            print_warning "Production deployment commands not configured yet"
        else
            print_status "[DRY RUN] Would deploy to production"
        fi
        ;;
esac

# Health check
print_status "Performing post-deployment health check..."
if [ "$DRY_RUN" = false ]; then
    sleep 10  # Wait for service to start
    
    # Check if service is responding
    if command -v curl &> /dev/null; then
        HEALTH_URL="http://localhost:8000/health"
        if [ "$ENVIRONMENT" = "production" ]; then
            HEALTH_URL="https://api.cookify.app/health"
        fi
        
        if curl -f $HEALTH_URL > /dev/null 2>&1; then
            print_success "Health check passed"
        else
            print_error "Health check failed"
            exit 1
        fi
    else
        print_warning "curl not available, skipping health check"
    fi
else
    print_status "[DRY RUN] Would perform health check"
fi

# Cleanup old deployments
print_status "Cleaning up old deployment artifacts..."
if [ "$DRY_RUN" = false ]; then
    # Keep only last 10 deployment info files
    cd deployments
    ls -t deploy_${ENVIRONMENT}_*.json | tail -n +11 | xargs rm -f 2>/dev/null || true
    cd ..
    
    # Remove old Docker images
    docker image prune -f > /dev/null 2>&1 || true
else
    print_status "[DRY RUN] Would cleanup old artifacts"
fi

echo ""
print_success "🎉 Deployment completed successfully!"
echo ""
echo "Deployment Summary:"
echo "==================="
echo "Environment: $ENVIRONMENT"
echo "Git Commit: $GIT_COMMIT"
if [ -n "$GIT_TAG" ]; then
    echo "Git Tag: $GIT_TAG"
fi
echo "Timestamp: $(date)"
if [ "$DRY_RUN" = false ]; then
    echo "Deployment Info: $DEPLOY_INFO"
fi
echo ""
echo "Next steps:"
echo "- Monitor application logs"
echo "- Verify all functionality"
echo "- Update monitoring dashboards"
