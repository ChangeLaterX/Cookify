"""
Health Check Configuration.
Centralized configuration for health monitoring thresholds and settings.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class HealthThresholds:
    """Configuration thresholds for health checks."""
    
    # Response time thresholds (milliseconds)
    response_time_warning: int = 1000  # 1 second
    response_time_critical: int = 5000  # 5 seconds
    
    # Database thresholds
    database_query_timeout: int = 5000  # 5 seconds
    database_connection_timeout: int = 3000  # 3 seconds
    
    # System resource thresholds (percentages)
    memory_usage_warning: float = 80.0
    memory_usage_critical: float = 95.0
    cpu_usage_warning: float = 80.0
    cpu_usage_critical: float = 95.0
    disk_usage_warning: float = 85.0
    disk_usage_critical: float = 95.0
    
    # Service-specific thresholds
    auth_check_timeout: int = 2000  # 2 seconds
    ingredients_query_timeout: int = 3000  # 3 seconds
    receipt_ocr_check_timeout: int = 1000  # 1 second


@dataclass
class HealthConfig:
    """Configuration for health monitoring system."""
    
    # Check intervals (seconds)
    detailed_check_cache_ttl: int = 30  # Cache detailed checks for 30 seconds
    quick_check_cache_ttl: int = 10  # Cache quick checks for 10 seconds
    
    # Retry configuration
    max_retries: int = 2
    retry_delay: float = 0.5  # 500ms
    
    # Concurrent check settings
    max_concurrent_checks: int = 10
    check_timeout: int = 30  # Overall timeout for all checks
    
    # Alert thresholds
    consecutive_failures_alert: int = 3
    degraded_services_alert_percent: float = 50.0  # Alert if >50% services degraded
    
    # Feature flags
    enable_system_monitoring: bool = True
    enable_performance_metrics: bool = True
    enable_external_service_checks: bool = True
    
    # Thresholds
    thresholds: HealthThresholds = field(default_factory=HealthThresholds)


# Global health configuration instance
health_config = HealthConfig()


def get_health_config() -> HealthConfig:
    """Get the global health configuration."""
    return health_config


def update_health_config(**kwargs: Any) -> None:
    """Update health configuration values."""
    for key, value in kwargs.items():
        if hasattr(health_config, key):
            setattr(health_config, key, value)
        else:
            raise ValueError(f"Unknown health config parameter: {key}")


def get_service_timeout(service_name: str) -> int:
    """Get timeout configuration for a specific service."""
    timeouts = {
        "auth": health_config.thresholds.auth_check_timeout,
        "ingredients": health_config.thresholds.ingredients_query_timeout,
        "receipt": health_config.thresholds.receipt_ocr_check_timeout,
        "database": health_config.thresholds.database_connection_timeout,
    }
    return timeouts.get(service_name, 5000)  # Default 5 seconds


def is_response_time_warning(response_time_ms: int) -> bool:
    """Check if response time indicates a warning condition."""
    return response_time_ms >= health_config.thresholds.response_time_warning


def is_response_time_critical(response_time_ms: int) -> bool:
    """Check if response time indicates a critical condition."""
    return response_time_ms >= health_config.thresholds.response_time_critical


def get_resource_status(usage_percent: float, warning_threshold: float, critical_threshold: float) -> str:
    """Determine resource status based on usage and thresholds."""
    if usage_percent >= critical_threshold:
        return "critical"
    elif usage_percent >= warning_threshold:
        return "warning"
    else:
        return "healthy"


# Export main components
__all__ = [
    "HealthConfig",
    "HealthThresholds", 
    "health_config",
    "get_health_config",
    "update_health_config",
    "get_service_timeout",
    "is_response_time_warning",
    "is_response_time_critical",
    "get_resource_status",
]
