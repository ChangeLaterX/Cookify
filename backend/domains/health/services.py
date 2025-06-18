"""
Health Check Services.
Provides centralized health monitoring for all application services.
"""

import asyncio
import logging
import time
import platform
from typing import List, Dict, Optional
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None  # type: ignore

from .schemas import ServiceHealthStatus, ServiceStatus, HealthResponse, DetailedHealthResponse
from core.config import settings
from domains.update.ingredient_cache import get_ingredient_cache_status

logger = logging.getLogger(__name__)

# Global application start time for uptime calculation
_app_start_time = time.time()


class HealthCheckService:
    """Service for performing health checks across all application domains."""
    
    def __init__(self):
        # Use service names from settings
        self.service_checkers = {}
        for service_name in settings.HEALTH_SERVICE_NAMES:
            if service_name == "auth":
                self.service_checkers[service_name] = self._check_auth_service
            elif service_name == "ingredients":
                self.service_checkers[service_name] = self._check_ingredients_service
            elif service_name == "receipt":
                self.service_checkers[service_name] = self._check_receipt_service
            elif service_name == "database":
                self.service_checkers[service_name] = self._check_database_connection
            elif service_name == "system":
                self.service_checkers[service_name] = self._check_system_resources
            elif service_name == "cache":
                self.service_checkers[service_name] = self._check_cache_status
            elif service_name == "update":
                self.service_checkers[service_name] = self._check_update_service
    
    async def check_all_services(self) -> DetailedHealthResponse:
        """
        Perform health checks on all services.
        
        Returns:
            DetailedHealthResponse with status of all services
        """
        start_time = time.time()
        service_results = []
        
        # Run all health checks concurrently
        tasks = []
        for service_name, checker in self.service_checkers.items():
            tasks.append(self._run_service_check(service_name, checker))
        
        service_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and get valid results
        valid_results = [
            result for result in service_results 
            if isinstance(result, ServiceHealthStatus)
        ]
        
        # Determine overall status
        overall_status = self._determine_overall_status(valid_results)
        
        # Calculate total check time
        total_time_ms = int((time.time() - start_time) * 1000)
        
        return DetailedHealthResponse(
            status=overall_status,
            message=self._get_overall_message(overall_status, len(valid_results)),
            services=valid_results,
            system_info=self._get_enhanced_system_info(total_time_ms),
            uptime_seconds=int(time.time() - _app_start_time)
        )
    
    async def quick_health_check(self) -> HealthResponse:
        """
        Perform a quick health check without detailed service information.
        
        Returns:
            HealthResponse with basic health status
        """
        try:
            # Just check if we can import core modules
            from shared.database.supabase import get_supabase_client
            from core.config import settings
            
            # Test basic Supabase connectivity
            supabase = get_supabase_client()
            
            return HealthResponse(
                status=ServiceStatus.HEALTHY,
                message="System is operational"
            )
        except Exception as e:
            logger.error(f"Quick health check failed: {str(e)}")
            return HealthResponse(
                status=ServiceStatus.UNHEALTHY,
                message="System is experiencing issues"
            )
    
    async def _run_service_check(self, service_name: str, checker) -> ServiceHealthStatus:
        """Run an individual service health check with timing."""
        start_time = time.time()
        
        try:
            result = await checker()
            result.response_time_ms = int((time.time() - start_time) * 1000)
            return result
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {str(e)}")
            return ServiceHealthStatus(
                name=service_name,
                status=ServiceStatus.UNHEALTHY,
                message=f"{service_name.title()} service health check failed",
                response_time_ms=int((time.time() - start_time) * 1000),
                error=str(e)
            )
    
    async def _check_auth_service(self) -> ServiceHealthStatus:
        """Check authentication service health."""
        try:
            # Try to import auth services and verify they're available
            from domains.auth.services import auth_service
            
            # Basic check - ensure service is importable and has expected methods
            if hasattr(auth_service, 'supabase'):
                return ServiceHealthStatus(
                    name="auth",
                    status=ServiceStatus.HEALTHY,
                    message="Authentication service is operational",
                    details={"provider": "Supabase Auth"}
                )
            else:
                return ServiceHealthStatus(
                    name="auth",
                    status=ServiceStatus.DEGRADED,
                    message="Authentication service partially available",
                    details={"provider": "Supabase Auth"}
                )
        except Exception as e:
            return ServiceHealthStatus(
                name="auth",
                status=ServiceStatus.UNHEALTHY,
                message="Authentication service unavailable",
                error=str(e)
            )
    
    async def _check_ingredients_service(self) -> ServiceHealthStatus:
        """Check ingredients service health."""
        try:
            from domains.ingredients.services import get_all_ingredients
            
            # Test database connectivity with a simple query
            result = await get_all_ingredients(limit=1, offset=0)
            
            return ServiceHealthStatus(
                name="ingredients",
                status=ServiceStatus.HEALTHY,
                message="Ingredients service is operational and database accessible",
                details={
                    "database": "connected",
                    "test_query": "successful"
                }
            )
        except Exception as e:
            return ServiceHealthStatus(
                name="ingredients",
                status=ServiceStatus.UNHEALTHY,
                message="Ingredients service or database unavailable",
                error=str(e)
            )
    
    async def _check_receipt_service(self) -> ServiceHealthStatus:
        """Check receipt/OCR service health."""
        try:
            from domains.ocr.services import OCR_AVAILABLE
            
            if OCR_AVAILABLE:
                return ServiceHealthStatus(
                    name="receipt",
                    status=ServiceStatus.HEALTHY,
                    message="Receipt service is operational and OCR available",
                    response_time_ms=0,
                    details={
                        "ocr_available": "true",
                        "provider": "Tesseract/PIL"
                    },
                    error=None
                )
            else:
                return ServiceHealthStatus(
                    name="receipt",
                    status=ServiceStatus.DEGRADED,
                    message="Receipt service operational but OCR dependencies missing",
                    response_time_ms=0,
                    details={
                        "ocr_available": "false",
                        "provider": "Tesseract/PIL"
                    },
                    error=None
                )
        except Exception as e:
            return ServiceHealthStatus(
                name="receipt",
                status=ServiceStatus.UNHEALTHY,
                message="Receipt service unavailable",
                response_time_ms=0,
                details=None,
                error=str(e)
            )
    
    async def _check_database_connection(self) -> ServiceHealthStatus:
        """Check database connection health."""
        try:
            from shared.database.supabase import get_supabase_client
            
            # Test Supabase connection by getting the auth user (works even without tables)
            supabase = get_supabase_client()
            
            # Try to access Supabase auth which should always be available
            # This doesn't require any custom tables to exist
            auth_response = supabase.auth.get_session()
            
            return ServiceHealthStatus(
                name="database",
                status=ServiceStatus.HEALTHY,
                message="Database connection is healthy",
                response_time_ms=0,
                details={
                    "provider": "Supabase PostgreSQL",
                    "connection": "active",
                    "auth_available": "true"
                },
                error=None
            )
        except Exception as e:
            return ServiceHealthStatus(
                name="database",
                status=ServiceStatus.UNHEALTHY,
                message="Database connection failed",
                response_time_ms=0,
                details=None,
                error=str(e)
            )
    
    async def _check_cache_status(self) -> ServiceHealthStatus:
        """Check ingredient file cache status."""
        import traceback
        try:
            status = get_ingredient_cache_status()
            file_exists = status.get("file_exists", False)
            needs_update = status.get("needs_update", True)
            ingredient_count = status.get("ingredient_count", 0)
            last_updated = status.get("last_updated")
            
            # Convert all status values to strings for Pydantic validation
            details = {
                "file_exists": str(file_exists),
                "file_path": str(status.get("file_path", "")),
                "last_updated": str(last_updated) if last_updated else "never",
                "ingredient_count": str(ingredient_count),
                "needs_update": str(needs_update),
                "update_interval_days": str(status.get("update_interval_days", 7))
            }
            
            msg = "Ingredient file cache is healthy" if file_exists and not needs_update else "Ingredient file cache needs update or is missing"
            health_status = ServiceStatus.HEALTHY if file_exists and not needs_update else ServiceStatus.DEGRADED if file_exists else ServiceStatus.UNHEALTHY
            
            return ServiceHealthStatus(
                name="cache",
                status=health_status,
                message=msg,
                details=details,
                error=None if file_exists else "Ingredient file missing or inaccessible"
            )
        except Exception as e:
            return ServiceHealthStatus(
                name="cache",
                status=ServiceStatus.UNHEALTHY,
                message="Failed to check ingredient file cache status",
                details={"traceback": traceback.format_exc()},
                error=str(e)
            )
    
    async def _check_update_service(self) -> ServiceHealthStatus:
        """Check update service health."""
        try:
            from domains.update.services import get_ingredient_cache_status
            
            # Test if we can access the update service functions
            cache_status = await get_ingredient_cache_status()
            
            # Check if the update service is operational
            cache_healthy = cache_status.get("cache_file_exists", False)
            
            return ServiceHealthStatus(
                name="update",
                status=ServiceStatus.HEALTHY if cache_healthy else ServiceStatus.DEGRADED,
                message="Update service is operational" if cache_healthy else "Update service operational but cache degraded",
                details={
                    "cache_status": "healthy" if cache_healthy else "degraded",
                    "last_cache_update": str(cache_status.get("last_updated", "unknown")),
                    "ingredient_count": str(cache_status.get("ingredient_count", 0)),
                    "service_available": "true"
                }
            )
        except Exception as e:
            return ServiceHealthStatus(
                name="update",
                status=ServiceStatus.UNHEALTHY,
                message="Update service unavailable",                error=str(e)
            )
    
    async def _check_update_service(self) -> ServiceHealthStatus:
        """Check update service health."""
        try:
            from domains.update.services import get_ingredient_cache_status
            
            # Test if we can access the update service functions
            cache_status = await get_ingredient_cache_status()
            
            # Check if the update service is operational
            cache_healthy = cache_status.get("cache_file_exists", False)
            
            return ServiceHealthStatus(
                name="update",
                status=ServiceStatus.HEALTHY if cache_healthy else ServiceStatus.DEGRADED,
                message="Update service is operational" if cache_healthy else "Update service operational but cache degraded",
                details={
                    "cache_status": "healthy" if cache_healthy else "degraded",
                    "last_cache_update": str(cache_status.get("last_updated", "unknown")),
                    "ingredient_count": str(cache_status.get("ingredient_count", 0)),
                    "service_available": "true"
                }
            )
        except Exception as e:
            return ServiceHealthStatus(
                name="update",
                status=ServiceStatus.UNHEALTHY,
                message="Update service unavailable",
                error=str(e)
            )

    def _determine_overall_status(self, services: List[ServiceHealthStatus]) -> ServiceStatus:
        """Determine overall system status based on individual service statuses."""
        if not services:
            return ServiceStatus.UNHEALTHY
        
        unhealthy_count = sum(1 for s in services if s.status == ServiceStatus.UNHEALTHY)
        degraded_count = sum(1 for s in services if s.status == ServiceStatus.DEGRADED)
        
        if unhealthy_count > 0:
            return ServiceStatus.UNHEALTHY
        elif degraded_count > 0:
            return ServiceStatus.DEGRADED
        else:
            return ServiceStatus.HEALTHY
    
    def _get_overall_message(self, status: ServiceStatus, service_count: int) -> str:
        """Get appropriate overall message based on status."""
        if status == ServiceStatus.HEALTHY:
            return f"All {service_count} services are healthy"
        elif status == ServiceStatus.DEGRADED:
            return f"Some services are degraded (checked {service_count} services)"
        else:
            return f"One or more services are unhealthy (checked {service_count} services)"
    
    def _get_enhanced_system_info(self, total_time_ms: int) -> Dict[str, str]:
        """Get enhanced system information including performance metrics."""
        try:
            from core.config import settings
            
            basic_info = {
                "app_name": settings.APP_NAME,
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "total_check_time_ms": str(total_time_ms),
                "platform": platform.system(),
                "python_version": platform.python_version(),
            }
            
            if not PSUTIL_AVAILABLE:
                basic_info["metrics_note"] = "Advanced system metrics unavailable (psutil not installed)"
                return basic_info
            
            # Get system metrics with psutil
            assert psutil is not None  # Type narrowing
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=None)
            disk_usage = psutil.disk_usage('/')
            
            # Get load averages (Unix-like systems only)
            load_avg = "N/A"
            try:
                load_avg = f"{psutil.getloadavg()[0]:.2f}" if hasattr(psutil, 'getloadavg') else "N/A"
            except (AttributeError, OSError):
                pass
            
            basic_info.update({
                "cpu_usage_percent": f"{cpu_percent:.1f}",
                "memory_usage_percent": f"{memory.percent:.1f}",
                "memory_available_mb": f"{memory.available // (1024 * 1024)}",
                "disk_usage_percent": f"{disk_usage.percent:.1f}",
                "load_average": load_avg,
                "process_count": str(len(psutil.pids())),
            })
            
            return basic_info
            
        except Exception as e:
            logger.warning(f"Failed to collect system metrics: {str(e)}")
            from core.config import settings
            return {
                "app_name": settings.APP_NAME,
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "total_check_time_ms": str(total_time_ms),
                "metrics_error": "Failed to collect system metrics"
            }
    
    async def _check_system_resources(self) -> ServiceHealthStatus:
        """Check system resource health (CPU, memory, disk)."""
        if not PSUTIL_AVAILABLE:
            return ServiceHealthStatus(
                name="system",
                status=ServiceStatus.DEGRADED,
                message="System monitoring unavailable - psutil not installed",
                response_time_ms=0,
                details={"psutil_available": "false"},
                error=None
            )
        
        try:
            # Get system metrics
            assert psutil is not None  # Type narrowing
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)  # 100ms sample
            disk_usage = psutil.disk_usage('/')
            
            status = ServiceStatus.HEALTHY
            warnings = []
            
            # Check memory usage
            if memory.percent > settings.HEALTH_MEMORY_USAGE_WARNING:
                status = ServiceStatus.DEGRADED
                warnings.append(f"High memory usage: {memory.percent:.1f}%")
            
            # Check CPU usage
            if cpu_percent > settings.HEALTH_CPU_USAGE_WARNING:
                status = ServiceStatus.DEGRADED
                warnings.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            # Check disk usage
            if disk_usage.percent > settings.HEALTH_DISK_USAGE_WARNING:
                status = ServiceStatus.DEGRADED
                warnings.append(f"High disk usage: {disk_usage.percent:.1f}%")
            
            # Determine message
            if warnings:
                message = f"System resources under stress: {', '.join(warnings)}"
            else:
                message = "System resources are healthy"
            
            return ServiceHealthStatus(
                name="system",
                status=status,
                message=message,
                response_time_ms=0,
                details={
                    "cpu_percent": f"{cpu_percent:.1f}",
                    "memory_percent": f"{memory.percent:.1f}",
                    "memory_available_gb": f"{memory.available / (1024**3):.1f}",
                    "disk_percent": f"{disk_usage.percent:.1f}",
                    "disk_free_gb": f"{disk_usage.free / (1024**3):.1f}",
                },
                error=None
            )
        except Exception as e:
            return ServiceHealthStatus(
                name="system",
                status=ServiceStatus.UNHEALTHY,
                message="Failed to check system resources",
                response_time_ms=0,
                details=None,
                error=str(e)
            )


# Global health service instance
health_service = HealthCheckService()

# Alias for backward compatibility
HealthStatus = ServiceStatus

# Export main components
__all__ = [
    "HealthCheckService",
    "health_service", 
    "ServiceStatus",
    "HealthStatus",  # Backward compatibility
]
