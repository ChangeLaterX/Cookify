# Cookify Backend Scripts

This directory contains useful scripts for development, testing, deployment and maintenance of the Cookify backend.

## 📋 Overview

### 🚀 Script Manager

```bash
./scripts/manage.sh [COMMAND] [OPTIONS]
```

Central access to all backend scripts with unified user interface.

## 📂 Available Scripts

### Development & Setup

#### `setup-backend-dev.sh`
Sets up the complete backend development environment.

**Features:**

- Create Python Virtual Environment
- Install dependencies
- Configure .env file
- Set up pre-commit hooks
- Create necessary directories

```bash
./scripts/setup-backend-dev.sh
```

#### `run-tests.sh`
Comprehensive test system with various options.

**Features:**

- Unit tests with pytest
- Coverage reports
- Code quality checks (flake8, black, isort)
- Performance tests
- Domain-specific tests

```bash
# Run all tests
./scripts/run-tests.sh

# With coverage report
./scripts/run-tests.sh --coverage

# Test specific domain only
./scripts/run-tests.sh --domain auth

# Performance tests
./scripts/run-tests.sh --performance

# Fast tests (without slow tests)
./scripts/run-tests.sh --fast
```

### Monitoring & Analysis

#### `monitor.sh`
Monitors backend health and performance in real-time.

**Features:**

- System resources (CPU, Memory, Disk)
- Application health
- Database connectivity
- Log analysis
- Alert system

```bash
# One-time check
./scripts/monitor.sh

# Continuous monitoring
./scripts/monitor.sh --continuous --interval 30

# With custom thresholds
./scripts/monitor.sh --cpu-threshold 90 --memory-threshold 85
```

#### `analyze-logs.sh`
Detailed log analysis for debugging and monitoring.

**Features:**

- Log summaries
- Error analysis
- Performance metrics
- Request analysis
- Export in various formats

```bash
# Summary of last 24h
./scripts/analyze-logs.sh --type summary

# Error analysis of last week
./scripts/analyze-logs.sh --type errors --range 7d

# Performance analysis with JSON export
./scripts/analyze-logs.sh --type performance --output report.json --format json

# Request analysis
./scripts/analyze-logs.sh --type requests --range 24h
```

### Database Management

#### `db-manage.sh`
Comprehensive database management for Supabase.

**Features:**

- Run migrations
- Add seed data
- Generate test data
- Backup management
- Status overview

```bash
# Check database status
./scripts/db-manage.sh status

# Run migrations
./scripts/db-manage.sh migrate

# Add seed data
./scripts/db-manage.sh seed

# Generate test data
./scripts/db-manage.sh test-data

# Clean temporary data
./scripts/db-manage.sh clean
```

### Deployment & Operations

#### `deploy.sh`
Automated deployment system for different environments.

**Features:**

- Multi-Environment Support (staging, production)
- Git integration
- Automatic tests before deployment
- Docker image building
- Database migrations
- Health checks

```bash
# Staging deployment
./scripts/deploy.sh --env staging

# Production deployment
./scripts/deploy.sh --env production

# Dry run (shows what would happen)
./scripts/deploy.sh --env staging --dry-run

# Without tests (not recommended)
./scripts/deploy.sh --env staging --skip-tests
```

#### `backup.sh`
Comprehensive backup system for code, data and configurations.

**Features:**

- Various backup types
- Compression
- Automatic cleanup of old backups
- Backup manifest with metadata

```bash
# Complete backup
./scripts/backup.sh --type full

# Code only
./scripts/backup.sh --type code

# Data only
./scripts/backup.sh --type data

# Configuration only
./scripts/backup.sh --type config

# With custom settings
./scripts/backup.sh --type full --dir /custom/backup/path --cleanup-days 14
```

### Performance Testing

#### `configure_performance_tests.sh`
Configures performance test parameters for different environments.

**Features:**

- Environment-specific configurations
- OCR performance tuning
- Latency and throughput parameters

```bash
# Configure development environment
source scripts/configure_performance_tests.sh
configure_development

# CI/CD environment
configure_ci_cd

# Staging environment
configure_staging
```

## 🎯 Quick Start

### 1. Initial Setup

```bash
# Set up backend development environment
./scripts/manage.sh setup

# Run all tests
./scripts/manage.sh test

# Migrate database
./scripts/manage.sh db migrate
```

### 2. Daily Development

```bash
# Start continuous monitoring
./scripts/manage.sh monitor --continuous

# Tests with coverage
./scripts/manage.sh test --coverage

# Analyze logs
./scripts/manage.sh logs --type summary
```

### 3. Deployment

```bash
# Create complete backup
./scripts/manage.sh backup --type full

# Deploy to staging
./scripts/manage.sh deploy --env staging

# Health check
./scripts/manage.sh monitor
```

## 🔧 Configuration

### Environment Variables
Scripts use the following environment variables from the `.env` file:

- `SUPABASE_URL` - Supabase database URL
- `SUPABASE_KEY` - Supabase API Key
- `ENVIRONMENT` - Current environment (development, staging, production)
- `LOG_LEVEL` - Log level for the application

### Performance Test Configuration
See `configure_performance_tests.sh` for detailed performance parameters.

## 📊 Monitoring & Alerts

### Alert Thresholds

- CPU: 80% (configurable)
- Memory: 80% (configurable)
- Disk: 90% (fixed)

### Log Rotation

- Logs are automatically archived after 7 days
- Monitoring logs deleted after 30 days

## 🚨 Troubleshooting

### Common Problems

1. **Permission Denied**
   ```bash
   chmod +x scripts/*.sh
   ```

2. **Python Virtual Environment Error**
   ```bash
   ./scripts/manage.sh setup
   ```

3. **Database Connection Error**
   - Check `.env` file
   - Validate Supabase credentials

4. **Docker Problems**
   ```bash
   docker system prune -f
   ./start-docker.sh
   ```

### Debug Mode
For detailed debug output:
```bash
set -x  # Add at the beginning of the script
```

## 📝 Logging

All scripts log important events:
- `logs/monitoring_YYYYMMDD.log` - Monitoring logs
- `logs/deployment_YYYYMMDD.log` - Deployment logs
- `logs/backup_summary.txt` - Backup summaries

## 🔄 Updates

Scripts are continuously extended. For the latest features:
```bash
git pull origin main
chmod +x scripts/*.sh
```

## 📞 Support

For problems or improvement suggestions:
1. Create issues in the repository
2. Provide log output and error messages
3. Specify environment details
