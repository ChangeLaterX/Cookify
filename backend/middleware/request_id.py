"""
Request ID middleware for request tracing.
"""
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger: logging.Logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request IDs for tracing."""
    
    def __init__(self, app, header_name: str = "X-Request-ID") -> None:
        super().__init__(app)
        self.header_name: str = header_name
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or extract request ID
        request_id: str | None = request.headers.get(self.header_name)
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Store request ID in request state
        request.state.request_id = request_id
        
        # Add to logging context
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs) -> logging.LogRecord:
            record: logging.LogRecord = old_factory(*args, **kwargs)
            record.request_id = request_id
            return record
        
        logging.setLogRecordFactory(record_factory)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers[self.header_name] = request_id
            
            return response
        
        finally:
            # Restore original log record factory
            logging.setLogRecordFactory(old_factory)


def get_request_id(request: Request) -> str:
    """Get the current request ID."""
    return getattr(request.state, "request_id", "unknown")
