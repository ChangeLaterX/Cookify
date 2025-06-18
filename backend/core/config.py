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
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, model_validator, HttpUrl
from typing import Optional, List, Set, Tuple, Literal, Union
from enum import Enum
import secrets
import os
import json
from pprint import pprint


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
    ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT, description="Runtime environment")
    VERSION: str = Field(default="0.1.0", pattern=r"^\d+\.\d+\.\d+$", description="Application version")
    
    # API Documentation
    DOCS_URL: Optional[str] = Field(default="/docs", description="Swagger docs URL")
    REDOC_URL: Optional[str] = Field(default="/redoc", description="ReDoc URL")
    API_V1_PREFIX: str = Field(default="/api", description="API prefix")
    API_TITLE: str = Field(default="Cookify API", description="API title")
    API_DESCRIPTION: str = Field(default="REST API for meal planning and recipe management", description="API description")
    API_VERSION: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$", description="API version")
    API_CONTACT_NAME: str = Field(default="Cookify Support", description="Contact name")
    API_CONTACT_EMAIL: str = Field(default="support@cookify.app", description="Contact email")
    API_LICENSE_NAME: str = Field(default="MIT", description="License name")
    API_TERMS_OF_SERVICE: Optional[HttpUrl] = Field(default=None, description="Terms of service URL")

    @field_validator('API_CONTACT_EMAIL')
    @classmethod
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v


class ServerConfig(BaseSettings):
    """Server and networking configuration."""
    
    # Server Settings
    SERVER_HOST: str = Field(default="0.0.0.0", description="Server host")
    SERVER_PORT: int = Field(default=8000, ge=1024, le=65535, description="Server port")
    SERVER_WORKERS: int = Field(default=1, ge=1, le=16, description="Number of workers")
    SERVER_RELOAD: bool = Field(default=True, description="Enable auto-reload")
    
    # Request/Response Settings
    API_MAX_REQUEST_SIZE_MB: int = Field(default=10, ge=1, le=100, description="Max request size in MB")
    API_DEFAULT_PAGE_SIZE: int = Field(default=20, ge=1, le=100, description="Default page size")
    API_MAX_PAGE_SIZE: int = Field(default=100, ge=1, le=1000, description="Max page size")
    API_REQUEST_TIMEOUT_SECONDS: int = Field(default=30, ge=1, le=300, description="Request timeout")
    API_RESPONSE_CACHE_TTL: int = Field(default=300, ge=0, description="Response cache TTL")


class SecurityConfig(BaseSettings):
    """Security and authentication configuration."""
    
    # Sensitive values loaded from environment
    SUPABASE_URL: str = Field(default_factory=lambda: os.getenv("SUPABASE_URL", ""), description="Supabase URL")
    SUPABASE_KEY: str = Field(default_factory=lambda: os.getenv("SUPABASE_KEY", ""), description="Supabase key")
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET", "") or secrets.token_urlsafe(32),
        min_length=32,
        description="JWT secret key"
    )
    JWT_ALGORITHM: JWTAlgorithm = Field(
        default_factory=lambda: JWTAlgorithm(os.getenv("JWT_ALGORITHM", "HS256")),
        description="JWT algorithm"
    )
    JWT_EXPIRE_MINUTES: int = Field(
        default_factory=lambda: int(os.getenv("JWT_EXPIRATION", "30")),
        ge=1,
        le=1440,
        description="JWT expiration in minutes"
    )
    SESSION_SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("SESSION_SECRET_KEY", "") or secrets.token_urlsafe(32),
        min_length=32,
        description="Session secret key"
    )
    
    # Authentication Settings
    REQUIRE_EMAIL_VERIFICATION: bool = Field(default=False, description="Require email verification")
    PASSWORD_MIN_LENGTH: int = Field(default=8, ge=6, le=128, description="Minimum password length")
    MAX_LOGIN_ATTEMPTS: int = Field(default=5, ge=1, le=10, description="Max login attempts")
    LOCKOUT_DURATION_MINUTES: int = Field(default=15, ge=1, le=1440, description="Lockout duration")
    FRONTEND_URL: HttpUrl = Field(default="http://localhost:3000", description="Frontend URL")
    
    # Security Headers
    SECURITY_HEADERS_ENABLED: bool = Field(default=True, description="Enable security headers")
    HSTS_MAX_AGE: int = Field(default=31536000, ge=0, description="HSTS max age")
    HSTS_INCLUDE_SUBDOMAINS: bool = Field(default=True, description="HSTS include subdomains")
    HSTS_PRELOAD: bool = Field(default=False, description="HSTS preload")
    CSP_REPORT_URI: Optional[HttpUrl] = Field(default=None, description="CSP report URI")
    CUSTOM_SECURITY_HEADERS: Optional[dict] = Field(default=None, description="Custom security headers")

    @field_validator('SUPABASE_URL')
    @classmethod
    def validate_supabase_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('SUPABASE_URL must be a valid URL')
        return v


class CORSConfig(BaseSettings):
    """CORS and middleware configuration."""
    
    CORS_ORIGINS: List[str] = Field(default=[], description="CORS origins")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow credentials")
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        description="Allowed methods"
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=["Authorization", "Content-Type", "X-Request-ID"],
        description="Allowed headers"
    )
    
    # Middleware Settings
    TRUSTED_HOSTS: List[str] = Field(default=["localhost", "127.0.0.1"], description="Trusted hosts")
    ENABLE_TRUSTED_HOST_MIDDLEWARE: bool = Field(default=True, description="Enable trusted host middleware")
    SESSION_HTTPS_ONLY: bool = Field(default=True, description="HTTPS only sessions")
    SESSION_SAME_SITE: Literal["strict", "lax", "none"] = Field(default="strict", description="SameSite cookie setting")


class RateLimitConfig(BaseSettings):
    """Rate limiting configuration."""
    
    RATE_LIMITING_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_LOGIN_ATTEMPTS: int = Field(default=5, ge=1, le=20, description="Login rate limit")
    RATE_LIMIT_LOGIN_WINDOW_MINUTES: int = Field(default=15, ge=1, le=60, description="Login window")
    RATE_LIMIT_REGISTRATION_ATTEMPTS: int = Field(default=3, ge=1, le=10, description="Registration rate limit")
    RATE_LIMIT_REGISTRATION_WINDOW_MINUTES: int = Field(default=5, ge=1, le=30, description="Registration window")
    RATE_LIMIT_PASSWORD_RESET_ATTEMPTS: int = Field(default=3, ge=1, le=10, description="Password reset rate limit")
    RATE_LIMIT_PASSWORD_RESET_WINDOW_MINUTES: int = Field(default=60, ge=1, le=240, description="Password reset window")
    RATE_LIMIT_PROGRESSIVE_MULTIPLIER: float = Field(default=2.0, ge=1.0, le=5.0, description="Progressive multiplier")
    RATE_LIMIT_MAX_PROGRESSIVE_DELAY: int = Field(default=300, ge=60, le=3600, description="Max progressive delay")
    RATE_LIMIT_CLEANUP_INTERVAL: int = Field(default=600, ge=60, le=3600, description="Cleanup interval")


class DatabaseConfig(BaseSettings):
    """Database configuration and connection settings."""
    
    # Connection Settings
    DB_CONNECTION_POOL_SIZE: int = Field(default=10, ge=1, le=50, description="Connection pool size")
    DB_CONNECTION_POOL_MAX_OVERFLOW: int = Field(default=20, ge=0, le=100, description="Max pool overflow")
    DB_QUERY_TIMEOUT_SECONDS: int = Field(default=30, ge=1, le=300, description="Query timeout")
    DB_CONNECTION_TIMEOUT_SECONDS: int = Field(default=10, ge=1, le=60, description="Connection timeout")
    DB_TRANSACTION_TIMEOUT_SECONDS: int = Field(default=60, ge=1, le=600, description="Transaction timeout")
    DB_RETRY_ATTEMPTS: int = Field(default=3, ge=0, le=10, description="Retry attempts")
    DB_RETRY_DELAY_SECONDS: float = Field(default=1.0, ge=0.1, le=10.0, description="Retry delay")
    DB_ENABLE_QUERY_LOGGING: bool = Field(default=False, description="Enable query logging")
    DB_SLOW_QUERY_THRESHOLD_MS: int = Field(default=1000, ge=100, le=10000, description="Slow query threshold")
    
    # Field Length Settings
    DB_EMAIL_MAX_LENGTH: int = Field(default=255, ge=50, le=500, description="Email field length")
    DB_PASSWORD_MAX_LENGTH: int = Field(default=255, ge=50, le=500, description="Password field length")
    DB_TOKEN_MAX_LENGTH: int = Field(default=255, ge=50, le=500, description="Token field length")
    DB_STRING_DEFAULT_LENGTH: int = Field(default=255, ge=50, le=500, description="Default string length")
    DB_DISPLAY_NAME_MAX_LENGTH: int = Field(default=100, ge=10, le=200, description="Display name length")


class CacheConfig(BaseSettings):
    """Caching configuration."""
    
    USER_CACHE_TTL_SECONDS: int = Field(default=300, ge=60, le=3600, description="User cache TTL")
    ENABLE_USER_CACHE: bool = Field(default=True, description="Enable user cache")
    CACHE_DEFAULT_TTL_SECONDS: int = Field(default=1800, ge=60, le=7200, description="Default cache TTL")
    CACHE_MAX_SIZE: int = Field(default=1000, ge=100, le=10000, description="Max cache size")
    CACHE_ENABLE_COMPRESSION: bool = Field(default=True, description="Enable compression")
    CACHE_CLEANUP_INTERVAL_SECONDS: int = Field(default=3600, ge=300, le=7200, description="Cleanup interval")


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    
    LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    LOG_FORMAT_JSON: bool = Field(default=False, description="JSON log format")
    CONSOLE_LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, description="Console log level")
    LOG_TO_FILE: bool = Field(default=False, description="Log to file")
    LOG_DIR: str = Field(default="backend/logs", description="Log directory")
    ENABLE_ACCESS_LOG: bool = Field(default=True, description="Enable access log")


class MonitoringConfig(BaseSettings):
    """Monitoring and metrics configuration."""
    
    MONITORING_ENABLED: bool = Field(default=True, description="Enable monitoring")
    METRICS_COLLECTION_ENABLED: bool = Field(default=True, description="Enable metrics collection")
    PERFORMANCE_MONITORING_ENABLED: bool = Field(default=True, description="Enable performance monitoring")
    ERROR_TRACKING_ENABLED: bool = Field(default=True, description="Enable error tracking")
    TRACE_SAMPLING_RATE: float = Field(default=0.1, ge=0.0, le=1.0, description="Trace sampling rate")
    METRICS_EXPORT_INTERVAL_SECONDS: int = Field(default=60, ge=10, le=300, description="Metrics export interval")
    MONITORING_ENDPOINT_PREFIX: str = Field(default="/metrics", description="Monitoring endpoint prefix")
    MONITORING_REQUIRE_AUTH: bool = Field(default=False, description="Require auth for monitoring")


class PasswordConfig(BaseSettings):
    """Password validation and security configuration."""
    
    PASSWORD_MIN_SECURITY_LENGTH: int = Field(default=6, ge=4, le=32, description="Min security length")
    PASSWORD_MAX_LENGTH: int = Field(default=128, ge=32, le=256, description="Max password length")
    PASSWORD_MIN_UNIQUE_CHARS: int = Field(default=6, ge=3, le=20, description="Min unique chars")
    PASSWORD_MAX_REPEATED_CHAR_RATIO: float = Field(default=0.4, ge=0.1, le=0.8, description="Max repeated char ratio")
    PASSWORD_MIN_CHAR_TYPES: int = Field(default=3, ge=1, le=4, description="Min character types")
    PASSWORD_MIN_ENTROPY_SCORE: int = Field(default=35, ge=10, le=100, description="Min entropy score")
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(default=True, description="Require uppercase")
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(default=True, description="Require lowercase")
    PASSWORD_REQUIRE_DIGITS: bool = Field(default=True, description="Require digits")
    PASSWORD_REQUIRE_SPECIAL: bool = Field(default=True, description="Require special chars")
    
    # Password Complexity
    PASSWORD_SPECIAL_CHARS: str = Field(
        default="!@#$%^&*()_+-=[]{}|;:,.<>?",
        min_length=10,
        description="Special characters"
    )
    PASSWORD_FORBIDDEN_PATTERNS: List[str] = Field(
        default=[
            r'(.)\1{3,}',  # 4+ repeated characters
            r'(0123|1234|2345|3456|4567|5678|6789)',  # Sequential numbers
            r'^(password|admin|user|guest)$',  # Common passwords
        ],
        description="Forbidden patterns"
    )


class OCRConfig(BaseSettings):
    """OCR processing configuration."""
    
    OCR_MAX_IMAGE_SIZE_BYTES: int = Field(default=5242880, ge=1048576, le=52428800, description="Max image size (5MB)")
    OCR_ALLOWED_IMAGE_FORMATS: List[str] = Field(
        default=["JPEG", "JPG", "PNG", "WEBP", "BMP", "TIFF"],
        description="Allowed image formats"
    )
    OCR_MIN_IMAGE_WIDTH: int = Field(default=100, ge=50, le=1000, description="Min image width")
    OCR_MIN_IMAGE_HEIGHT: int = Field(default=100, ge=50, le=1000, description="Min image height")
    OCR_MAX_IMAGE_WIDTH: int = Field(default=4000, ge=1000, le=8000, description="Max image width")
    OCR_MAX_IMAGE_HEIGHT: int = Field(default=4000, ge=1000, le=8000, description="Max image height")
    OCR_DEFAULT_DPI: int = Field(default=300, ge=72, le=600, description="Default DPI")
    OCR_PREPROCESSING_ENABLED: bool = Field(default=True, description="Enable preprocessing")
    OCR_CONFIDENCE_THRESHOLD: float = Field(default=0.6, ge=0.0, le=1.0, description="Confidence threshold")
    OCR_PROCESSING_TIMEOUT: int = Field(default=30, ge=5, le=120, description="Processing timeout")
    OCR_DEFAULT_LANGUAGE: OCRLanguage = Field(default=OCRLanguage.GERMAN, description="Default language")
    OCR_SUPPORTED_LANGUAGES: List[OCRLanguage] = Field(
        default=[OCRLanguage.GERMAN, OCRLanguage.ENGLISH],
        description="Supported languages"
    )


class HealthConfig(BaseSettings):
    """Health monitoring configuration."""
    
    HEALTH_MONITORING_ENABLED: bool = Field(default=True, description="Enable health monitoring")
    HEALTH_DATABASE_QUERY_TIMEOUT: int = Field(default=5000, ge=1000, le=30000, description="DB query timeout (ms)")
    HEALTH_RESPONSE_TIME_WARNING: int = Field(default=1000, ge=100, le=5000, description="Response time warning (ms)")
    HEALTH_RESPONSE_TIME_CRITICAL: int = Field(default=5000, ge=1000, le=30000, description="Response time critical (ms)")
    HEALTH_MEMORY_USAGE_WARNING: float = Field(default=80.0, ge=50.0, le=95.0, description="Memory warning (%)")
    HEALTH_MEMORY_USAGE_CRITICAL: float = Field(default=95.0, ge=80.0, le=99.0, description="Memory critical (%)")
    HEALTH_CPU_USAGE_WARNING: float = Field(default=80.0, ge=50.0, le=95.0, description="CPU warning (%)")
    HEALTH_CPU_USAGE_CRITICAL: float = Field(default=95.0, ge=80.0, le=99.0, description="CPU critical (%)")
    HEALTH_DETAILED_CHECK_CACHE_TTL: int = Field(default=30, ge=10, le=300, description="Detailed check cache TTL")
    HEALTH_QUICK_CHECK_CACHE_TTL: int = Field(default=10, ge=5, le=60, description="Quick check cache TTL")


class EndpointConfig(BaseSettings):
    """API endpoint paths and descriptions."""
    
    # Health Endpoints
    HEALTH_PREFIX: str = Field(default="/health", pattern=r"^/[\w-]+$", description="Health prefix")
    HEALTH_TAG: str = Field(default="Health", description="Health tag")
    HEALTH_ROOT_ENDPOINT: str = Field(default="/", description="Root endpoint")
    HEALTH_QUICK_ENDPOINT: str = Field(default="/quick", description="Quick endpoint")
    HEALTH_LIVENESS_ENDPOINT: str = Field(default="/liveness", description="Liveness endpoint")
    HEALTH_READINESS_ENDPOINT: str = Field(default="/readiness", description="Readiness endpoint")
    
    # Auth Endpoints
    AUTH_PREFIX: str = Field(default="/auth", pattern=r"^/[\w-]+$", description="Auth prefix")
    AUTH_TAG: str = Field(default="Authentication", description="Auth tag")
    AUTH_REGISTER_ENDPOINT: str = Field(default="/register", description="Register endpoint")
    AUTH_LOGIN_ENDPOINT: str = Field(default="/login", description="Login endpoint")
    AUTH_LOGOUT_ENDPOINT: str = Field(default="/logout", description="Logout endpoint")
    AUTH_REFRESH_ENDPOINT: str = Field(default="/refresh", description="Refresh endpoint")
    
    # Ingredients Endpoints
    INGREDIENTS_PREFIX: str = Field(default="/ingredients", pattern=r"^/[\w-]+$", description="Ingredients prefix")
    INGREDIENTS_TAG: str = Field(default="Ingredients", description="Ingredients tag")
    INGREDIENTS_MASTER_ENDPOINT: str = Field(default="/master", description="Master endpoint")
    INGREDIENTS_SEARCH_ENDPOINT: str = Field(default="/search", description="Search endpoint")
    INGREDIENTS_PANTRY_ENDPOINT: str = Field(default="/pantry", description="Pantry endpoint")
    
    # OCR Endpoints
    OCR_PREFIX: str = Field(default="/ocr", pattern=r"^/[\w-]+$", description="OCR prefix")
    OCR_TAG: str = Field(default="OCR", description="OCR tag")
    OCR_EXTRACT_TEXT_ENDPOINT: str = Field(default="/extract-text", description="Extract text endpoint")
    OCR_PROCESS_RECEIPT_ENDPOINT: str = Field(default="/process-receipt", description="Process receipt endpoint")


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
    HealthConfig,
    EndpointConfig
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
    
    @model_validator(mode='before')
    @classmethod
    def validate_environment_consistency(cls, values):
        """Validate that configuration is consistent with environment."""
        if isinstance(values, dict):
            environment = values.get('ENVIRONMENT', Environment.DEVELOPMENT)
            debug = values.get('DEBUG', True)
            
            # Production environment should have debug disabled
            if environment == Environment.PRODUCTION and debug:
                values['DEBUG'] = False
                
            # Security validations for production
            if environment == Environment.PRODUCTION:
                if not values.get('SECURITY_HEADERS_ENABLED', True):
                    raise ValueError('Security headers must be enabled in production')
                if values.get('SESSION_HTTPS_ONLY', True) is False:
                    raise ValueError('HTTPS-only sessions required in production')
                    
        return values
    
    @field_validator('CORS_ORIGINS')
    @classmethod
    def validate_cors_origins(cls, v):
        """Validate CORS origins format."""
        for origin in v:
            if not origin.startswith(('http://', 'https://')):
                raise ValueError(f'Invalid CORS origin format: {origin}')
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
        sensitive_keys = {'SUPABASE_KEY', 'JWT_SECRET_KEY', 'SESSION_SECRET_KEY', 'SUPABASE_URL'}

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
                    env_vars[key] = 'MASKED'
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
        sensitive_keys = {'SUPABASE_KEY', 'JWT_SECRET_KEY', 'SESSION_SECRET_KEY', 'SUPABASE_URL'}

        for key in dir(self):
            # Only consider uppercase constants
            if not key.isupper() or not hasattr(self.__class__, key):
                continue

            value = getattr(self, key)

            # Mask sensitive values
            if mask_secrets and key in sensitive_keys:
                config_dict[key] = '*** MASKED ***'
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
