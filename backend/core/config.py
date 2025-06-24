"""
Enhanced configuration management for the FastAPI application.

This module provides a centralized configuration system using Pydantic's BaseSettings.
Configuration is organized into logical sections with validation and type safety.

Configuration values can be loaded in three ways:
1. Sensitive values are loaded from the .env file (like SUPABASE_KEY, JWT_SECRET)
2. Default values are defined directly in the code
3. All values can be overridden by environment variables with the same name

Example:
    To override APP_NAME, set an environment variable called APP_NAME:
    export APP_NAME="My Custom API"

    To override nested settings with double underscores:
    export RATE_LIMIT__LOGIN_ATTEMPTS=10
"""

import json
import os
import secrets
from enum import Enum
from pprint import pprint
from typing import List, Literal, Optional, Set, Tuple, Union

from pydantic import Field, HttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings

# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================


class Environment(str, Enum):
    """Environment types."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"
    STAGING = "staging"


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OCRLanguage(str, Enum):
    """Supported OCR languages."""

    GERMAN = "deu"
    ENGLISH = "eng"


class JWTAlgorithm(str, Enum):
    """Supported JWT algorithms."""

    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    RS256 = "RS256"


# =============================================================================
# BASE CONFIGURATION CLASSES
# =============================================================================


class AppConfig(BaseSettings):
    """Application-level configuration settings."""

    # Basic App Settings
    APP_NAME: str = Field(default="Cookify Meal Planning API", description="Application name")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    ENVIRONMENT: Environment = Field(
        default=Environment.DEVELOPMENT, description="Runtime environment"
    )
    VERSION: str = Field(
        default="0.1.0",
        pattern=r"^\d+\.\d+\.\d+(-\w+)?$",
        description="Application version",
    )

    # API Documentation
    DOCS_URL: Optional[str] = Field(default="/docs", description="Swagger docs URL")
    REDOC_URL: Optional[str] = Field(default="/redoc", description="ReDoc URL")
    API_V1_PREFIX: str = Field(default="/api", description="API prefix")
    API_TITLE: str = Field(default="Cookify API", description="API title")
    API_DESCRIPTION: str = Field(
        default="REST API for meal planning and recipe management",
        description="API description",
    )
    API_VERSION: str = Field(
        default="1.0.0", pattern=r"^\d+\.\d+\.\d+(-\w+)?$", description="API version"
    )
    API_CONTACT_NAME: str = Field(default="Cookify Support", description="Contact name")
    API_CONTACT_EMAIL: str = Field(default="support@cookify.app", description="Contact email")
    API_LICENSE_NAME: str = Field(default="MIT", description="License name")
    API_TERMS_OF_SERVICE: Optional[HttpUrl] = Field(
        default=None, description="Terms of service URL"
    )

    @field_validator("API_CONTACT_EMAIL")
    @classmethod
    def validate_email(cls, v):
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v


class ServerConfig(BaseSettings):
    """Server and networking configuration."""

    # Server Settings
    SERVER_HOST: str = Field(default="0.0.0.0", description="Server host")
    SERVER_PORT: int = Field(default=8000, ge=1024, le=65535, description="Server port")
    SERVER_WORKERS: int = Field(default=1, ge=1, le=16, description="Number of workers")
    SERVER_RELOAD: bool = Field(default=True, description="Enable auto-reload")

    # Request/Response Settings
    API_MAX_REQUEST_SIZE_MB: int = Field(
        default=10, ge=1, le=100, description="Max request size in MB"
    )
    API_DEFAULT_PAGE_SIZE: int = Field(default=20, ge=1, le=100, description="Default page size")
    API_MAX_PAGE_SIZE: int = Field(default=100, ge=1, le=1000, description="Max page size")
    API_REQUEST_TIMEOUT_SECONDS: int = Field(
        default=30, ge=1, le=300, description="Request timeout"
    )
    API_RESPONSE_CACHE_TTL: int = Field(default=300, ge=0, description="Response cache TTL")
    PAGINATION_DEFAULT_PER_PAGE: int = Field(
        default=20, ge=1, le=100, description="Default pagination per page"
    )


class SecurityConfig(BaseSettings):
    """Security and authentication configuration."""

    # Sensitive values loaded from environment
    SUPABASE_URL: str = Field(
        default_factory=lambda: os.getenv("SUPABASE_URL", ""),
        description="Supabase URL",
    )
    SUPABASE_KEY: str = Field(
        default_factory=lambda: os.getenv("SUPABASE_KEY", ""),
        description="Supabase key",
    )
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET", "") or secrets.token_urlsafe(32),
        min_length=32,
        description="JWT secret key",
    )
    JWT_ALGORITHM: JWTAlgorithm = Field(
        default_factory=lambda: JWTAlgorithm(os.getenv("JWT_ALGORITHM", "HS256")),
        description="JWT algorithm",
    )
    JWT_EXPIRE_MINUTES: int = Field(
        default_factory=lambda: int(os.getenv("JWT_EXPIRATION", "30")),
        ge=1,
        le=1440,
        description="JWT expiration in minutes",
    )
    SESSION_SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("SESSION_SECRET_KEY", "") or secrets.token_urlsafe(32),
        min_length=32,
        description="Session secret key",
    )

    # Authentication Settings
    REQUIRE_EMAIL_VERIFICATION: bool = Field(
        default=False, description="Require email verification"
    )
    PASSWORD_MIN_LENGTH: int = Field(default=8, ge=6, le=128, description="Minimum password length")
    MAX_LOGIN_ATTEMPTS: int = Field(default=5, ge=1, le=10, description="Max login attempts")
    LOCKOUT_DURATION_MINUTES: int = Field(default=15, ge=1, le=1440, description="Lockout duration")
    FRONTEND_URL: HttpUrl = Field(default="http://localhost:3000", description="Frontend URL")

    # Security Headers
    SECURITY_HEADERS_ENABLED: bool = Field(default=True, description="Enable security headers")
    HSTS_MAX_AGE: int = Field(default=31536000, ge=0, description="HSTS max age")
    SECURITY_HSTS_MAX_AGE_DEFAULT: int = Field(
        default=31536000, ge=0, description="Default HSTS max age fallback"
    )
    HSTS_INCLUDE_SUBDOMAINS: bool = Field(default=True, description="HSTS include subdomains")
    HSTS_PRELOAD: bool = Field(default=False, description="HSTS preload")
    CSP_REPORT_URI: Optional[HttpUrl] = Field(default=None, description="CSP report URI")
    CUSTOM_SECURITY_HEADERS: Optional[dict] = Field(
        default=None, description="Custom security headers"
    )

    # Security Header Values
    SECURITY_CONTENT_TYPE_OPTIONS: str = Field(
        default="nosniff", description="X-Content-Type-Options header value"
    )
    SECURITY_FRAME_OPTIONS: str = Field(default="DENY", description="X-Frame-Options header value")
    SECURITY_XSS_PROTECTION: str = Field(
        default="1; mode=block", description="X-XSS-Protection header value"
    )
    SECURITY_REFERRER_POLICY: str = Field(
        default="strict-origin-when-cross-origin",
        description="Referrer-Policy header value",
    )
    SECURITY_PERMISSIONS_POLICY: str = Field(
        default="camera=(), microphone=(), geolocation=()",
        description="Permissions-Policy header value",
    )

    # Content Security Policy (CSP) Directives
    CSP_DEFAULT_SRC: str = Field(default="'self'", description="CSP default-src directive")
    CSP_SCRIPT_SRC: str = Field(
        default="'self' 'unsafe-inline'", description="CSP script-src directive"
    )
    CSP_SCRIPT_SRC_DEV: str = Field(
        default="'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com",
        description="CSP script-src directive for development",
    )
    CSP_SCRIPT_SRC_PROD: str = Field(
        default="'self'", description="CSP script-src directive for production"
    )
    CSP_STYLE_SRC: str = Field(
        default="'self' 'unsafe-inline'", description="CSP style-src directive"
    )
    CSP_STYLE_SRC_DEV: str = Field(
        default="'self' 'unsafe-inline' localhost:* 127.0.0.1:* https://cdn.jsdelivr.net https://unpkg.com https://fonts.googleapis.com",
        description="CSP style-src directive for development",
    )
    CSP_STYLE_SRC_PROD: str = Field(
        default="'self' 'unsafe-inline'",
        description="CSP style-src directive for production",
    )
    CSP_IMG_SRC: str = Field(default="'self' data: https:", description="CSP img-src directive")
    CSP_IMG_SRC_DEV: str = Field(
        default="'self' data: blob: localhost:* 127.0.0.1:*",
        description="CSP img-src directive for development",
    )
    CSP_CONNECT_SRC: str = Field(default="'self'", description="CSP connect-src directive")
    CSP_CONNECT_SRC_DEV: str = Field(
        default="'self' localhost:* 127.0.0.1:* ws: wss:",
        description="CSP connect-src directive for development",
    )
    CSP_CONNECT_SRC_PROD: str = Field(
        default="'self'", description="CSP connect-src directive for production"
    )
    CSP_FONT_SRC: str = Field(default="'self' https:", description="CSP font-src directive")
    CSP_FONT_SRC_DEV: str = Field(
        default="'self' https: data: https://fonts.gstatic.com https://cdn.jsdelivr.net",
        description="CSP font-src directive for development",
    )
    CSP_FONT_SRC_PROD: str = Field(
        default="'self' https:", description="CSP font-src directive for production"
    )
    CSP_FRAME_ANCESTORS: str = Field(default="'none'", description="CSP frame-ancestors directive")
    CSP_OBJECT_SRC: str = Field(default="'none'", description="CSP object-src directive")
    CSP_MEDIA_SRC: str = Field(default="'self'", description="CSP media-src directive")
    CSP_FRAME_SRC: str = Field(default="'none'", description="CSP frame-src directive")
    CSP_CHILD_SRC: str = Field(default="'none'", description="CSP child-src directive")
    CSP_FORM_ACTION: str = Field(default="'self'", description="CSP form-action directive")
    CSP_BASE_URI: str = Field(default="'self'", description="CSP base-uri directive")
    CSP_MANIFEST_SRC: str = Field(default="'self'", description="CSP manifest-src directive")
    CSP_WORKER_SRC: str = Field(default="'self'", description="CSP worker-src directive")

    # Permissions Policy Settings
    PERMISSIONS_POLICY_CAMERA: str = Field(
        default="()", description="Permissions policy for camera"
    )
    PERMISSIONS_POLICY_MICROPHONE: str = Field(
        default="()", description="Permissions policy for microphone"
    )
    PERMISSIONS_POLICY_GEOLOCATION: str = Field(
        default="()", description="Permissions policy for geolocation"
    )
    PERMISSIONS_POLICY_PAYMENT: str = Field(
        default="()", description="Permissions policy for payment"
    )
    PERMISSIONS_POLICY_USB: str = Field(default="()", description="Permissions policy for USB")
    PERMISSIONS_POLICY_MAGNETOMETER: str = Field(
        default="()", description="Permissions policy for magnetometer"
    )
    PERMISSIONS_POLICY_GYROSCOPE: str = Field(
        default="()", description="Permissions policy for gyroscope"
    )
    PERMISSIONS_POLICY_ACCELEROMETER: str = Field(
        default="()", description="Permissions policy for accelerometer"
    )
    PERMISSIONS_POLICY_AMBIENT_LIGHT: str = Field(
        default="()", description="Permissions policy for ambient light sensor"
    )
    PERMISSIONS_POLICY_AUTOPLAY: str = Field(
        default="()", description="Permissions policy for autoplay"
    )
    PERMISSIONS_POLICY_ENCRYPTED_MEDIA: str = Field(
        default="()", description="Permissions policy for encrypted media"
    )
    PERMISSIONS_POLICY_FULLSCREEN: str = Field(
        default="(self)", description="Permissions policy for fullscreen"
    )
    PERMISSIONS_POLICY_PICTURE_IN_PICTURE: str = Field(
        default="()", description="Permissions policy for picture-in-picture"
    )

    @field_validator("SUPABASE_URL")
    @classmethod
    def validate_supabase_url(cls, v):
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("SUPABASE_URL must be a valid URL")
        return v


class CORSConfig(BaseSettings):
    """CORS and middleware configuration."""

    CORS_ORIGINS: List[str] = Field(default=[], description="CORS origins")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow credentials")
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        description="Allowed methods",
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=["Authorization", "Content-Type", "X-Request-ID"],
        description="Allowed headers",
    )

    # Middleware Settings
    TRUSTED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"], description="Trusted hosts"
    )
    ENABLE_TRUSTED_HOST_MIDDLEWARE: bool = Field(
        default=True, description="Enable trusted host middleware"
    )
    SESSION_HTTPS_ONLY: bool = Field(default=True, description="HTTPS only sessions")
    SESSION_SAME_SITE: Literal["strict", "lax", "none"] = Field(
        default="strict", description="SameSite cookie setting"
    )


class RateLimitConfig(BaseSettings):
    """Rate limiting configuration."""

    RATE_LIMITING_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_LOGIN_ATTEMPTS: int = Field(default=5, ge=1, le=20, description="Login rate limit")
    RATE_LIMIT_LOGIN_WINDOW_MINUTES: int = Field(
        default=15, ge=1, le=60, description="Login window"
    )
    RATE_LIMIT_REGISTRATION_ATTEMPTS: int = Field(
        default=3, ge=1, le=10, description="Registration rate limit"
    )
    RATE_LIMIT_REGISTRATION_WINDOW_MINUTES: int = Field(
        default=5, ge=1, le=30, description="Registration window"
    )
    RATE_LIMIT_PASSWORD_RESET_ATTEMPTS: int = Field(
        default=3, ge=1, le=10, description="Password reset rate limit"
    )
    RATE_LIMIT_PASSWORD_RESET_WINDOW_MINUTES: int = Field(
        default=60, ge=1, le=240, description="Password reset window"
    )

    # Password reset confirmation settings (separate from initiation)
    RATE_LIMIT_RESET_PASSWORD_ATTEMPTS: int = Field(
        default=5, ge=1, le=15, description="Password reset confirmation attempts"
    )
    RATE_LIMIT_RESET_PASSWORD_WINDOW: int = Field(
        default=900,
        ge=300,
        le=3600,
        description="Password reset confirmation window in seconds",
    )

    # Email verification settings
    RATE_LIMIT_VERIFY_EMAIL_ATTEMPTS: int = Field(
        default=3, ge=1, le=10, description="Email verification attempts"
    )
    RATE_LIMIT_VERIFY_EMAIL_WINDOW: int = Field(
        default=300, ge=60, le=1800, description="Email verification window in seconds"
    )

    # Resend verification settings
    RATE_LIMIT_RESEND_VERIFICATION_ATTEMPTS: int = Field(
        default=2, ge=1, le=5, description="Resend verification attempts"
    )
    RATE_LIMIT_RESEND_VERIFICATION_WINDOW: int = Field(
        default=600,
        ge=300,
        le=1800,
        description="Resend verification window in seconds",
    )

    # Refresh token settings
    RATE_LIMIT_REFRESH_TOKEN_ATTEMPTS: int = Field(
        default=10, ge=1, le=50, description="Refresh token attempts"
    )
    RATE_LIMIT_REFRESH_TOKEN_WINDOW: int = Field(
        default=300, ge=60, le=1800, description="Refresh token window in seconds"
    )

    # Default auth settings (fallback)
    RATE_LIMIT_DEFAULT_AUTH_ATTEMPTS: int = Field(
        default=5, ge=1, le=20, description="Default auth attempts"
    )
    RATE_LIMIT_DEFAULT_AUTH_WINDOW: int = Field(
        default=900, ge=300, le=3600, description="Default auth window in seconds"
    )

    RATE_LIMIT_PROGRESSIVE_MULTIPLIER: float = Field(
        default=2.0, ge=1.0, le=5.0, description="Progressive multiplier"
    )
    RATE_LIMIT_MAX_PROGRESSIVE_DELAY: int = Field(
        default=300, ge=60, le=3600, description="Max progressive delay"
    )
    RATE_LIMIT_CLEANUP_INTERVAL: int = Field(
        default=600, ge=60, le=3600, description="Cleanup interval"
    )

    # Additional rate limiting utility settings
    RATE_LIMIT_USER_AGENT_LENGTH: int = Field(
        default=50, ge=10, le=200, description="User agent string length for tracking"
    )
    RATE_LIMIT_CLEANUP_CUTOFF: int = Field(
        default=3600, ge=600, le=86400, description="Cleanup cutoff time in seconds"
    )

    # OCR-specific rate limiting (resource-intensive operations)
    RATE_LIMIT_OCR_ATTEMPTS: int = Field(
        default=10,
        ge=1,
        le=50,
        description="OCR requests per window (resource-intensive)",
    )
    RATE_LIMIT_OCR_WINDOW_MINUTES: int = Field(
        default=5, ge=1, le=30, description="OCR rate limit window in minutes"
    )
    RATE_LIMIT_OCR_EXTRACT_ATTEMPTS: int = Field(
        default=5, ge=1, le=20, description="OCR text extraction per window"
    )
    RATE_LIMIT_OCR_EXTRACT_WINDOW_MINUTES: int = Field(
        default=2, ge=1, le=15, description="OCR text extraction window in minutes"
    )
    RATE_LIMIT_OCR_PROCESS_ATTEMPTS: int = Field(
        default=8, ge=1, le=30, description="OCR processing per window"
    )
    RATE_LIMIT_OCR_PROCESS_WINDOW_MINUTES: int = Field(
        default=3, ge=1, le=20, description="OCR processing window in minutes"
    )
    RATE_LIMIT_OCR_ENABLE_PROGRESSIVE_DELAY: bool = Field(
        default=True, description="Enable progressive delay for OCR violations"
    )


class DatabaseConfig(BaseSettings):
    """Database configuration and connection settings."""

    # Connection Settings
    DB_CONNECTION_POOL_SIZE: int = Field(
        default=10, ge=1, le=50, description="Connection pool size"
    )
    DB_CONNECTION_POOL_MAX_OVERFLOW: int = Field(
        default=20, ge=0, le=100, description="Max pool overflow"
    )
    DB_QUERY_TIMEOUT_SECONDS: int = Field(default=30, ge=1, le=300, description="Query timeout")
    DB_CONNECTION_TIMEOUT_SECONDS: int = Field(
        default=10, ge=1, le=60, description="Connection timeout"
    )
    DB_TRANSACTION_TIMEOUT_SECONDS: int = Field(
        default=60, ge=1, le=600, description="Transaction timeout"
    )
    DB_RETRY_ATTEMPTS: int = Field(default=3, ge=0, le=10, description="Retry attempts")
    DB_RETRY_DELAY_SECONDS: float = Field(default=1.0, ge=0.1, le=10.0, description="Retry delay")
    DB_ENABLE_QUERY_LOGGING: bool = Field(default=False, description="Enable query logging")
    DB_SLOW_QUERY_THRESHOLD_MS: int = Field(
        default=1000, ge=100, le=10000, description="Slow query threshold"
    )

    # Field Length Settings
    DB_EMAIL_MAX_LENGTH: int = Field(default=255, ge=50, le=500, description="Email field length")
    DB_PASSWORD_MAX_LENGTH: int = Field(
        default=255, ge=50, le=500, description="Password field length"
    )
    DB_TOKEN_MAX_LENGTH: int = Field(default=255, ge=50, le=500, description="Token field length")
    DB_STRING_DEFAULT_LENGTH: int = Field(
        default=255, ge=50, le=500, description="Default string length"
    )
    DB_DISPLAY_NAME_MAX_LENGTH: int = Field(
        default=100, ge=10, le=200, description="Display name length"
    )
    DB_PHONE_MAX_LENGTH: int = Field(default=20, ge=10, le=30, description="Phone number length")
    DB_URL_MAX_LENGTH: int = Field(default=2048, ge=100, le=4096, description="URL field length")
    DB_TEXT_FIELD_MAX_LENGTH: int = Field(
        default=1000, ge=100, le=5000, description="Text field max length"
    )
    DB_STATUS_CODE_LENGTH: int = Field(
        default=20, ge=5, le=50, description="Status code field length"
    )
    DB_CODE_LENGTH: int = Field(default=6, ge=4, le=12, description="Verification code length")
    DB_ROLE_LENGTH: int = Field(default=50, ge=10, le=100, description="User role field length")
    DB_PROVIDER_LENGTH: int = Field(
        default=50, ge=5, le=100, description="Auth provider field length"
    )
    DB_FIRST_NAME_MAX_LENGTH: int = Field(
        default=100, ge=10, le=200, description="First name field length"
    )
    DB_LAST_NAME_MAX_LENGTH: int = Field(
        default=100, ge=10, le=200, description="Last name field length"
    )
    DB_BIO_MAX_LENGTH: int = Field(default=500, ge=50, le=2000, description="User bio field length")
    DB_LOCATION_MAX_LENGTH: int = Field(
        default=100, ge=10, le=200, description="Location field length"
    )
    DB_TIMEZONE_MAX_LENGTH: int = Field(
        default=50, ge=10, le=100, description="Timezone field length"
    )
    DB_LANGUAGE_CODE_LENGTH: int = Field(
        default=10, ge=2, le=20, description="Language code field length"
    )


class CacheConfig(BaseSettings):
    """Caching configuration."""

    USER_CACHE_TTL_SECONDS: int = Field(default=300, ge=60, le=3600, description="User cache TTL")
    ENABLE_USER_CACHE: bool = Field(default=True, description="Enable user cache")
    CACHE_DEFAULT_TTL_SECONDS: int = Field(
        default=1800, ge=60, le=7200, description="Default cache TTL"
    )
    CACHE_MAX_SIZE: int = Field(default=1000, ge=100, le=10000, description="Max cache size")
    CACHE_ENABLE_COMPRESSION: bool = Field(default=True, description="Enable compression")
    CACHE_CLEANUP_INTERVAL_SECONDS: int = Field(
        default=3600, ge=300, le=7200, description="Cleanup interval"
    )


class LoggingConfig(BaseSettings):
    """Logging configuration."""

    LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format",
    )
    LOG_FORMAT_JSON: bool = Field(default=False, description="JSON log format")
    CONSOLE_LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, description="Console log level")
    LOG_TO_FILE: bool = Field(default=False, description="Log to file")
    LOG_DIR: str = Field(default="backend/logs", description="Log directory")
    ENABLE_ACCESS_LOG: bool = Field(default=True, description="Enable access log")

    # Domain-specific logging
    DOMAINS_LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, description="Domains log level")
    MIDDLEWARE_LOG_LEVEL: LogLevel = Field(
        default=LogLevel.INFO, description="Middleware log level"
    )
    MIDDLEWARE_DURATION_DECIMAL_PLACES: int = Field(
        default=3,
        ge=1,
        le=6,
        description="Decimal places for middleware duration logging",
    )
    MIDDLEWARE_HTTP_SERVER_ERROR_THRESHOLD: int = Field(
        default=500,
        ge=400,
        le=599,
        description="HTTP status code threshold for server errors",
    )
    MIDDLEWARE_HTTP_CLIENT_ERROR_THRESHOLD: int = Field(
        default=400,
        ge=400,
        le=499,
        description="HTTP status code threshold for client errors",
    )
    SHARED_LOG_LEVEL: LogLevel = Field(
        default=LogLevel.INFO, description="Shared modules log level"
    )


class MonitoringConfig(BaseSettings):
    """Monitoring and metrics configuration."""

    MONITORING_ENABLED: bool = Field(default=True, description="Enable monitoring")
    METRICS_COLLECTION_ENABLED: bool = Field(default=True, description="Enable metrics collection")
    PERFORMANCE_MONITORING_ENABLED: bool = Field(
        default=True, description="Enable performance monitoring"
    )
    ERROR_TRACKING_ENABLED: bool = Field(default=True, description="Enable error tracking")
    TRACE_SAMPLING_RATE: float = Field(
        default=0.1, ge=0.0, le=1.0, description="Trace sampling rate"
    )
    METRICS_EXPORT_INTERVAL_SECONDS: int = Field(
        default=60, ge=10, le=300, description="Metrics export interval"
    )
    MONITORING_ENDPOINT_PREFIX: str = Field(
        default="/metrics", description="Monitoring endpoint prefix"
    )
    MONITORING_REQUIRE_AUTH: bool = Field(default=False, description="Require auth for monitoring")


class PasswordConfig(BaseSettings):
    """Password validation and security configuration."""

    PASSWORD_MIN_SECURITY_LENGTH: int = Field(
        default=6, ge=4, le=32, description="Min security length"
    )
    PASSWORD_MAX_LENGTH: int = Field(default=128, ge=32, le=256, description="Max password length")
    PASSWORD_MIN_UNIQUE_CHARS: int = Field(default=6, ge=3, le=20, description="Min unique chars")
    PASSWORD_MAX_REPEATED_CHAR_RATIO: float = Field(
        default=0.4, ge=0.1, le=0.8, description="Max repeated char ratio"
    )
    PASSWORD_MIN_CHAR_TYPES: int = Field(default=3, ge=1, le=4, description="Min character types")
    PASSWORD_MIN_ENTROPY_SCORE: int = Field(
        default=35, ge=10, le=100, description="Min entropy score"
    )
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(default=True, description="Require uppercase")
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(default=True, description="Require lowercase")
    PASSWORD_REQUIRE_DIGITS: bool = Field(default=True, description="Require digits")
    PASSWORD_REQUIRE_SPECIAL: bool = Field(default=True, description="Require special chars")

    # Password Complexity
    PASSWORD_SPECIAL_CHARS: str = Field(
        default="!@#$%^&*()_+-=[]{}|;:,.<>?",
        min_length=10,
        description="Special characters",
    )
    PASSWORD_FORBIDDEN_PATTERNS: List[str] = Field(
        default=[
            r"(.)\1{3,}",  # 4+ repeated characters
            r"(0123|1234|2345|3456|4567|5678|6789)",  # Sequential numbers
            r"^(password|admin|user|guest)$",  # Common passwords
        ],
        description="Forbidden patterns",
    )

    # Password Strength Thresholds
    PASSWORD_STRENGTH_VERY_WEAK_THRESHOLD: int = Field(
        default=10, ge=0, le=50, description="Very weak password threshold"
    )
    PASSWORD_STRENGTH_WEAK_THRESHOLD: int = Field(
        default=20, ge=10, le=60, description="Weak password threshold"
    )
    PASSWORD_STRENGTH_FAIR_THRESHOLD: int = Field(
        default=35, ge=20, le=70, description="Fair password threshold"
    )
    PASSWORD_STRENGTH_GOOD_THRESHOLD: int = Field(
        default=50, ge=30, le=80, description="Good password threshold"
    )
    PASSWORD_STRENGTH_STRONG_THRESHOLD: int = Field(
        default=70, ge=50, le=90, description="Strong password threshold"
    )
    PASSWORD_STRENGTH_VERY_STRONG_THRESHOLD: int = Field(
        default=90, ge=70, le=100, description="Very strong password threshold"
    )

    # Common Passwords
    COMMON_PASSWORD_DICTIONARY: List[str] = Field(
        default=[
            "password",
            "123456",
            "password123",
            "admin",
            "qwerty",
            "abc123",
            "letmein",
            "monkey",
            "password1",
            "123456789",
            "welcome",
            "admin123",
            "user",
            "guest",
            "login",
            "root",
            "test",
            "demo",
            "sample",
            "example",
        ],
        description="List of common passwords to reject",
    )
    COMMON_PASSWORD_SUFFIX_LIST: List[str] = Field(
        default=["123", "!", "1", "2023", "2024", "01", "99", "@", "#"],
        description="Common password suffixes",
    )
    COMMON_PASSWORD_PREFIX_LIST: List[str] = Field(
        default=["admin", "user", "test", "demo", "guest"],
        description="Common password prefixes",
    )
    COMMON_PASSWORD_YEAR_LIST: List[str] = Field(
        default=["2023", "2024", "2022", "2021", "2020"],
        description="Common password years",
    )
    COMMON_PASSWORD_MIN_VARIATION_LENGTH: int = Field(
        default=3, ge=2, le=10, description="Minimum length for password variations"
    )
    COMMON_PASSWORD_SUBSTITUTIONS: List[Tuple[str, str]] = Field(
        default=[
            ("password", "p@ssw0rd"),
            ("admin", "@dmin"),
            ("user", "us3r"),
            ("login", "l0gin"),
            ("welcome", "w3lc0m3"),
        ],
        description="Common password substitution patterns",
    )
    LEET_SPEAK_SUBSTITUTIONS: dict = Field(
        default={
            "a": ["@", "4"],
            "e": ["3"],
            "i": ["1", "!"],
            "o": ["0"],
            "s": ["5", "$"],
            "t": ["7"],
            "l": ["1"],
            "g": ["9"],
            "b": ["6"],
        },
        description="Leet speak character substitutions",
    )


class OCRConfig(BaseSettings):
    """OCR processing configuration."""

    # Image processing settings
    OCR_MAX_IMAGE_SIZE_BYTES: int = Field(
        default=5242880, ge=1048576, le=52428800, description="Max image size (5MB)"
    )
    OCR_ALLOWED_IMAGE_FORMATS: List[str] = Field(
        default=["JPEG", "JPG", "PNG", "WEBP", "BMP", "TIFF"],
        description="Allowed image formats",
    )
    OCR_MIN_IMAGE_WIDTH: int = Field(default=100, ge=50, le=1000, description="Min image width")
    OCR_MIN_IMAGE_HEIGHT: int = Field(default=100, ge=50, le=1000, description="Min image height")
    OCR_MAX_IMAGE_WIDTH: int = Field(default=4000, ge=1000, le=8000, description="Max image width")
    OCR_MAX_IMAGE_HEIGHT: int = Field(
        default=4000, ge=1000, le=8000, description="Max image height"
    )
    OCR_DEFAULT_DPI: int = Field(default=300, ge=72, le=600, description="Default DPI")
    OCR_PREPROCESSING_ENABLED: bool = Field(default=True, description="Enable preprocessing")
    OCR_GAUSSIAN_BLUR_RADIUS: float = Field(
        default=0.5,
        ge=0.1,
        le=2.0,
        description="Gaussian blur radius for preprocessing",
    )

    # OCR processing settings
    OCR_CONFIDENCE_THRESHOLD: float = Field(
        default=0.6, ge=0.0, le=1.0, description="Confidence threshold"
    )
    OCR_MIN_CONFIDENCE_SCORE: float = Field(
        default=30.0, ge=0.0, le=100.0, description="Minimum confidence score"
    )
    OCR_PROCESSING_TIMEOUT: int = Field(default=30, ge=5, le=120, description="Processing timeout")
    OCR_DEFAULT_LANGUAGE: OCRLanguage = Field(
        default=OCRLanguage.GERMAN, description="Default language"
    )
    OCR_SUPPORTED_LANGUAGES: List[OCRLanguage] = Field(
        default=[OCRLanguage.GERMAN, OCRLanguage.ENGLISH],
        description="Supported languages",
    )

    # Tesseract configuration
    OCR_TESSERACT_PATHS: List[str] = Field(
        default=[
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract",
            "/opt/homebrew/bin/tesseract",
        ],
        description="Possible tesseract executable paths",
    )
    OCR_TESSERACT_CMD_ENV_VAR: str = Field(
        default="TESSERACT_CMD",
        description="Environment variable for tesseract command",
    )
    OCR_CHAR_WHITELIST: str = Field(
        default="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,$()- ",
        description="Character whitelist for OCR",
    )

    # Tesseract PSM (Page Segmentation Mode) configurations
    OCR_PRIMARY_CONFIG: str = Field(
        default="--psm 6 --oem 1", description="Primary OCR configuration"
    )
    OCR_FALLBACK_PSM_4_CONFIG: str = Field(
        default="--psm 4 --oem 1", description="Fallback PSM 4 configuration"
    )
    OCR_FALLBACK_PSM_11_CONFIG: str = Field(
        default="--psm 11 --oem 1", description="Fallback PSM 11 configuration"
    )
    OCR_DEFAULT_CONFIG: str = Field(default="--psm 6", description="Default OCR configuration")
    OCR_SIMPLE_CONFIG: str = Field(default="--psm 6", description="Simple OCR configuration")

    # Price extraction settings
    OCR_MIN_PRICE: float = Field(
        default=0.01, ge=0.0, le=10.0, description="Minimum reasonable price"
    )
    OCR_MAX_PRICE: float = Field(
        default=999.99, ge=100.0, le=10000.0, description="Maximum reasonable price"
    )


class ValidationConfig(BaseSettings):
    """Input validation configuration."""

    # Validation settings that were referenced in validation_config.py
    VALIDATION_MAX_REPEATED_CHARS_RATIO: float = Field(
        default=0.4,
        ge=0.1,
        le=0.8,
        description="Max repeated char ratio for validation",
    )
    VALIDATION_MAX_TOTAL_SIZE_BYTES: int = Field(
        default=10240,
        ge=1024,
        le=102400,
        description="Max total size in bytes for metadata validation (10KB)",
    )

    # Additional validation settings
    VALIDATION_MAX_STRING_LENGTH: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Max string length for general validation",
    )
    VALIDATION_MAX_SEARCH_QUERY_LENGTH: int = Field(
        default=200, ge=50, le=1000, description="Max search query length"
    )
    VALIDATION_MAX_FILENAME_LENGTH: int = Field(
        default=255, ge=50, le=512, description="Max filename length"
    )
    VALIDATION_MAX_JSON_DEPTH: int = Field(
        default=10, ge=3, le=50, description="Max JSON nesting depth"
    )
    VALIDATION_FORBIDDEN_CONTROL_CHARS: bool = Field(
        default=True, description="Forbid control characters"
    )
    VALIDATION_HTML_ESCAPE_BY_DEFAULT: bool = Field(
        default=True, description="HTML escape by default"
    )
    VALIDATION_STRIP_WHITESPACE: bool = Field(
        default=True, description="Strip whitespace by default"
    )

    # Email validation settings
    EMAIL_MAX_LENGTH: int = Field(default=254, ge=50, le=320, description="Maximum email length")
    EMAIL_MIN_LENGTH: int = Field(default=5, ge=3, le=20, description="Minimum email length")
    EMAIL_DANGEROUS_CHARS: str = Field(
        default="<>\"'&;\\", description="Dangerous characters in email"
    )

    # UUID validation settings
    UUID_LENGTH: int = Field(default=36, description="Standard UUID length")
    UUID_PATTERN: str = Field(
        default=r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        description="UUID validation pattern",
    )

    # Input validation settings
    INPUT_MAX_STRING_LENGTH: int = Field(
        default=1000, ge=100, le=10000, description="Max input string length"
    )
    INPUT_HTML_ESCAPE_BY_DEFAULT: bool = Field(
        default=True, description="HTML escape input by default"
    )
    INPUT_STRIP_WHITESPACE: bool = Field(default=True, description="Strip whitespace from input")
    INPUT_FORBIDDEN_CONTROL_CHARS: bool = Field(
        default=True, description="Forbid control characters in input"
    )
    CONTROL_CHARS_PATTERN: str = Field(
        default=r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]",
        description="Control characters pattern",
    )
    INPUT_MAX_FILENAME_LENGTH: int = Field(
        default=255, ge=50, le=512, description="Max input filename length"
    )
    INPUT_MAX_JSON_DEPTH: int = Field(default=10, ge=3, le=50, description="Max input JSON depth")
    INPUT_MAX_SEARCH_QUERY_LENGTH: int = Field(
        default=200, ge=50, le=1000, description="Max input search query length"
    )

    # URL validation settings
    URL_ALLOWED_SCHEMES: List[str] = Field(
        default=["http", "https"], description="Allowed URL schemes"
    )
    URL_ALLOWED_DOMAINS: List[str] = Field(
        default=[], description="Allowed domains (empty = all allowed)"
    )
    URL_ALLOW_LOCALHOST: bool = Field(default=True, description="Allow localhost URLs")
    DB_URL_MAX_LENGTH: int = Field(
        default=2048, ge=100, le=4096, description="Maximum database URL length"
    )

    # Hostname validation
    HOSTNAME_VALIDATION_PATTERN: str = Field(
        default=r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$",
        description="Hostname validation pattern",
    )

    # Phone validation settings
    PHONE_STRICT_INTERNATIONAL: bool = Field(
        default=False, description="Strict international phone validation"
    )
    PHONE_MIN_LENGTH: int = Field(default=7, ge=5, le=15, description="Minimum phone number length")
    PHONE_MAX_LENGTH: int = Field(
        default=15, ge=10, le=20, description="Maximum phone number length"
    )

    # Metadata validation settings
    VALIDATION_METADATA_MAX_KEY_LENGTH: int = Field(
        default=100, ge=10, le=255, description="Max metadata key length"
    )
    VALIDATION_METADATA_MAX_TOTAL_SIZE: int = Field(
        default=10240, ge=1024, le=102400, description="Max metadata total size"
    )
    METADATA_MAX_STRING_VALUE_LENGTH: int = Field(
        default=1000, ge=100, le=5000, description="Max metadata string value length"
    )
    METADATA_MAX_LIST_ITEMS: int = Field(
        default=100, ge=10, le=1000, description="Max items in metadata list"
    )

    # Date validation settings
    DATE_WEEK_DAYS: int = Field(default=7, description="Number of days in a week")

    # Additional validation settings for personal info checks
    VALIDATION_EMAIL_MIN_LENGTH: int = Field(
        default=3,
        ge=2,
        le=10,
        description="Min length for email parts in password check",
    )
    VALIDATION_NAME_MIN_LENGTH: int = Field(
        default=2, ge=1, le=5, description="Min length for name parts in password check"
    )
    VALIDATION_USER_ID_MIN_LENGTH: int = Field(
        default=3, ge=2, le=10, description="Min length for user ID in password check"
    )

    # Password strength calculation settings
    PASSWORD_RECOMMENDED_MIN_LENGTH: int = Field(
        default=12, ge=8, le=20, description="Recommended minimum password length"
    )
    PASSWORD_BONUS_MIN_LENGTH: int = Field(
        default=16, ge=12, le=25, description="Bonus minimum password length"
    )
    PASSWORD_MIN_UNIQUE_CHARS_BONUS: int = Field(
        default=8, ge=5, le=15, description="Minimum unique chars for bonus"
    )

    # Entropy calculation settings
    ENTROPY_LOWERCASE_CHARS: int = Field(
        default=26, description="Number of lowercase characters for entropy"
    )
    ENTROPY_UPPERCASE_CHARS: int = Field(
        default=26, description="Number of uppercase characters for entropy"
    )
    ENTROPY_DIGIT_CHARS: int = Field(
        default=10, description="Number of digit characters for entropy"
    )

    # Password strength thresholds
    PASSWORD_STRENGTH_VERY_STRONG_THRESHOLD: int = Field(
        default=90, ge=80, le=100, description="Very strong password threshold"
    )
    PASSWORD_STRENGTH_STRONG_THRESHOLD: int = Field(
        default=80, ge=70, le=90, description="Strong password threshold"
    )
    PASSWORD_STRENGTH_GOOD_THRESHOLD: int = Field(
        default=60, ge=50, le=70, description="Good password threshold"
    )
    PASSWORD_STRENGTH_FAIR_THRESHOLD: int = Field(
        default=40, ge=30, le=50, description="Fair password threshold"
    )
    PASSWORD_STRENGTH_WEAK_THRESHOLD: int = Field(
        default=20, ge=10, le=30, description="Weak password threshold"
    )

    # Pattern lists for password validation
    INCREMENTAL_PATTERN_LIST: List[str] = Field(
        default=[
            "123",
            "234",
            "345",
            "456",
            "567",
            "678",
            "789",
            "abc",
            "bcd",
            "cde",
            "def",
        ],
        description="Incremental patterns to detect in passwords",
    )
    ALTERNATING_PATTERN_LIST: List[str] = Field(
        default=["aba", "121", "010", "aba", "cdc", "efe"],
        description="Alternating patterns to detect in passwords",
    )

    # Metadata forbidden keys
    METADATA_FORBIDDEN_KEYS: List[str] = Field(
        default=["password", "secret", "key", "token", "auth", "session", "private"],
        description="Forbidden keys in metadata",
    )

    # User registration validation
    USER_REGISTRATION_REQUIRED_FIELDS: List[str] = Field(
        default=["email", "password"],
        description="Required fields for user registration",
    )

    # Password reset validation
    PASSWORD_RESET_REQUIRED_FIELDS: List[str] = Field(
        default=["email"], description="Required fields for password reset"
    )

    # Password update validation
    PASSWORD_UPDATE_REQUIRED_FIELDS: List[str] = Field(
        default=["password"], description="Required fields for password update"
    )

    # Magic link validation
    MAGIC_LINK_REQUIRED_FIELDS: List[str] = Field(
        default=["email"], description="Required fields for magic link request"
    )

    # OTP verification validation
    OTP_VERIFICATION_REQUIRED_FIELDS: List[str] = Field(
        default=["email", "token", "type"],
        description="Required fields for OTP verification",
    )

    # OTP token validation
    OTP_TOKEN_MIN_LENGTH: int = Field(default=4, ge=4, le=6, description="Minimum OTP token length")
    OTP_TOKEN_MAX_LENGTH: int = Field(
        default=10, ge=6, le=12, description="Maximum OTP token length"
    )

    # OTP allowed types
    OTP_ALLOWED_TYPES: List[str] = Field(
        default=["email", "sms", "phone_change"],
        description="Allowed OTP verification types",
    )

    # Search validation
    SEARCH_LIMIT_MAX_VALUE: int = Field(
        default=100, ge=50, le=500, description="Maximum search results limit"
    )
    SEARCH_LIMIT_MIN_VALUE: int = Field(
        default=1, ge=1, le=10, description="Minimum search results limit"
    )

    # Pagination validation
    PAGINATION_PER_PAGE_MAX: int = Field(
        default=100, ge=50, le=500, description="Maximum items per page"
    )
    PAGINATION_PER_PAGE_MIN: int = Field(
        default=1, ge=1, le=10, description="Minimum items per page"
    )
    PAGINATION_PAGE_MIN: int = Field(default=1, description="Minimum page number")

    # API sorting validation
    API_SORT_BY_MAX_LENGTH: int = Field(
        default=50, ge=20, le=100, description="Maximum length for sort_by field"
    )
    API_ALLOWED_SORT_ORDERS: List[str] = Field(
        default=["asc", "desc"], description="Allowed sort orders"
    )


class UpdateConfig(BaseSettings):
    """Update and cache configuration."""

    # Ingredient cache file paths
    UPDATE_INGREDIENT_CACHE_FILE_PATH: str = Field(
        default="data/ingredient_names.txt",
        description="Path to ingredient names cache file",
    )
    UPDATE_INGREDIENT_CACHE_METADATA_FILE: str = Field(
        default="data/ingredient_names_metadata.json",
        description="Path to ingredient names metadata file",
    )

    # Cache settings
    UPDATE_CACHE_TTL_HOURS: int = Field(default=24, ge=1, le=168, description="Cache TTL in hours")
    UPDATE_AUTO_REFRESH_ENABLED: bool = Field(default=True, description="Enable auto refresh")
    UPDATE_MAX_INGREDIENTS: int = Field(
        default=10000, ge=100, le=50000, description="Max ingredients to cache"
    )
    UPDATE_INGREDIENT_CACHE_INTERVAL_DAYS: int = Field(
        default=7, ge=1, le=30, description="Ingredient cache update interval in days"
    )
    UPDATE_CACHE_FILE_PERMISSIONS: int = Field(default=0o755, description="Cache file permissions")

    # Database update settings
    UPDATE_DATABASE_SYNC_ENABLED: bool = Field(default=True, description="Enable database sync")
    UPDATE_MAX_BATCH_SIZE: int = Field(
        default=1000, ge=100, le=5000, description="Max batch size for updates"
    )
    UPDATE_RETRY_ATTEMPTS: int = Field(
        default=3, ge=1, le=10, description="Number of retry attempts"
    )
    UPDATE_RETRY_DELAY_SECONDS: int = Field(
        default=5, ge=1, le=60, description="Retry delay in seconds"
    )


class HealthConfig(BaseSettings):
    """Health monitoring configuration."""

    HEALTH_MONITORING_ENABLED: bool = Field(default=True, description="Enable health monitoring")
    HEALTH_DATABASE_QUERY_TIMEOUT: int = Field(
        default=5000, ge=1000, le=30000, description="DB query timeout (ms)"
    )
    HEALTH_RESPONSE_TIME_WARNING: int = Field(
        default=1000, ge=100, le=5000, description="Response time warning (ms)"
    )
    HEALTH_RESPONSE_TIME_CRITICAL: int = Field(
        default=5000, ge=1000, le=30000, description="Response time critical (ms)"
    )
    HEALTH_MEMORY_USAGE_WARNING: float = Field(
        default=80.0, ge=50.0, le=95.0, description="Memory warning (%)"
    )
    HEALTH_MEMORY_USAGE_CRITICAL: float = Field(
        default=95.0, ge=80.0, le=99.0, description="Memory critical (%)"
    )
    HEALTH_CPU_USAGE_WARNING: float = Field(
        default=80.0, ge=50.0, le=95.0, description="CPU warning (%)"
    )
    HEALTH_CPU_USAGE_CRITICAL: float = Field(
        default=95.0, ge=80.0, le=99.0, description="CPU critical (%)"
    )
    HEALTH_DISK_USAGE_WARNING: float = Field(
        default=80.0, ge=50.0, le=95.0, description="Disk usage warning (%)"
    )
    HEALTH_DISK_USAGE_CRITICAL: float = Field(
        default=95.0, ge=80.0, le=99.0, description="Disk usage critical (%)"
    )
    HEALTH_DETAILED_CHECK_CACHE_TTL: int = Field(
        default=30, ge=10, le=300, description="Detailed check cache TTL"
    )
    HEALTH_QUICK_CHECK_CACHE_TTL: int = Field(
        default=10, ge=5, le=60, description="Quick check cache TTL"
    )

    # Health service names for monitoring
    HEALTH_SERVICE_NAMES: List[str] = Field(
        default=[
            "auth",
            "ingredients",
            "receipt",
            "database",
            "system",
            "cache",
            "update",
        ],
        description="List of service names to monitor for health checks",
    )

    # Health metrics settings
    HEALTH_METRICS_MAX_RETENTION: int = Field(
        default=1000, ge=100, le=10000, description="Max health metrics to retain"
    )
    HEALTH_METRICS_CLEANUP_INTERVAL: int = Field(
        default=300, ge=60, le=3600, description="Metrics cleanup interval in seconds"
    )
    HEALTH_ALERT_RETENTION_HOURS: int = Field(
        default=24, ge=1, le=168, description="Health alert retention in hours"
    )
    HEALTH_ALERTS_DEFAULT_HOURS: int = Field(
        default=24, ge=1, le=168, description="Default hours for health alerts query"
    )
    HEALTH_METRICS_DECIMAL_PLACES: int = Field(
        default=2, ge=0, le=6, description="Decimal places for health metrics rounding"
    )


class EndpointConfig(BaseSettings):
    """API endpoint paths and descriptions."""

    # Health Endpoints
    HEALTH_PREFIX: str = Field(default="/health", pattern=r"^/[\w-]+$", description="Health prefix")
    HEALTH_TAG: str = Field(default="Health", description="Health tag")
    HEALTH_ROOT_ENDPOINT: str = Field(default="/", description="Root endpoint")
    HEALTH_QUICK_ENDPOINT: str = Field(default="/quick", description="Quick endpoint")
    HEALTH_LIVENESS_ENDPOINT: str = Field(default="/liveness", description="Liveness endpoint")
    HEALTH_READINESS_ENDPOINT: str = Field(default="/readiness", description="Readiness endpoint")
    HEALTH_METRICS_ENDPOINT: str = Field(default="/metrics", description="Health metrics endpoint")
    HEALTH_DETAILED_ENDPOINT: str = Field(
        default="/detailed", description="Detailed health endpoint"
    )
    HEALTH_ALERTS_ENDPOINT: str = Field(default="/alerts", description="Health alerts endpoint")
    HEALTH_SERVICE_HISTORY_ENDPOINT: str = Field(
        default="/service-history", description="Service history endpoint"
    )

    # Health API Documentation
    HEALTH_ROOT_TITLE: str = Field(default="Health Check", description="Root health endpoint title")
    HEALTH_ROOT_DESCRIPTION: str = Field(
        default="Comprehensive health check with detailed service status",
        description="Root health endpoint description",
    )
    HEALTH_QUICK_TITLE: str = Field(
        default="Quick Health Check", description="Quick health endpoint title"
    )
    HEALTH_QUICK_DESCRIPTION: str = Field(
        default="Fast health check for load balancers",
        description="Quick health endpoint description",
    )
    HEALTH_LIVENESS_TITLE: str = Field(
        default="Liveness Probe", description="Liveness endpoint title"
    )
    HEALTH_LIVENESS_DESCRIPTION: str = Field(
        default="Check if the application is alive",
        description="Liveness endpoint description",
    )
    HEALTH_READINESS_TITLE: str = Field(
        default="Readiness Probe", description="Readiness endpoint title"
    )
    HEALTH_READINESS_DESCRIPTION: str = Field(
        default="Check if the application is ready to serve requests",
        description="Readiness endpoint description",
    )
    HEALTH_METRICS_TITLE: str = Field(
        default="Health Metrics", description="Health metrics endpoint title"
    )
    HEALTH_METRICS_DESCRIPTION: str = Field(
        default="Get detailed health metrics and statistics",
        description="Health metrics endpoint description",
    )
    HEALTH_DETAILED_TITLE: str = Field(
        default="Detailed Health Status", description="Detailed health endpoint title"
    )
    HEALTH_DETAILED_DESCRIPTION: str = Field(
        default="Comprehensive health status with all service details",
        description="Detailed health endpoint description",
    )
    HEALTH_ALERTS_TITLE: str = Field(
        default="Health Alerts", description="Health alerts endpoint title"
    )
    HEALTH_ALERTS_DESCRIPTION: str = Field(
        default="Get current health alerts and warnings",
        description="Health alerts endpoint description",
    )
    HEALTH_SERVICE_HISTORY_TITLE: str = Field(
        default="Service Health History", description="Service history endpoint title"
    )
    HEALTH_SERVICE_HISTORY_DESCRIPTION: str = Field(
        default="Get historical health data for services",
        description="Service history endpoint description",
    )

    # Auth Endpoints
    AUTH_PREFIX: str = Field(default="/auth", pattern=r"^/[\w-]+$", description="Auth prefix")
    AUTH_TAG: str = Field(default="Authentication", description="Auth tag")
    AUTH_REGISTER_ENDPOINT: str = Field(default="/register", description="Register endpoint")
    AUTH_LOGIN_ENDPOINT: str = Field(default="/login", description="Login endpoint")
    AUTH_LOGOUT_ENDPOINT: str = Field(default="/logout", description="Logout endpoint")
    AUTH_REFRESH_ENDPOINT: str = Field(default="/refresh", description="Refresh endpoint")

    # Ingredients Endpoints
    INGREDIENTS_PREFIX: str = Field(
        default="/ingredients", pattern=r"^/[\w-]+$", description="Ingredients prefix"
    )
    INGREDIENTS_TAG: str = Field(default="Ingredients", description="Ingredients tag")
    INGREDIENTS_MASTER_ENDPOINT: str = Field(default="/master", description="Master endpoint")
    INGREDIENTS_SEARCH_ENDPOINT: str = Field(default="/search", description="Search endpoint")
    INGREDIENTS_PANTRY_ENDPOINT: str = Field(default="/pantry", description="Pantry endpoint")

    # Ingredients API Documentation
    INGREDIENTS_MASTER_LIST_TITLE: str = Field(
        default="List All Ingredients", description="Master list endpoint title"
    )
    INGREDIENTS_MASTER_LIST_DESCRIPTION: str = Field(
        default="Retrieve a paginated list of all ingredients from the master database",
        description="Master list endpoint description",
    )

    # Ingredients Pagination Settings
    INGREDIENTS_DEFAULT_LIMIT: int = Field(
        default=20, ge=1, le=10000, description="Default limit for ingredient queries"
    )
    INGREDIENTS_MAX_LIMIT: int = Field(
        default=1000, ge=1, le=10000, description="Maximum limit for ingredient queries"
    )
    INGREDIENTS_SEARCH_DEFAULT_LIMIT: int = Field(
        default=50, ge=1, le=10000, description="Default limit for ingredient search"
    )
    INGREDIENTS_SEARCH_MAX_LIMIT: int = Field(
        default=1000, ge=1, le=10000, description="Maximum limit for ingredient search"
    )

    # OCR Endpoints
    OCR_PREFIX: str = Field(default="/ocr", pattern=r"^/[\w-]+$", description="OCR prefix")
    OCR_TAG: str = Field(default="OCR", description="OCR tag")
    OCR_EXTRACT_TEXT_ENDPOINT: str = Field(
        default="/extract-text", description="Extract text endpoint"
    )
    OCR_PROCESS_RECEIPT_ENDPOINT: str = Field(
        default="/process-receipt", description="Process receipt endpoint"
    )


# =============================================================================
# MAIN SETTINGS CLASS
# =============================================================================


class Settings(
    AppConfig,
    ServerConfig,
    SecurityConfig,
    CORSConfig,
    RateLimitConfig,
    DatabaseConfig,
    CacheConfig,
    LoggingConfig,
    MonitoringConfig,
    PasswordConfig,
    OCRConfig,
    ValidationConfig,
    HealthConfig,
    EndpointConfig,
    UpdateConfig,
):
    """
    Main application configuration combining all config sections.

    This class inherits from all configuration classes to provide a unified
    interface while maintaining logical separation of concerns with validation.

    Configuration loading order:
    1. Environment variables
    2. .env file values (for secrets)
    3. Default values defined in the config classes
    """

    # =========================================================================
    # VALIDATORS
    # =========================================================================

    @model_validator(mode="before")
    @classmethod
    def validate_environment_consistency(cls, values):
        """Validate that configuration is consistent with environment."""
        if isinstance(values, dict):
            environment = values.get("ENVIRONMENT", Environment.DEVELOPMENT)
            debug = values.get("DEBUG", True)

            # Production environment should have debug disabled
            if environment == Environment.PRODUCTION and debug:
                values["DEBUG"] = False

            # Security validations for production
            if environment == Environment.PRODUCTION:
                if not values.get("SECURITY_HEADERS_ENABLED", True):
                    raise ValueError("Security headers must be enabled in production")
                if values.get("SESSION_HTTPS_ONLY", True) is False:
                    raise ValueError("HTTPS-only sessions required in production")

        return values

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v):
        """Validate CORS origins format."""
        for origin in v:
            if not origin.startswith(("http://", "https://")):
                raise ValueError(f"Invalid CORS origin format: {origin}")
        return v

    # =========================================================================
    # COMPUTED PROPERTIES
    # =========================================================================

    @property
    def supabase_url(self) -> str:
        """Get the Supabase URL."""
        return self.SUPABASE_URL

    @property
    def supabase_anon_key(self) -> str:
        """Get the Supabase anonymous key."""
        return self.SUPABASE_KEY

    @property
    def is_production(self) -> bool:
        """Check if the application is running in production mode."""
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Check if the application is running in development mode."""
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        """Check if the application is running in testing mode."""
        return self.ENVIRONMENT == Environment.TESTING

    @property
    def rate_limiting_enabled_safe(self) -> bool:
        """Get rate limiting setting with debug mode awareness."""
        if self.DEBUG or self.is_development:
            return False  # Disable rate limiting in debug/dev mode
        return self.RATE_LIMITING_ENABLED

    @property
    def cors_origins_safe(self) -> List[str]:
        """Get CORS origins with development defaults if in dev mode."""
        if self.is_development and not self.CORS_ORIGINS:
            return [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
            ]
        return self.CORS_ORIGINS

    @property
    def session_https_only_safe(self) -> bool:
        """Get session HTTPS setting with environment awareness."""
        if self.is_development:
            return False  # Allow HTTP in development
        return self.SESSION_HTTPS_ONLY

    @property
    def docs_enabled(self) -> bool:
        """Check if API documentation should be enabled."""
        return self.is_development or self.DEBUG

    @property
    def monitoring_enabled_safe(self) -> bool:
        """Get monitoring setting with environment awareness."""
        return self.MONITORING_ENABLED and (self.is_production or self.DEBUG)

    @property
    def log_level_safe(self) -> LogLevel:
        """Get log level with environment awareness."""
        if self.is_development:
            return LogLevel.DEBUG
        return self.LOG_LEVEL

    @property
    def security_headers_enabled_safe(self) -> bool:
        """Get security headers setting with environment awareness."""
        return self.SECURITY_HEADERS_ENABLED or self.is_production

    # =========================================================================
    # PYDANTIC CONFIGURATION
    # =========================================================================

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "env_nested_delimiter": "__",
        "case_sensitive": True,
        "validate_default": True,
        "env_prefix": "",  # Don't use prefixes for environment variables
        "validate_assignment": True,  # Validate on assignment
        "use_enum_values": True,  # Use enum values in validation
    }

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def get_config_summary(self) -> dict:
        """Get a summary of current configuration."""
        return {
            "environment": self.ENVIRONMENT,
            "debug": self.DEBUG,
            "version": self.VERSION,
            "rate_limiting": self.rate_limiting_enabled_safe,
            "security_headers": self.security_headers_enabled_safe,
            "docs_enabled": self.docs_enabled,
            "monitoring": self.monitoring_enabled_safe,
        }

    def validate_config(self) -> List[str]:
        """Validate configuration and return list of warnings/errors."""
        warnings = []

        # Check for missing sensitive values in production
        if self.is_production:
            if not self.SUPABASE_URL:
                warnings.append("SUPABASE_URL is not set in production")
            if not self.SUPABASE_KEY:
                warnings.append("SUPABASE_KEY is not set in production")
            if len(self.JWT_SECRET_KEY) < 32:
                warnings.append("JWT_SECRET_KEY should be at least 32 characters")

        # Check CORS configuration
        if self.is_production and not self.CORS_ORIGINS:
            warnings.append("CORS_ORIGINS should be configured in production")

        return warnings

    def show_environment_overrides(self) -> dict:
        """
        Shows which settings have been overridden by environment variables.
        This method is useful for debugging purposes.

        Note: Sensitive values are displayed as 'MASKED' for security reasons.

        Returns:
            dict: A dictionary with the names of overridden settings and their masked values
        """
        env_vars: dict[str, str] = {}
        sensitive_keys = {
            "SUPABASE_KEY",
            "JWT_SECRET_KEY",
            "SESSION_SECRET_KEY",
            "SUPABASE_URL",
        }

        # Check all settings of the class
        for key in dir(self):
            # Only consider uppercase constants
            if not key.isupper() or not hasattr(self.__class__, key):
                continue

            # Check if the environment variable is set
            env_value = os.environ.get(key)
            if env_value is not None:
                # Mask sensitive values
                if key in sensitive_keys:
                    env_vars[key] = "MASKED"
                else:
                    env_vars[key] = env_value

        return env_vars

    def print_config(self, mask_secrets: bool = True, show_warnings: bool = True) -> None:
        """
        Prints the current configuration, useful for debugging purposes.

        Args:
            mask_secrets: If True, sensitive values will be masked
            show_warnings: If True, show configuration warnings
        """
        # Collect all attributes of the class
        config_dict = {}
        sensitive_keys = {
            "SUPABASE_KEY",
            "JWT_SECRET_KEY",
            "SESSION_SECRET_KEY",
            "SUPABASE_URL",
        }

        for key in dir(self):
            # Only consider uppercase constants
            if not key.isupper() or not hasattr(self.__class__, key):
                continue

            value = getattr(self, key)

            # Mask sensitive values
            if mask_secrets and key in sensitive_keys:
                config_dict[key] = "*** MASKED ***"
            else:
                # Try to convert complex objects to serializable formats
                try:
                    json.dumps({key: value})  # Test if serializable
                    config_dict[key] = value
                except (TypeError, OverflowError):
                    config_dict[key] = str(value)

        print("\n===== Current Configuration =====")
        pprint(self.get_config_summary())
        print("\n=== Environment Overrides ===")
        pprint(self.show_environment_overrides())

        if show_warnings:
            warnings = self.validate_config()
            if warnings:
                print("\n=== Configuration Warnings ===")
                for warning in warnings:
                    print(f"⚠️  {warning}")
            else:
                print("\n✅ No configuration warnings")

        print("===============================\n")


# =============================================================================
# GLOBAL SETTINGS INSTANCE
# =============================================================================

# Global settings instance with validation
settings = Settings()
