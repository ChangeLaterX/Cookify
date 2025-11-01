"""
Health Check Configuration.
Wrapper around centralized core/config.py settings for health monitoring.
"""

from core.config import settings


def get_service_timeout(service_name: str) -> int:
    """Get timeout configuration for a specific service."""
    timeouts = {
        "auth": settings.HEALTH_AUTH_CHECK_TIMEOUT,
        "ingredients": settings.HEALTH_INGREDIENTS_QUERY_TIMEOUT,
        "receipt": settings.HEALTH_RECEIPT_OCR_CHECK_TIMEOUT,
        "database": settings.HEALTH_DATABASE_CONNECTION_TIMEOUT,
        "system": 1000,  # System checks are usually fast
    }
    return timeouts.get(service_name, 5000)  # Default 5 seconds


def is_response_time_warning(response_time_ms: int) -> bool:
    """Check if response time indicates a warning condition."""
    return response_time_ms >= settings.HEALTH_RESPONSE_TIME_WARNING


def is_response_time_critical(response_time_ms: int) -> bool:
    """Check if response time indicates a critical condition."""
    return response_time_ms >= settings.HEALTH_RESPONSE_TIME_CRITICAL


def get_resource_status(usage_percent: float, resource_type: str) -> str:
    """Determine resource status based on usage and thresholds."""
    if resource_type == "memory":
        warning_threshold = settings.HEALTH_MEMORY_USAGE_WARNING
        critical_threshold = settings.HEALTH_MEMORY_USAGE_CRITICAL
    elif resource_type == "cpu":
        warning_threshold = settings.HEALTH_CPU_USAGE_WARNING
        critical_threshold = settings.HEALTH_CPU_USAGE_CRITICAL
    elif resource_type == "disk":
        warning_threshold = settings.HEALTH_DISK_USAGE_WARNING
        critical_threshold = settings.HEALTH_DISK_USAGE_CRITICAL
    else:
        warning_threshold = 80.0
        critical_threshold = 95.0

    if usage_percent >= critical_threshold:
        return "critical"
    elif usage_percent >= warning_threshold:
        return "warning"
    else:
        return "healthy"


def get_health_config():
    """Get health configuration from centralized settings."""
    return {
        "monitoring_enabled": settings.HEALTH_MONITORING_ENABLED,
        "system_monitoring_enabled": settings.HEALTH_SYSTEM_MONITORING_ENABLED,
        "performance_metrics_enabled": settings.HEALTH_PERFORMANCE_METRICS_ENABLED,
        "external_service_checks_enabled": settings.HEALTH_EXTERNAL_SERVICE_CHECKS_ENABLED,
        "detailed_check_cache_ttl": settings.HEALTH_DETAILED_CHECK_CACHE_TTL,
        "quick_check_cache_ttl": settings.HEALTH_QUICK_CHECK_CACHE_TTL,
        "max_retries": settings.HEALTH_MAX_RETRIES,
        "retry_delay": settings.HEALTH_RETRY_DELAY,
        "max_concurrent_checks": settings.HEALTH_MAX_CONCURRENT_CHECKS,
        "consecutive_failures_alert": settings.HEALTH_CONSECUTIVE_FAILURES_ALERT,
        "degraded_services_alert_percent": settings.HEALTH_DEGRADED_SERVICES_ALERT_PERCENT,
        "service_names": settings.HEALTH_SERVICE_NAMES,
    }


# Export main components
__all__ = [
    "get_service_timeout",
    "is_response_time_warning",
    "is_response_time_critical",
    "get_resource_status",
    "get_health_config",
]
