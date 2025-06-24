"""
OCR Rate Limiting Middleware.
Implements specialized rate limiting for resource-intensive OCR endpoints
with enhanced security features and image validation.
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Dict, Optional, Tuple

import magic
from fastapi import HTTPException, Request, Response, status
from PIL import Image, UnidentifiedImageError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class OCRRateLimitConfig:
    """Configuration for OCR-specific rate limiting."""

    requests_per_window: int
    window_seconds: int
    progressive_delay: bool = True
    max_file_size_mb: int = 10
    allowed_formats: list = None


@dataclass
class ClientOCRData:
    """OCR rate limit data for a specific client."""

    requests: list[float]  # Timestamps of requests
    violations: int = 0
    last_violation: Optional[float] = None
    progressive_delay_until: Optional[float] = None
    total_processing_time: float = 0.0  # Track processing burden


class OCRRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware specifically for OCR endpoints.

    Features:
    - Resource-aware rate limiting based on image size and processing time
    - Enhanced file validation (size, format, content)
    - Progressive delays for repeated violations
    - Security monitoring and logging
    - Protection against malicious file uploads
    """

    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Rate limit storage (in production, use Redis)
        self.client_data: Dict[str, ClientOCRData] = defaultdict(
            lambda: ClientOCRData(requests=[])
        )

        # OCR-specific rate limit rules
        self.ocr_rate_limits = {
            "/api/ocr/extract-text": OCRRateLimitConfig(
                requests_per_window=settings.RATE_LIMIT_OCR_EXTRACT_ATTEMPTS,
                window_seconds=settings.RATE_LIMIT_OCR_EXTRACT_WINDOW_MINUTES * 60,
                progressive_delay=settings.RATE_LIMIT_OCR_ENABLE_PROGRESSIVE_DELAY,
                max_file_size_mb=5,
                allowed_formats=["JPEG", "JPG", "PNG", "WEBP", "BMP", "TIFF"],
            ),
            "/api/ocr/process": OCRRateLimitConfig(
                requests_per_window=settings.RATE_LIMIT_OCR_PROCESS_ATTEMPTS,
                window_seconds=settings.RATE_LIMIT_OCR_PROCESS_WINDOW_MINUTES * 60,
                progressive_delay=settings.RATE_LIMIT_OCR_ENABLE_PROGRESSIVE_DELAY,
                max_file_size_mb=5,
                allowed_formats=["JPEG", "JPG", "PNG", "WEBP", "BMP", "TIFF"],
            ),
        }

        # Malicious file patterns to detect
        self.suspicious_patterns = [
            b"<?php",  # PHP code
            b"<script",  # JavaScript
            b"eval(",  # Code evaluation
            b"exec(",  # Code execution
            b"system(",  # System commands
        ]

    async def dispatch(self, request: Request, call_next):
        """Process OCR requests with rate limiting and security checks."""

        # Only apply to OCR endpoints
        if not self._is_ocr_endpoint(request.url.path):
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        endpoint = request.url.path
        current_time = time.time()

        try:
            # Check rate limits first
            rate_limit_result = self._check_rate_limit(
                client_ip, endpoint, current_time
            )
            if rate_limit_result:
                return rate_limit_result

            # For POST requests with files, perform enhanced validation
            if request.method == "POST":
                validation_result = await self._validate_request(request, endpoint)
                if validation_result:
                    return validation_result

            # Record request
            self._record_request(client_ip, endpoint, current_time)

            # Process request
            start_time = time.time()
            response = await call_next(request)
            processing_time = time.time() - start_time

            # Track processing burden for adaptive rate limiting
            self._update_processing_metrics(client_ip, processing_time)

            self.logger.info(
                "OCR request processed successfully",
                extra={
                    "client_ip": client_ip,
                    "endpoint": endpoint,
                    "processing_time_ms": int(processing_time * 1000),
                    "status_code": response.status_code,
                },
            )

            return response

        except Exception as e:
            self.logger.error(
                f"Error in OCR rate limiting middleware: {e}",
                extra={"client_ip": client_ip, "endpoint": endpoint, "error": str(e)},
            )
            # Don't block request on middleware errors
            return await call_next(request)

    def _is_ocr_endpoint(self, path: str) -> bool:
        """Check if the request path is an OCR endpoint."""
        return any(
            path.startswith(ocr_path) for ocr_path in self.ocr_rate_limits.keys()
        )

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address with proxy support."""
        # Check for forwarded headers (for proxy/load balancer setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fallback to direct connection IP
        if hasattr(request.client, "host"):
            return request.client.host

        return "unknown"

    def _check_rate_limit(
        self, client_ip: str, endpoint: str, current_time: float
    ) -> Optional[JSONResponse]:
        """Check if client has exceeded rate limits."""
        config = self.ocr_rate_limits.get(endpoint)
        if not config:
            return None

        client_data = self.client_data[client_ip]

        # Check progressive delay
        if (
            client_data.progressive_delay_until
            and current_time < client_data.progressive_delay_until
        ):
            delay_remaining = int(client_data.progressive_delay_until - current_time)

            self.logger.warning(
                "OCR request blocked due to progressive delay",
                extra={
                    "client_ip": client_ip,
                    "endpoint": endpoint,
                    "delay_remaining_seconds": delay_remaining,
                    "violation_count": client_data.violations,
                },
            )

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded - progressive delay active",
                    "error_code": "OCR_RATE_LIMIT_PROGRESSIVE_DELAY",
                    "retry_after": delay_remaining,
                    "message": f"Too many OCR requests. Please wait {delay_remaining} seconds.",
                },
                headers={"Retry-After": str(delay_remaining)},
            )

        # Clean old requests outside window
        window_start = current_time - config.window_seconds
        client_data.requests = [
            req_time for req_time in client_data.requests if req_time > window_start
        ]

        # Check request count
        if len(client_data.requests) >= config.requests_per_window:
            self._handle_rate_limit_violation(
                client_ip, client_data, config, current_time
            )

            retry_after = config.window_seconds
            if client_data.progressive_delay_until:
                retry_after = int(client_data.progressive_delay_until - current_time)

            self.logger.warning(
                "OCR rate limit exceeded",
                extra={
                    "client_ip": client_ip,
                    "endpoint": endpoint,
                    "requests_in_window": len(client_data.requests),
                    "limit": config.requests_per_window,
                    "window_seconds": config.window_seconds,
                    "violation_count": client_data.violations,
                },
            )

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "OCR rate limit exceeded",
                    "error_code": "OCR_RATE_LIMIT_EXCEEDED",
                    "retry_after": retry_after,
                    "message": f"Too many OCR requests. Limit: {config.requests_per_window} per {config.window_seconds//60} minutes.",
                    "requests_remaining": 0,
                },
                headers={"Retry-After": str(retry_after)},
            )

        return None

    def _handle_rate_limit_violation(
        self,
        client_ip: str,
        client_data: ClientOCRData,
        config: OCRRateLimitConfig,
        current_time: float,
    ):
        """Handle rate limit violations with progressive delays."""
        client_data.violations += 1
        client_data.last_violation = current_time

        if config.progressive_delay and client_data.violations > 1:
            # Calculate progressive delay: base delay * (multiplier ^ violations)
            base_delay = 60  # 1 minute base
            multiplier = settings.RATE_LIMIT_PROGRESSIVE_MULTIPLIER
            delay = min(
                base_delay * (multiplier ** (client_data.violations - 1)),
                settings.RATE_LIMIT_MAX_PROGRESSIVE_DELAY,
            )
            client_data.progressive_delay_until = current_time + delay

            self.logger.warning(
                "Progressive delay applied for OCR violations",
                extra={
                    "client_ip": client_ip,
                    "violation_count": client_data.violations,
                    "delay_seconds": delay,
                    "delay_until": client_data.progressive_delay_until,
                },
            )

    async def _validate_request(
        self, request: Request, endpoint: str
    ) -> Optional[JSONResponse]:
        """Validate OCR request for security and compliance."""
        config = self.ocr_rate_limits.get(endpoint)
        if not config:
            return None

        try:
            # Get form data
            form = await request.form()

            if "image" not in form:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "error": "No image file provided",
                        "error_code": "MISSING_IMAGE_FILE",
                    },
                )

            image_file = form["image"]
            if not hasattr(image_file, "read"):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "error": "Invalid image file",
                        "error_code": "INVALID_IMAGE_FILE",
                    },
                )

            # Read file content for validation
            image_content = await image_file.read()

            # Reset file pointer for downstream processing
            if hasattr(image_file, "seek"):
                await image_file.seek(0)

            # Validate file size
            file_size_mb = len(image_content) / (1024 * 1024)
            if file_size_mb > config.max_file_size_mb:
                self.logger.warning(
                    "OCR file size exceeded",
                    extra={
                        "file_size_mb": file_size_mb,
                        "max_size_mb": config.max_file_size_mb,
                        "filename": getattr(image_file, "filename", "unknown"),
                        "endpoint": endpoint,
                    },
                )
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={
                        "error": f"File too large. Maximum size: {config.max_file_size_mb}MB",
                        "error_code": "FILE_TOO_LARGE",
                        "max_size_mb": config.max_file_size_mb,
                    },
                )

            # Validate file format and content
            validation_result = self._validate_image_content(image_content, config)
            if validation_result:
                return validation_result

            return None

        except Exception as e:
            self.logger.error(f"Error validating OCR request: {e}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "Invalid request format",
                    "error_code": "INVALID_REQUEST",
                },
            )

    def _validate_image_content(
        self, image_content: bytes, config: OCRRateLimitConfig
    ) -> Optional[JSONResponse]:
        """Validate image content for security and format compliance."""

        # Check for malicious content patterns
        for pattern in self.suspicious_patterns:
            if pattern in image_content:
                self.logger.error(
                    "Suspicious content detected in uploaded file",
                    extra={
                        "pattern": pattern.decode("utf-8", errors="ignore"),
                        "file_size": len(image_content),
                    },
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "error": "Invalid file content detected",
                        "error_code": "SUSPICIOUS_CONTENT",
                    },
                )

        # Validate MIME type using python-magic (if available)
        try:
            import magic

            mime_type = magic.from_buffer(image_content, mime=True)
            if not mime_type.startswith("image/"):
                self.logger.warning(
                    "Non-image MIME type detected",
                    extra={"detected_mime": mime_type, "file_size": len(image_content)},
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "error": "File is not a valid image",
                        "error_code": "INVALID_IMAGE_TYPE",
                        "detected_type": mime_type,
                    },
                )
        except ImportError:
            # python-magic not available, skip MIME validation
            pass
        except Exception as e:
            self.logger.warning(f"MIME type detection failed: {e}")

        # Validate image using PIL
        try:
            with Image.open(BytesIO(image_content)) as img:
                # Check image dimensions
                width, height = img.size

                if (
                    width < settings.OCR_MIN_IMAGE_WIDTH
                    or height < settings.OCR_MIN_IMAGE_HEIGHT
                ):
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                            "error": f"Image too small. Minimum size: {settings.OCR_MIN_IMAGE_WIDTH}x{settings.OCR_MIN_IMAGE_HEIGHT}",
                            "error_code": "IMAGE_TOO_SMALL",
                            "actual_size": f"{width}x{height}",
                        },
                    )

                if (
                    width > settings.OCR_MAX_IMAGE_WIDTH
                    or height > settings.OCR_MAX_IMAGE_HEIGHT
                ):
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                            "error": f"Image too large. Maximum size: {settings.OCR_MAX_IMAGE_WIDTH}x{settings.OCR_MAX_IMAGE_HEIGHT}",
                            "error_code": "IMAGE_TOO_LARGE",
                            "actual_size": f"{width}x{height}",
                        },
                    )

                # Check image format
                if img.format not in config.allowed_formats:
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                            "error": f"Unsupported image format: {img.format}",
                            "error_code": "UNSUPPORTED_FORMAT",
                            "allowed_formats": config.allowed_formats,
                        },
                    )

                # Verify image integrity
                img.verify()

        except UnidentifiedImageError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "File is not a valid image or is corrupted",
                    "error_code": "INVALID_IMAGE_FILE",
                },
            )
        except Exception as e:
            self.logger.warning(f"Image validation failed: {e}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "Image validation failed",
                    "error_code": "IMAGE_VALIDATION_ERROR",
                },
            )

        return None

    def _record_request(self, client_ip: str, endpoint: str, current_time: float):
        """Record a new request for rate limiting tracking."""
        self.client_data[client_ip].requests.append(current_time)

    def _update_processing_metrics(self, client_ip: str, processing_time: float):
        """Update processing metrics for adaptive rate limiting."""
        client_data = self.client_data[client_ip]
        client_data.total_processing_time += processing_time

        # Log high processing time requests
        if processing_time > 10.0:  # More than 10 seconds
            self.logger.warning(
                "High OCR processing time detected",
                extra={
                    "client_ip": client_ip,
                    "processing_time_seconds": processing_time,
                    "total_processing_time": client_data.total_processing_time,
                },
            )

    def cleanup_old_data(self, max_age_hours: int = 24):
        """Clean up old rate limiting data."""
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)

        clients_to_remove = []
        for client_ip, client_data in self.client_data.items():
            # Remove old requests
            client_data.requests = [
                req_time for req_time in client_data.requests if req_time > cutoff_time
            ]

            # Reset progressive delays if expired
            if (
                client_data.progressive_delay_until
                and current_time > client_data.progressive_delay_until
            ):
                client_data.progressive_delay_until = None
                client_data.violations = 0

            # Remove clients with no recent activity
            if not client_data.requests and (
                not client_data.last_violation
                or client_data.last_violation < cutoff_time
            ):
                clients_to_remove.append(client_ip)

        for client_ip in clients_to_remove:
            del self.client_data[client_ip]

        self.logger.info(f"Cleaned up {len(clients_to_remove)} old client records")
