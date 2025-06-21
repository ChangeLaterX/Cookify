"""
FastAPI Routes for Health Domain.
Provides HTTP endpoints for system health monitoring.
"""

import time
from fastapi import APIRouter, status
from datetime import datetime

from core.config import settings
from core.logging import get_logger
from .schemas import DetailedHealthResponse, HealthResponse
from .services import health_service
from .metrics import get_metrics_collector

logger = get_logger(__name__)

# Create router for health endpoints
router = APIRouter(prefix=settings.HEALTH_PREFIX, tags=[settings.HEALTH_TAG])


@router.get(
    settings.HEALTH_ROOT_ENDPOINT,
    response_model=DetailedHealthResponse,
    status_code=status.HTTP_200_OK,
    summary=settings.HEALTH_ROOT_TITLE,
    description=settings.HEALTH_ROOT_DESCRIPTION,
)
async def detailed_health_check() -> DetailedHealthResponse:
    """
    Perform comprehensive health check of all services.

    Returns:
        DetailedHealthResponse with status of all services including timing and details

    This endpoint checks:
    - Authentication service (Supabase Auth)
    - Ingredients service (Database connectivity)
    - Receipt service (OCR availability)
    - Database connection (PostgreSQL)
    - System resources (CPU, Memory, Disk)
    """
    start_time = time.time()
    
    logger.info(
        "Starting detailed health check",
        context={
            "endpoint": "/health",
            "check_type": "detailed"
        }
    )
    
    health_result = await health_service.check_all_services()
    
    check_duration_ms = int((time.time() - start_time) * 1000)
    
    # Record metrics
    metrics_collector = get_metrics_collector()
    metrics_collector.record_health_check(health_result)
    
    logger.info(
        "Detailed health check completed",
        context={
            "endpoint": "/health",
            "check_type": "detailed",
            "overall_status": health_result.status.value,
            "services_checked": len(health_result.services),
            "check_duration_ms": check_duration_ms
        },
        data={
            "health_check_results": {
                "overall_status": health_result.status.value,
                "services_checked": len(health_result.services),
                "healthy_services": len([s for s in health_result.services if s.status == "healthy"]),
                "unhealthy_services": len([s for s in health_result.services if s.status != "healthy"]),
                "check_duration_ms": check_duration_ms
            }
        }
    )
    
    return health_result


@router.get(
    settings.HEALTH_QUICK_ENDPOINT,
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary=settings.HEALTH_QUICK_TITLE,
    description=settings.HEALTH_QUICK_DESCRIPTION,
)
async def quick_health_check() -> HealthResponse:
    """
    Perform quick health check without detailed service information.

    Returns:
        HealthResponse with basic system health status

    This is a lightweight endpoint that performs minimal checks,
    suitable for load balancer health checks or frequent monitoring.
    """
    start_time = time.time()
    
    logger.info(
        "Starting quick health check",
        context={
            "endpoint": "/health/quick",
            "check_type": "quick"
        }
    )
    
    health_result = await health_service.quick_health_check()
    
    check_duration_ms = int((time.time() - start_time) * 1000)
    
    logger.info(
        "Quick health check completed",
        context={
            "endpoint": "/health/quick",
            "check_type": "quick",
            "status": health_result.status.value,
            "check_duration_ms": check_duration_ms
        },
        data={
            "health_check_results": {
                "status": health_result.status.value,
                "check_duration_ms": check_duration_ms,
                "timestamp": health_result.timestamp
            }
        }
    )
    
    return health_result


@router.get(
    settings.HEALTH_LIVENESS_ENDPOINT,
    status_code=status.HTTP_200_OK,
    summary=settings.HEALTH_LIVENESS_TITLE,
    description=settings.HEALTH_LIVENESS_DESCRIPTION,
)
async def liveness_probe() -> dict:
    """
    Liveness probe for Kubernetes/Docker orchestration.
    
    This endpoint only checks if the application is running and can respond.
    It does not check external dependencies.
    
    Returns:
        Simple status dict
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get(
    settings.HEALTH_READINESS_ENDPOINT,
    status_code=status.HTTP_200_OK,
    summary=settings.HEALTH_READINESS_TITLE, 
    description=settings.HEALTH_READINESS_DESCRIPTION,
)
async def readiness_probe() -> dict:
    """
    Readiness probe for Kubernetes/Docker orchestration.
    
    This endpoint checks if the application is ready to serve traffic
    by validating critical dependencies.
    
    Returns:
        Status dict with readiness information
        
    Raises:
        HTTPException: 503 if application is not ready
    """
    try:
        # Quick check of critical services only
        from shared.database.supabase import get_supabase_client
        
        # Test basic Supabase connectivity
        supabase = get_supabase_client()
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        from fastapi import HTTPException
        raise HTTPException(
            status_code=settings.HEALTH_SERVICE_UNAVAILABLE_STATUS,
            detail={
                "status": "not_ready",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get(
    settings.HEALTH_METRICS_ENDPOINT,
    status_code=status.HTTP_200_OK,
    summary=settings.HEALTH_METRICS_TITLE,
    description=settings.HEALTH_METRICS_DESCRIPTION,
)
async def health_metrics() -> dict:
    """
    Get health metrics and system overview.
    
    Returns:
        Dictionary with system overview and service metrics
    """
    metrics_collector = get_metrics_collector()
    system_overview = metrics_collector.get_system_overview()
    service_metrics = metrics_collector.get_all_service_metrics()
    
    # Convert ServiceMetrics objects to dicts for JSON serialization
    service_metrics_dict = {}
    for service_name, metrics in service_metrics.items():
        service_metrics_dict[service_name] = {
            "service_name": metrics.service_name,
            "total_checks": metrics.total_checks,
            "successful_checks": metrics.successful_checks,
            "failed_checks": metrics.failed_checks,
            "avg_response_time": round(metrics.avg_response_time, settings.HEALTH_METRICS_DECIMAL_PLACES),
            "max_response_time": metrics.max_response_time,
            "min_response_time": metrics.min_response_time if metrics.min_response_time != float('inf') else settings.HEALTH_MIN_RESPONSE_TIME_DEFAULT,
            "uptime_percentage": round(metrics.uptime_percentage, settings.HEALTH_METRICS_DECIMAL_PLACES),
            "last_check": metrics.last_check.isoformat() if metrics.last_check else None,
            "last_failure": metrics.last_failure.isoformat() if metrics.last_failure else None,
            "consecutive_failures": metrics.consecutive_failures,
            "consecutive_successes": metrics.consecutive_successes,
        }
    
    return {
        "system_overview": system_overview,
        "service_metrics": service_metrics_dict,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    settings.HEALTH_ALERTS_ENDPOINT,
    status_code=status.HTTP_200_OK,
    summary=settings.HEALTH_ALERTS_TITLE,
    description=settings.HEALTH_ALERTS_DESCRIPTION,
)
async def health_alerts(hours: int = settings.HEALTH_ALERTS_DEFAULT_HOURS) -> dict:
    """
    Get recent health alerts.
    
    Args:
        hours: Number of hours to look back for alerts (default: 1)
        
    Returns:
        Dictionary with recent alerts
    """
    if hours < settings.HEALTH_ALERTS_MIN_HOURS or hours > settings.HEALTH_ALERTS_MAX_HOURS:  # Max 1 week
        hours = settings.HEALTH_ALERTS_DEFAULT_HOURS
    
    metrics_collector = get_metrics_collector()
    alerts = metrics_collector.get_recent_alerts(hours=hours)
    
    # Convert alerts to dict format
    alerts_dict = []
    for alert in alerts:
        alerts_dict.append({
            "level": alert.level.value,
            "service_name": alert.service_name,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "metric": {
                "status": alert.metric.status.value,
                "response_time_ms": alert.metric.response_time_ms,
                "error_message": alert.metric.error_message
            } if alert.metric else None
        })
    
    return {
        "alerts": alerts_dict,
        "hours_back": hours,
        "alert_count": len(alerts_dict),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    settings.HEALTH_SERVICE_HISTORY_ENDPOINT,
    status_code=status.HTTP_200_OK,
    summary=settings.HEALTH_SERVICE_HISTORY_TITLE,
    description=settings.HEALTH_SERVICE_HISTORY_DESCRIPTION,
)
async def service_health_history(service_name: str, hours: int = 1) -> dict:
    """
    Get health check history for a specific service.
    
    Args:
        service_name: Name of the service
        hours: Number of hours to look back (default: 1)
        
    Returns:
        Dictionary with service health history
    """
    if hours < 1 or hours > 168:  # Max 1 week
        hours = 1
    
    metrics_collector = get_metrics_collector()
    history = metrics_collector.get_service_history(service_name, hours=hours)
    service_metrics = metrics_collector.get_service_metrics(service_name)
    
    # Convert history to dict format
    history_dict = []
    for metric in history:
        history_dict.append({
            "timestamp": metric.timestamp.isoformat(),
            "status": metric.status.value,
            "response_time_ms": metric.response_time_ms,
            "error_message": metric.error_message,
            "details": metric.details
        })
    
    # Convert service metrics to dict
    service_metrics_dict = None
    if service_metrics:
        service_metrics_dict = {
            "service_name": service_metrics.service_name,
            "total_checks": service_metrics.total_checks,
            "successful_checks": service_metrics.successful_checks,
            "failed_checks": service_metrics.failed_checks,
            "avg_response_time": round(service_metrics.avg_response_time, 2),
            "uptime_percentage": round(service_metrics.uptime_percentage, 2),
            "consecutive_failures": service_metrics.consecutive_failures,
        }
    
    return {
        "service_name": service_name,
        "hours_back": hours,
        "history": history_dict,
        "history_count": len(history_dict),
        "service_metrics": service_metrics_dict,
        "timestamp": datetime.utcnow().isoformat()
    }


# Export router
__all__ = ["router"]
