"""
Health Metrics Collection and Analysis.
Collects health check metrics over time for monitoring and alerting.
"""

import time
import logging
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Deque, Any
from datetime import datetime, timezone
from datetime import datetime, timedelta
from enum import Enum

from .schemas import ServiceStatus, ServiceHealthStatus, DetailedHealthResponse
from core.config import settings

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class HealthMetric:
    """Single health check metric data point."""

    timestamp: datetime
    service_name: str
    status: ServiceStatus
    response_time_ms: int
    error_message: Optional[str] = None
    details: Optional[Dict[str, str]] = None


@dataclass
class HealthAlert:
    """Health alert information."""

    level: AlertLevel
    service_name: str
    message: str
    timestamp: datetime
    metric: Optional[HealthMetric] = None


@dataclass
class ServiceMetrics:
    """Aggregated metrics for a service."""

    service_name: str
    total_checks: int = 0
    successful_checks: int = 0
    failed_checks: int = 0
    avg_response_time: float = 0.0
    max_response_time: int = 0
    min_response_time: int = 999999  # Use large int instead of float('inf')
    uptime_percentage: float = 100.0
    last_check: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0


class HealthMetricsCollector:
    """Collects and analyzes health metrics over time."""

    def __init__(
        self,
        max_metrics: Optional[int] = None,
        alert_retention_hours: Optional[int] = None,
    ):
        """
        Initialize metrics collector.

        Args:
            max_metrics: Maximum number of metrics to retain per service (uses settings default)
            alert_retention_hours: Hours to retain alert history (uses settings default)
        """
        self.max_metrics = max_metrics or settings.HEALTH_METRICS_MAX_RETENTION
        self.alert_retention_hours = (
            alert_retention_hours or settings.HEALTH_ALERT_RETENTION_HOURS
        )

        # Metrics storage: service_name -> deque of HealthMetric
        self.metrics: Dict[str, Deque[HealthMetric]] = defaultdict(
            lambda: deque(maxlen=self.max_metrics)
        )

        # Alert history
        self.alerts: Deque[HealthAlert] = deque(maxlen=self.max_metrics)

        # Aggregated service metrics
        self.service_metrics: Dict[str, ServiceMetrics] = {}

        # Performance tracking
        self.start_time = datetime.now(timezone.utc)

    def record_health_check(self, health_response: DetailedHealthResponse) -> None:
        """Record a complete health check response."""
        timestamp = datetime.utcnow()

        for service in health_response.services:
            metric = HealthMetric(
                timestamp=timestamp,
                service_name=service.name,
                status=service.status,
                response_time_ms=service.response_time_ms or 0,
                error_message=service.error,
                details=service.details,
            )

            # Store metric
            self.metrics[service.name].append(metric)

            # Update aggregated metrics
            self._update_service_metrics(service.name, metric)

            # Check for alerts
            self._check_for_alerts(metric)

    def _update_service_metrics(self, service_name: str, metric: HealthMetric) -> None:
        """Update aggregated metrics for a service."""
        if service_name not in self.service_metrics:
            self.service_metrics[service_name] = ServiceMetrics(
                service_name=service_name
            )

        service_metric = self.service_metrics[service_name]
        service_metric.total_checks += 1
        service_metric.last_check = metric.timestamp

        # Update response times
        if metric.response_time_ms > 0:
            service_metric.max_response_time = max(
                service_metric.max_response_time, metric.response_time_ms
            )
            service_metric.min_response_time = min(
                service_metric.min_response_time, metric.response_time_ms
            )

            # Calculate running average
            total_time = (
                service_metric.avg_response_time * (service_metric.total_checks - 1)
                + metric.response_time_ms
            )
            service_metric.avg_response_time = total_time / service_metric.total_checks

        # Update success/failure tracking
        if metric.status == ServiceStatus.HEALTHY:
            service_metric.successful_checks += 1
            service_metric.consecutive_successes += 1
            service_metric.consecutive_failures = 0
        else:
            service_metric.failed_checks += 1
            service_metric.consecutive_failures += 1
            service_metric.consecutive_successes = 0
            service_metric.last_failure = metric.timestamp

        # Calculate uptime percentage
        service_metric.uptime_percentage = (
            service_metric.successful_checks / service_metric.total_checks
        ) * 100

    def _check_for_alerts(self, metric: HealthMetric) -> None:
        """Check if a metric should trigger an alert."""
        service_metric = self.service_metrics.get(metric.service_name)
        if not service_metric:
            return

        alerts = []

        # Service failure alerts
        if metric.status == ServiceStatus.UNHEALTHY:
            if service_metric.consecutive_failures == 1:
                alerts.append(
                    HealthAlert(
                        level=AlertLevel.WARNING,
                        service_name=metric.service_name,
                        message=f"Service {metric.service_name} is unhealthy: {metric.error_message or 'Unknown error'}",
                        timestamp=metric.timestamp,
                        metric=metric,
                    )
                )
            elif service_metric.consecutive_failures >= 3:
                alerts.append(
                    HealthAlert(
                        level=AlertLevel.CRITICAL,
                        service_name=metric.service_name,
                        message=f"Service {metric.service_name} has failed {service_metric.consecutive_failures} consecutive times",
                        timestamp=metric.timestamp,
                        metric=metric,
                    )
                )

        # Performance alerts
        if metric.response_time_ms > 5000:  # 5 seconds
            alerts.append(
                HealthAlert(
                    level=AlertLevel.WARNING,
                    service_name=metric.service_name,
                    message=f"Service {metric.service_name} slow response: {metric.response_time_ms}ms",
                    timestamp=metric.timestamp,
                    metric=metric,
                )
            )

        # Recovery alerts
        if (
            metric.status == ServiceStatus.HEALTHY
            and service_metric.consecutive_successes == 1
            and service_metric.last_failure
        ):
            alerts.append(
                HealthAlert(
                    level=AlertLevel.INFO,
                    service_name=metric.service_name,
                    message=f"Service {metric.service_name} has recovered",
                    timestamp=metric.timestamp,
                    metric=metric,
                )
            )

        # Store alerts
        for alert in alerts:
            self.alerts.append(alert)
            logger.info(f"Health alert: {alert.level.value} - {alert.message}")

    def get_service_metrics(self, service_name: str) -> Optional[ServiceMetrics]:
        """Get aggregated metrics for a specific service."""
        return self.service_metrics.get(service_name)

    def get_all_service_metrics(self) -> Dict[str, ServiceMetrics]:
        """Get aggregated metrics for all services."""
        return self.service_metrics.copy()

    def get_recent_alerts(self, hours: int = 1) -> List[HealthAlert]:
        """Get alerts from the last N hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert.timestamp >= cutoff_time]

    def get_service_history(
        self, service_name: str, hours: int = 1
    ) -> List[HealthMetric]:
        """Get metric history for a service."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            metric
            for metric in self.metrics.get(service_name, [])
            if metric.timestamp >= cutoff_time
        ]

    def get_system_overview(self) -> Dict[str, Any]:
        """Get overall system health overview."""
        total_services = len(self.service_metrics)
        healthy_services = sum(
            1
            for metrics in self.service_metrics.values()
            if metrics.consecutive_failures == 0
        )

        recent_alerts = self.get_recent_alerts(hours=1)
        critical_alerts = [a for a in recent_alerts if a.level == AlertLevel.CRITICAL]

        avg_uptime = sum(
            metrics.uptime_percentage for metrics in self.service_metrics.values()
        ) / max(total_services, 1)

        return {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "unhealthy_services": total_services - healthy_services,
            "average_uptime_percent": round(avg_uptime, 2),
            "recent_alerts_1h": len(recent_alerts),
            "critical_alerts_1h": len(critical_alerts),
            "system_uptime_hours": (datetime.utcnow() - self.start_time).total_seconds()
            / 3600,
            "metrics_collected": sum(len(deque) for deque in self.metrics.values()),
        }

    def cleanup_old_data(self) -> None:
        """Clean up old metrics and alerts."""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.alert_retention_hours)

        # Clean old alerts
        while self.alerts and self.alerts[0].timestamp < cutoff_time:
            self.alerts.popleft()

        # Note: Metrics are automatically cleaned by deque maxlen
        logger.debug(
            f"Cleaned up health data older than {self.alert_retention_hours} hours"
        )


# Global metrics collector instance
metrics_collector = HealthMetricsCollector()


def get_metrics_collector() -> HealthMetricsCollector:
    """Get the global metrics collector."""
    return metrics_collector


# Export main components
__all__ = [
    "HealthMetric",
    "HealthAlert",
    "ServiceMetrics",
    "AlertLevel",
    "HealthMetricsCollector",
    "metrics_collector",
    "get_metrics_collector",
]
