"""
Rate Limiting Middleware for Authentication Endpoints.
Implements progressive rate limiting with                requests_per_window=settings.RATE_LIMIT_REFRESH_TOKEN_ATTEMPTS,
                window_seconds=settings.RATE_LIMIT_REFRESH_TOKEN_WINDOW,
                progressive_delay=False
            ),
            # General auth endpoints fallback
            "default_auth": RateLimitConfig(
                requests_per_window=settings.RATE_LIMIT_DEFAULT_AUTH_ATTEMPTS,
                window_seconds=settings.RATE_LIMIT_DEFAULT_AUTH_WINDOW,
                progressive_delay=False
            )ble limits and proper logging.
"""
import logging
import time
from collections import defaultdict
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting rules."""
    requests_per_window: int
    window_seconds: int
    progressive_delay: bool = True
    progressive_multiplier: float = settings.RATE_LIMIT_PROGRESSIVE_MULTIPLIER
    max_progressive_delay: int = settings.RATE_LIMIT_MAX_PROGRESSIVE_DELAY


@dataclass
class ClientRateLimitData:
    """Rate limit data for a specific client."""
    requests: list[float]  # Timestamps of requests
    violations: int = 0
    last_violation: Optional[float] = None
    progressive_delay_until: Optional[float] = None


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware specifically for authentication endpoints.
    
    Features:
    - Configurable rate limits per endpoint
    - Progressive delays for repeated violations
    - Proper HTTP 429 responses with Retry-After headers
    - Security logging for violations
    - IP-based tracking with cleanup
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Rate limit storage (in production, use Redis or similar)
        self.client_data: Dict[str, ClientRateLimitData] = defaultdict(
            lambda: ClientRateLimitData(requests=[])
        )
        
        # Define rate limit rules for different auth endpoints
        self.rate_limit_rules = {
            # Login endpoint - strict limits due to brute force risk
            "/api/auth/login": RateLimitConfig(
                requests_per_window=settings.RATE_LIMIT_LOGIN_ATTEMPTS,
                window_seconds=settings.RATE_LIMIT_LOGIN_WINDOW_MINUTES * 60,
                progressive_delay=True
            ),
            # Registration endpoint - moderate limits
            "/api/auth/register": RateLimitConfig(
                requests_per_window=settings.RATE_LIMIT_REGISTRATION_ATTEMPTS,
                window_seconds=settings.RATE_LIMIT_REGISTRATION_WINDOW_MINUTES * 60,
                progressive_delay=True
            ),
            # Password reset requests - prevent email spam
            "/api/auth/forgot-password": RateLimitConfig(
                requests_per_window=settings.RATE_LIMIT_PASSWORD_RESET_ATTEMPTS,
                window_seconds=settings.RATE_LIMIT_PASSWORD_RESET_WINDOW_MINUTES * 60,
                progressive_delay=True
            ),
            # Password reset confirmation - prevent token guessing
            "/api/auth/reset-password": RateLimitConfig(
                requests_per_window=settings.RATE_LIMIT_RESET_PASSWORD_ATTEMPTS,
                window_seconds=settings.RATE_LIMIT_RESET_PASSWORD_WINDOW,
                progressive_delay=True
            ),
            # Email verification - prevent spam
            "/api/auth/verify-email": RateLimitConfig(
                requests_per_window=settings.RATE_LIMIT_VERIFY_EMAIL_ATTEMPTS,
                window_seconds=settings.RATE_LIMIT_VERIFY_EMAIL_WINDOW,
                progressive_delay=False
            ),
            # Resend verification - prevent email spam
            "/api/auth/resend-verification": RateLimitConfig(
                requests_per_window=settings.RATE_LIMIT_RESEND_VERIFICATION_ATTEMPTS,
                window_seconds=settings.RATE_LIMIT_RESEND_VERIFICATION_WINDOW,
                progressive_delay=True
            ),
            # Token refresh - moderate limits
            "/api/auth/refresh": RateLimitConfig(
                requests_per_window=settings.RATE_LIMIT_REFRESH_TOKEN_ATTEMPTS,
                window_seconds=settings.rate_limit_refresh_token_window,
                progressive_delay=False
            ),
            # General auth endpoints fallback
            "default_auth": RateLimitConfig(
                requests_per_window=settings.rate_limit_default_auth_attempts,
                window_seconds=settings.rate_limit_default_auth_window,
                progressive_delay=False
            )
        }
        
        # Schedule cleanup
        self.last_cleanup = time.time()
        self.cleanup_interval = settings.rate_limit_cleanup_interval
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and apply rate limiting to authentication endpoints.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint in chain
            
        Returns:
            Response from downstream handler or rate limit error
        """
        # Skip rate limiting if disabled (but allow testing in development)
        rate_limiting_enabled = settings.rate_limiting_enabled_safe
        debug_mode = settings.DEBUG
        
        # Debug logging
        if debug_mode:
            self.logger.info(f"Rate limiting check - debug: {debug_mode}, enabled: {rate_limiting_enabled}, path: {request.url.path}")
        
        if not rate_limiting_enabled:
            if debug_mode:
                self.logger.info("Rate limiting disabled - allowing request through")
            return await call_next(request)
        
        # Check if this is an auth endpoint that needs rate limiting
        path = request.url.path
        if not self._is_auth_endpoint(path):
            return await call_next(request)
        
        # Get client identifier
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        client_key = f"{client_ip}:{user_agent[:settings.RATE_LIMIT_USER_AGENT_LENGTH]}"  # Include user agent for better tracking
        
        # Periodic cleanup
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_data(current_time)
            self.last_cleanup = current_time
        
        # Check rate limit
        rate_limit_result = self._check_rate_limit(path, client_key, current_time)
        
        if not rate_limit_result[0]:  # Rate limited
            retry_after = rate_limit_result[1]
            self._log_rate_limit_violation(request, client_ip, user_agent, retry_after)
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Too many requests",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": "Rate limit exceeded for authentication endpoint",
                    "retry_after": retry_after,
                    "details": {
                        "endpoint": path,
                        "limit_window": f"{self._get_window_minutes(path)} minutes",
                        "max_requests": self._get_rate_limit_config(path).requests_per_window
                    }
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self._get_rate_limit_config(path).requests_per_window),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + retry_after))
                }
            )
        
        # Process request normally
        response = await call_next(request)
        
        # Add rate limit headers to successful responses
        if hasattr(response, 'headers'):
            config = self._get_rate_limit_config(path)
            client_data = self.client_data[client_key]
            remaining = max(0, config.requests_per_window - len(client_data.requests))
            
            response.headers["X-RateLimit-Limit"] = str(config.requests_per_window)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(
                int(current_time + config.window_seconds)
            )
        
        return response
    
    def _is_auth_endpoint(self, path: str) -> bool:
        """
        Check if the path is an authentication endpoint that needs rate limiting.
        
        Args:
            path: Request path
            
        Returns:
            True if endpoint needs rate limiting
        """
        auth_prefixes = ["/api/auth/"]
        return any(path.startswith(prefix) for prefix in auth_prefixes)
    
    def _get_rate_limit_config(self, path: str) -> RateLimitConfig:
        """
        Get rate limit configuration for a specific path.
        
        Args:
            path: Request path
            
        Returns:
            RateLimitConfig for the path
        """
        return self.rate_limit_rules.get(path, self.rate_limit_rules["default_auth"])
    
    def _check_rate_limit(self, path: str, client_key: str, current_time: float) -> Tuple[bool, int]:
        """
        Check if request should be rate limited.
        
        Args:
            path: Request path
            client_key: Client identifier
            current_time: Current timestamp
            
        Returns:
            Tuple of (allowed: bool, retry_after_seconds: int)
        """
        config = self._get_rate_limit_config(path)
        client_data = self.client_data[client_key]
        
        # Check if client is in progressive delay period
        if (client_data.progressive_delay_until and 
            current_time < client_data.progressive_delay_until):
            retry_after = int(client_data.progressive_delay_until - current_time)
            return False, retry_after
        
        # Clean old requests outside the current window
        window_start = current_time - config.window_seconds
        client_data.requests = [
            req_time for req_time in client_data.requests 
            if req_time > window_start
        ]
        
        # Check if limit is exceeded
        if len(client_data.requests) >= config.requests_per_window:
            # Increment violation count
            client_data.violations += 1
            client_data.last_violation = current_time
            
            # Calculate retry after time
            retry_after = config.window_seconds
            
            # Apply progressive delay if enabled
            if config.progressive_delay and client_data.violations > 1:
                progressive_delay = min(
                    config.window_seconds * (config.progressive_multiplier ** (client_data.violations - 1)),
                    config.max_progressive_delay
                )
                client_data.progressive_delay_until = current_time + progressive_delay
                retry_after = int(progressive_delay)
            
            return False, retry_after
        
        # Allow request and record it
        client_data.requests.append(current_time)
        return True, 0
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request headers.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client IP address
        """
        # Check for forwarded headers (when behind proxy/load balancer)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        # Check for Cloudflare header
        cf_ip = request.headers.get("cf-connecting-ip")
        if cf_ip:
            return cf_ip.strip()
        
        # Fallback to direct connection
        if hasattr(request.client, "host") and request.client.host:
            return request.client.host
        
        return "unknown"
    
    def _cleanup_old_data(self, current_time: float) -> None:
        """
        Clean up old rate limit data to prevent memory leaks.
        
        Args:
            current_time: Current timestamp
        """
        # Remove data older than configured cutoff time
        cutoff_time = current_time - settings.rate_limit_cleanup_cutoff
        
        expired_clients = []
        for client_key, client_data in self.client_data.items():
            # Check if all requests are old and no recent violations
            if (not client_data.requests or 
                max(client_data.requests) < cutoff_time) and (
                not client_data.last_violation or 
                client_data.last_violation < cutoff_time):
                expired_clients.append(client_key)
        
        for client_key in expired_clients:
            del self.client_data[client_key]
        
        if expired_clients:
            self.logger.debug(f"Cleaned up rate limit data for {len(expired_clients)} clients")
    
    def _log_rate_limit_violation(
        self, 
        request: Request, 
        client_ip: str, 
        user_agent: str, 
        retry_after: int
    ) -> None:
        """
        Log rate limit violations for security monitoring.
        
        Args:
            request: FastAPI request object
            client_ip: Client IP address
            user_agent: User agent string
            retry_after: Retry after seconds
        """
        violation_data = {
            "event": "rate_limit_violation",
            "endpoint": request.url.path,
            "method": request.method,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "retry_after": retry_after,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request.headers.get("x-request-id", "unknown")
        }
        
        self.logger.warning(
            f"Rate limit violation: {request.method} {request.url.path} | "
            f"IP: {client_ip} | User-Agent: {user_agent[:settings.rate_limit_user_agent_length]} | "
            f"Retry-After: {retry_after}s | Data: {violation_data}"
        )


# Export middleware
__all__ = ["AuthRateLimitMiddleware"]
