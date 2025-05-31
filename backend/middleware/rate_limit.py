"""
Rate limiting middleware for API protection.
"""
import time
import logging
from typing import DefaultDict, Literal, Callable
from collections import defaultdict
from fastapi import Request, HTTPException, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from core.security import get_client_ip

logger: logging.Logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware with security enhancements."""
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_requests: int = 10,
        burst_window_seconds: int = 10,
        max_tracked_clients: int = 10000,
        cleanup_interval: int = 3600
    ) -> None:
        super().__init__(app)
        self.requests_per_minute: int = requests_per_minute
        self.burst_requests: int = burst_requests
        self.burst_window_seconds: int = burst_window_seconds
        self.max_tracked_clients: int = max_tracked_clients
        self.cleanup_interval: int = cleanup_interval
        
        # Storage for rate limiting data
        self.client_requests: DefaultDict[str, list[float]] = defaultdict(list)
        self.client_burst: DefaultDict[str, list[float]] = defaultdict(list)
        self.last_cleanup: float = time.time()
    
    def _cleanup_old_requests(self, client_ip: str) -> None:
        """Remove old request timestamps."""
        now: float = time.time()
        
        # Clean up minute-based tracking
        minute_ago: float = now - 60
        self.client_requests[client_ip] = [
            timestamp for timestamp in self.client_requests[client_ip]
            if timestamp > minute_ago
        ]
        
        # Clean up burst-based tracking
        burst_window_ago: float = now - self.burst_window_seconds
        self.client_burst[client_ip] = [
            timestamp for timestamp in self.client_burst[client_ip]
            if timestamp > burst_window_ago
        ]
        
        # Remove empty entries to prevent memory leaks
        if not self.client_requests[client_ip]:
            del self.client_requests[client_ip]
        if not self.client_burst[client_ip]:
            del self.client_burst[client_ip]
    
    def _global_cleanup(self) -> None:
        """Perform global cleanup to prevent memory leaks."""
        now: float = time.time()
        
        # Only cleanup if enough time has passed
        if now - self.last_cleanup < self.cleanup_interval:
            return

        clients_to_remove: list[str] = []

        # Check all tracked clients
        for client_ip in list(self.client_requests.keys()):
            self._cleanup_old_requests(client_ip)
            
        # If we have too many clients, remove the oldest inactive ones
        if len(self.client_requests) > self.max_tracked_clients:
            # Sort by last activity and remove oldest
            client_activity: dict[str, float] = {}
            for client_ip, timestamps in self.client_requests.items():
                if timestamps:
                    client_activity[client_ip] = max(timestamps)
                else:
                    clients_to_remove.append(client_ip)
            
            # Remove empty clients first
            for client_ip in clients_to_remove:
                self.client_requests.pop(client_ip, None)
                self.client_burst.pop(client_ip, None)
            
            # If still too many, remove oldest
            if len(self.client_requests) > self.max_tracked_clients:
                sorted_clients: list[tuple[str, float]] = sorted(client_activity.items(), key=lambda x: x[1])
                clients_to_remove = [
                    client for client, _ in sorted_clients[:len(self.client_requests) - self.max_tracked_clients]
                ]
                
                for client_ip in clients_to_remove:
                    self.client_requests.pop(client_ip, None)
                    self.client_burst.pop(client_ip, None)
        
        self.last_cleanup = now
        logger.debug(f"Rate limit cleanup completed. Tracking {len(self.client_requests)} clients")
    
    def _is_rate_limited(self, client_ip: str) -> tuple:
        """Check if client is rate limited."""
        now: float = time.time()
        
        # Clean up old requests
        self._cleanup_old_requests(client_ip)
        
        # Check burst limit
        burst_count: int = len(self.client_burst[client_ip])
        if burst_count >= self.burst_requests:
            return True, f"Burst limit exceeded: {burst_count}/{self.burst_requests} requests in {self.burst_window_seconds}s"
        
        # Check per-minute limit
        minute_count: int = len(self.client_requests[client_ip])
        if minute_count >= self.requests_per_minute:
            return True, f"Rate limit exceeded: {minute_count}/{self.requests_per_minute} requests per minute"
        
        return False, ""
    
    def _record_request(self, client_ip: str) -> None:
        """Record a new request for the client."""
        now: float = time.time()
        self.client_requests[client_ip].append(now)
        self.client_burst[client_ip].append(now)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for certain paths
        if request.url.path.startswith(("/docs", "/redoc", "/openapi.json", "/health")):
            return await call_next(request)
        
        # Perform global cleanup periodically
        self._global_cleanup()
        
        client_ip: str = get_client_ip(request)
        
        # Sanitize client IP to prevent log injection
        if not client_ip or len(client_ip) > 45:
            client_ip = "unknown"
        
        # Check if rate limited
        is_limited, reason = self._is_rate_limited(client_ip)
        
        if is_limited:
            # Log with sanitized client IP
            logger.warning(f"Rate limit exceeded for {client_ip[:45]}: {reason}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"}
            )
        
        # Record the request
        self._record_request(client_ip)
        
        # Process request
        response: Response = await call_next(request)
        
        # Add rate limit headers
        self._cleanup_old_requests(client_ip)
        current_minute_requests: int = len(self.client_requests[client_ip])
        current_burst_requests: int = len(self.client_burst[client_ip])

        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.requests_per_minute - current_minute_requests))
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        response.headers["X-RateLimit-Burst-Limit"] = str(self.burst_requests)
        response.headers["X-RateLimit-Burst-Remaining"] = str(max(0, self.burst_requests - current_burst_requests))
        
        return response


def create_rate_limit_middleware(
    requests_per_minute: int = 60,
    burst_requests: int = 10,
    burst_window_seconds: int = 10
):
    """Factory function to create rate limit middleware with custom settings."""
    def middleware_factory(app) -> RateLimitMiddleware:
        return RateLimitMiddleware(
            app,
            requests_per_minute=requests_per_minute,
            burst_requests=burst_requests,
            burst_window_seconds=burst_window_seconds
        )
    return middleware_factory


def rate_limit(max_calls: int, period: int) -> Callable[[Request], Literal[True]]:
    """
    Create a rate limiting dependency for individual routes.
    
    Args:
        max_calls: Maximum number of calls allowed
        period: Time period in seconds
    
    Returns:
        Callable dependency function for FastAPI routes
    """
    from collections import defaultdict
    from time import time
    from fastapi import HTTPException, Request, status
    
    # Simple in-memory storage for route-specific rate limiting
    call_times: DefaultDict[str, list[float]] = defaultdict(list)

    def dependency(request: Request) -> Literal[True]:
        client_ip: str = get_client_ip(request)
        current_time: float = time()
        
        # Clean old entries
        call_times[client_ip] = [
            call_time for call_time in call_times[client_ip]
            if current_time - call_time < period
        ]
        
        # Check if rate limit exceeded
        if len(call_times[client_ip]) >= max_calls:
            logger.warning(f"Rate limit exceeded for {client_ip}: {len(call_times[client_ip])} calls in {period}s")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {max_calls} requests per {period} seconds."
            )
        
        # Record this call
        call_times[client_ip].append(current_time)
        
        return True
    
    return dependency
