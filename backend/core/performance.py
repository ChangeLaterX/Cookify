"""
Performance monitoring and logging utilities.

This module provides decorators and utilities for measuring and logging
performance metrics across the application.
"""

import asyncio
import time
import functools
from typing import Dict, Any, Optional, Callable, Awaitable
from fastapi import Request, Response

from .logging import get_logger

logger = get_logger(__name__)


def log_performance(
    operation_name: str,
    include_args: bool = False,
    log_level: str = "INFO"
) -> Callable:
    """
    Decorator to log performance metrics for functions.
    
    Args:
        operation_name: Name of the operation being measured
        include_args: Whether to include function arguments in logs
        log_level: Logging level to use (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Decorated function with performance logging
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            
            context = {
                "operation": operation_name,
                "function": func.__name__
            }
            
            if include_args:
                context["args"] = str(args)
                context["kwargs"] = str(kwargs)
            
            try:
                logger.debug(f"Starting {operation_name}", context=context)
                
                result = await func(*args, **kwargs)
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                performance_data = {
                    "performance_metrics": {
                        "operation": operation_name,
                        "duration_ms": duration_ms,
                        "success": True
                    }
                }
                
                logger.info(
                    f"Completed {operation_name}",
                    context={**context, "duration_ms": duration_ms},
                    data=performance_data
                )
                
                return result
                
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                
                performance_data = {
                    "performance_metrics": {
                        "operation": operation_name,
                        "duration_ms": duration_ms,
                        "success": False,
                        "error": str(e)
                    }
                }
                
                logger.error(
                    f"Failed {operation_name}",
                    context={**context, "duration_ms": duration_ms, "error": str(e)},
                    data=performance_data
                )
                
                raise
                
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            
            context = {
                "operation": operation_name,
                "function": func.__name__
            }
            
            if include_args:
                context["args"] = str(args)
                context["kwargs"] = str(kwargs)
            
            try:
                logger.debug(f"Starting {operation_name}", context=context)
                
                result = func(*args, **kwargs)
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                performance_data = {
                    "performance_metrics": {
                        "operation": operation_name,
                        "duration_ms": duration_ms,
                        "success": True
                    }
                }
                
                logger.info(
                    f"Completed {operation_name}",
                    context={**context, "duration_ms": duration_ms},
                    data=performance_data
                )
                
                return result
                
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                
                performance_data = {
                    "performance_metrics": {
                        "operation": operation_name,
                        "duration_ms": duration_ms,
                        "success": False,
                        "error": str(e)
                    }
                }
                
                logger.error(
                    f"Failed {operation_name}",
                    context={**context, "duration_ms": duration_ms, "error": str(e)},
                    data=performance_data
                )
                
                raise
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


class PerformanceMiddleware:
    """
    Middleware to log request performance metrics.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        request_path = scope.get("path", "")
        request_method = scope.get("method", "")
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                duration_ms = int((time.time() - start_time) * 1000)
                status_code = message.get("status", 0)
                
                logger.info(
                    "HTTP request completed",
                    context={
                        "method": request_method,
                        "path": request_path,
                        "status_code": status_code,
                        "duration_ms": duration_ms
                    },
                    data={
                        "performance_metrics": {
                            "request_duration_ms": duration_ms,
                            "status_code": status_code,
                            "method": request_method,
                            "path": request_path
                        }
                    }
                )
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


def log_database_query(operation: str) -> Callable:
    """
    Decorator specifically for database query performance logging.
    
    Args:
        operation: Description of the database operation
    
    Returns:
        Decorated function with database performance logging
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                logger.debug(
                    f"Database query completed: {operation}",
                    context={
                        "operation": operation,
                        "duration_ms": duration_ms,
                        "function": func.__name__
                    },
                    data={
                        "database_metrics": {
                            "operation": operation,
                            "duration_ms": duration_ms,
                            "success": True
                        }
                    }
                )
                
                return result
                
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                
                logger.error(
                    f"Database query failed: {operation}",
                    context={
                        "operation": operation,
                        "duration_ms": duration_ms,
                        "error": str(e),
                        "function": func.__name__
                    },
                    data={
                        "database_metrics": {
                            "operation": operation,
                            "duration_ms": duration_ms,
                            "success": False,
                            "error": str(e)
                        }
                    }
                )
                
                raise
                
        return wrapper
    return decorator
