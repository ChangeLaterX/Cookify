# Health Check API Documentation

## Overview

The Cookify Health Check API provides comprehensive health monitoring for all application services, including detailed metrics, alerts, and system resource monitoring. This system is designed for both development debugging and production monitoring.

## Endpoints Overview

| Method | Endpoint                             | Description                | Use Case                      |
| ------ | ------------------------------------ | -------------------------- | ----------------------------- |
| GET    | `/api/health/`                       | Comprehensive health check | Manual monitoring, dashboards |
| GET    | `/api/health/quick`                  | Fast basic health check    | Load balancer health checks   |
| GET    | `/api/health/liveness`               | Kubernetes liveness probe  | Container orchestration       |
| GET    | `/api/health/readiness`              | Kubernetes readiness probe | Container orchestration       |
| GET    | `/api/health/metrics`                | Health metrics overview    | Monitoring systems            |
| GET    | `/api/health/alerts`                 | Recent health alerts       | Alert management              |
| GET    | `/api/health/service/{name}/history` | Service health history     | Debugging, analysis           |

## Endpoint Details

### 1. Detailed Health Check

**GET** `/api/health/`

Performs comprehensive health checks of all services including system resources.

#### Response

```json
{
  "status": "healthy|degraded|unhealthy",
  "message": "All 5 services are healthy",
  "timestamp": "2025-06-15T11:06:33.419688",
  "services": [
    {
      "name": "auth",
      "status": "healthy",
      "message": "Authentication service is operational",
      "response_time_ms": 0,
      "details": {
        "provider": "Supabase Auth"
      },
      "error": null
    },
    {
      "name": "system",
      "status": "healthy",
      "message": "System resources are healthy",
      "response_time_ms": 100,
      "details": {
        "cpu_percent": "15.2",
        "memory_percent": "45.8",
        "memory_available_gb": "2.1",
        "disk_percent": "35.4",
        "disk_free_gb": "120.5"
      },
      "error": null
    }
  ],
  "system_info": {
    "app_name": "Cookify Backend API",
    "version": "0.1.0",
    "environment": "development",
    "total_check_time_ms": "1250",
    "platform": "Linux",
    "python_version": "3.12.0",
    "cpu_usage_percent": "15.2",
    "memory_usage_percent": "45.8",
    "uptime_seconds": 3600
  },
  "uptime_seconds": 3600
}
```

#### Services Checked

- **auth**: Supabase authentication service availability
- **ingredients**: Database connectivity and ingredient service
- **receipt**: OCR service availability
- **database**: Direct database connection health
- **system**: CPU, memory, and disk usage

### 2. Quick Health Check

**GET** `/api/health/quick`

Fast, lightweight health check suitable for frequent monitoring.

#### Response

```json
{
  "status": "healthy|unhealthy",
  "message": "System is operational",
  "timestamp": "2025-06-15T11:07:25.106930"
}
```

### 3. Liveness Probe

**GET** `/api/health/liveness`

Kubernetes/Docker liveness probe - checks if the application is alive.

#### Response

```json
{
  "status": "alive",
  "timestamp": "2025-06-15T11:06:41.788155"
}
```

### 4. Readiness Probe

**GET** `/api/health/readiness`

Kubernetes/Docker readiness probe - checks if the application is ready to serve traffic.

#### Response

**Success (200):**

```json
{
  "status": "ready",
  "timestamp": "2025-06-15T11:07:06.867588",
  "database": "connected"
}
```

**Not Ready (503):**

```json
{
  "detail": {
    "status": "not_ready",
    "error": "Database connection failed",
    "timestamp": "2025-06-15T11:07:06.867588"
  }
}
```

### 5. Health Metrics

**GET** `/api/health/metrics`

Aggregated health metrics and system overview.

#### Response

```json
{
  "system_overview": {
    "total_services": 5,
    "healthy_services": 5,
    "unhealthy_services": 0,
    "average_uptime_percent": 100.0,
    "recent_alerts_1h": 0,
    "critical_alerts_1h": 0,
    "system_uptime_hours": 24.5,
    "metrics_collected": 150
  },
  "service_metrics": {
    "auth": {
      "service_name": "auth",
      "total_checks": 100,
      "successful_checks": 99,
      "failed_checks": 1,
      "avg_response_time": 45.2,
      "max_response_time": 1200,
      "min_response_time": 10,
      "uptime_percentage": 99.0,
      "last_check": "2025-06-15T11:06:33.419727",
      "last_failure": "2025-06-15T10:30:15.123456",
      "consecutive_failures": 0,
      "consecutive_successes": 25
    }
  },
  "timestamp": "2025-06-15T11:07:13.005854"
}
```

### 6. Health Alerts

**GET** `/api/health/alerts?hours=1`

Recent health alerts and incidents.

#### Parameters

- `hours` (optional): Number of hours to look back (1-168, default: 1)

#### Response

```json
{
  "alerts": [
    {
      "level": "warning",
      "service_name": "ingredients",
      "message": "Service ingredients slow response: 5200ms",
      "timestamp": "2025-06-15T10:45:30.123456",
      "metric": {
        "status": "healthy",
        "response_time_ms": 5200,
        "error_message": null
      }
    },
    {
      "level": "critical",
      "service_name": "database",
      "message": "Service database has failed 3 consecutive times",
      "timestamp": "2025-06-15T10:30:15.123456",
      "metric": {
        "status": "unhealthy",
        "response_time_ms": 0,
        "error_message": "Connection timeout"
      }
    }
  ],
  "hours_back": 1,
  "alert_count": 2,
  "timestamp": "2025-06-15T11:07:19.545455"
}
```

#### Alert Levels

- **info**: Service recoveries, informational events
- **warning**: Performance issues, single failures
- **critical**: Multiple consecutive failures, severe issues

### 7. Service Health History

**GET** `/api/health/service/{service_name}/history?hours=1`

Health check history for a specific service.

#### Parameters

- `service_name`: Name of the service (auth, ingredients, receipt, database, system)
- `hours` (optional): Number of hours to look back (1-168, default: 1)

#### Response

```json
{
  "service_name": "ingredients",
  "hours_back": 1,
  "history": [
    {
      "timestamp": "2025-06-15T11:06:33.419727",
      "status": "healthy",
      "response_time_ms": 1210,
      "error_message": null,
      "details": {
        "database": "connected",
        "test_query": "successful"
      }
    }
  ],
  "history_count": 15,
  "service_metrics": {
    "service_name": "ingredients",
    "total_checks": 15,
    "successful_checks": 14,
    "failed_checks": 1,
    "avg_response_time": 850.5,
    "uptime_percentage": 93.33,
    "consecutive_failures": 0
  },
  "timestamp": "2025-06-15T11:07:25.106930"
}
```

## Status Codes

### Service Status

- **healthy**: Service is operating normally
- **degraded**: Service is functional but with performance issues
- **unhealthy**: Service is not functioning properly

### HTTP Status Codes

- **200**: Success - health check completed
- **503**: Service Unavailable - readiness probe failed

## System Resource Monitoring

The system health check monitors:

### CPU Usage

- **Warning**: >80% usage
- **Critical**: >95% usage

### Memory Usage

- **Warning**: >80% usage
- **Critical**: >95% usage

### Disk Usage

- **Warning**: >85% usage
- **Critical**: >95% usage

## Monitoring Integration

### Kubernetes/Docker

Use the liveness and readiness probes in your deployment:

```yaml
spec:
  containers:
    - name: cookify-backend
      image: cookify:latest
      livenessProbe:
        httpGet:
          path: /api/health/liveness
          port: 8000
        initialDelaySeconds: 30
        periodSeconds: 10
      readinessProbe:
        httpGet:
          path: /api/health/readiness
          port: 8000
        initialDelaySeconds: 5
        periodSeconds: 5
```

### Load Balancer Health Checks

Use the quick health check endpoint:

```
Health Check URL: /api/health/quick
Expected Response: 200 OK
Check Interval: 30 seconds
```

### Monitoring Systems

Integration examples for popular monitoring systems:

#### Prometheus

```yaml
- job_name: 'cookify-health'
  static_configs:
    - targets: ['api.cookify.com:8000']
  metrics_path: '/api/health/metrics'
  scrape_interval: 30s
```

#### Grafana Dashboard

Query examples:

- Service uptime: `cookify_service_uptime_percentage`
- Response times: `cookify_service_avg_response_time`
- Alert count: `cookify_alerts_total`

## Development Tools

### Manual Testing

```bash
# Quick health check
curl http://localhost:8000/api/health/quick

# Detailed health check
curl http://localhost:8000/api/health/

# Check specific service history
curl http://localhost:8000/api/health/service/ingredients/history?hours=24

# Monitor alerts
curl http://localhost:8000/api/health/alerts?hours=6
```

### Health Check Script

```bash
#!/bin/bash
# health-monitor.sh

API_BASE="http://localhost:8000/api/health"

echo "=== Cookify Health Check ==="
echo

# Quick status
STATUS=$(curl -s "$API_BASE/quick" | jq -r '.status')
echo "Overall Status: $STATUS"

# Detailed check
echo
echo "Service Details:"
curl -s "$API_BASE/" | jq -r '.services[] | "\(.name): \(.status) (\(.response_time_ms)ms)"'

# Recent alerts
echo
echo "Recent Alerts:"
ALERT_COUNT=$(curl -s "$API_BASE/alerts" | jq -r '.alert_count')
echo "Alerts in last hour: $ALERT_COUNT"

if [ "$ALERT_COUNT" -gt 0 ]; then
  curl -s "$API_BASE/alerts" | jq -r '.alerts[] | "[\(.level)] \(.service_name): \(.message)"'
fi
```

## Best Practices

### For Development

- Use `/api/health/` for debugging individual services
- Monitor `/api/health/alerts` during testing
- Check service history after making changes

### For Production

- Use `/api/health/readiness` for load balancer health checks
- Monitor `/api/health/metrics` for system overview
- Set up alerting based on `/api/health/alerts`
- Use `/api/health/liveness` for container orchestration

### Alert Thresholds

- Response time warnings at 1000ms
- Critical alerts after 3 consecutive failures
- System resource warnings at 80% usage

## Troubleshooting

### Common Issues

1. **Service showing as unhealthy**

   - Check service-specific logs
   - Verify external dependencies (database, APIs)
   - Review service history for patterns

2. **High response times**

   - Check system resource usage
   - Review database performance
   - Monitor network connectivity

3. **Frequent alerts**
   - Analyze service history for root causes
   - Check system resource trends
   - Review application logs

### Debug Commands

```bash
# Check system resources
curl -s http://localhost:8000/api/health/ | jq '.services[] | select(.name=="system")'

# Monitor specific service
watch -n 5 'curl -s http://localhost:8000/api/health/service/ingredients/history | jq ".history[0]"'

# Track alerts in real-time
watch -n 10 'curl -s http://localhost:8000/api/health/alerts'
```

---

For more information or support, please refer to the main project documentation or contact the development team.
