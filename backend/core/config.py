"""
Enhanced configuration management for the FastAPI application.
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
import secrets


class Settings(BaseSettings):
    # Application Settings
    app_name: str = "APP API"
    debug: bool = True  # Enabled for development testing
    docs_url: Optional[str] = "/docs"
    redoc_url: Optional[str] = "/redoc"
    version: str = "0.1.0"
    
    # Environment detection
    environment: str = "production"  # Default to production
    
    # Supabase Configuration
    vite_supabase_url: str = ""
    vite_supabase_anon_key: str = ""
    
    # Security Settings
    jwt_secret_key: str = secrets.token_urlsafe(32)
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    session_secret_key: str = secrets.token_urlsafe(32)
    
    # Authentication Settings
    require_email_verification: bool = False  # Disabled for development testing
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    frontend_url: str = "http://localhost:3000"  # Default frontend URL
    
    # Rate Limiting Settings
    rate_limiting_enabled: bool = True
    rate_limit_login_attempts: int = 5  # Login attempts per window
    rate_limit_login_window_minutes: int = 15  # Window for login attempts
    rate_limit_registration_attempts: int = 3  # Registration attempts per window
    rate_limit_registration_window_minutes: int = 5  # Window for registration attempts
    rate_limit_password_reset_attempts: int = 3  # Password reset attempts per window
    rate_limit_password_reset_window_minutes: int = 60  # Window for password reset attempts
    
    # Cache Settings
    user_cache_ttl_seconds: int = 300  # 5 minutes
    enable_user_cache: bool = True
    
    # CORS Configuration - restrictive by default
    cors_origins: List[str] = []  # Empty by default, must be explicitly configured
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    cors_allow_headers: List[str] = ["Authorization", "Content-Type", "X-Request-ID"]
    
    # Middleware Settings
    trusted_hosts: List[str] = ["localhost", "127.0.0.1"]
    enable_trusted_host_middleware: bool = True  # Enable by default for security
    session_https_only: bool = True  # Enable HTTPS by default
    session_same_site: str = "strict"  # More secure default
    
    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_access_log: bool = True
    
    # Security Headers Settings
    # Enable or disable security headers middleware.
    # When enabled, the application will enforce security headers such as HSTS, CSP, etc.,
    # to enhance security in production environments.
    security_headers_enabled: bool = True
    hsts_max_age: int = 31536000  # 1 year in seconds
    hsts_include_subdomains: bool = True
    hsts_preload: bool = False  # Can be enabled in production
    csp_report_uri: Optional[str] = None  # For CSP violation reporting
    custom_security_headers: Optional[dict] = None  # Additional custom headers
    
    @property
    def supabase_url(self) -> str:
        """Get the Supabase URL."""
        return self.vite_supabase_url
    
    @property
    def supabase_anon_key(self) -> str:
        """Get the Supabase anonymous key."""
        return self.vite_supabase_anon_key
    
    @property
    def is_production(self) -> bool:
        """Check if the application is running in production mode."""
        return self.environment.lower() in ("production", "prod") or not self.debug
    
    @property
    def is_development(self) -> bool:
        """Check if the application is running in development mode."""
        return self.environment.lower() in ("development", "dev") and self.debug
    
    @property
    def cors_origins_safe(self) -> List[str]:
        """Get CORS origins with development defaults if in dev mode."""
        if self.is_development and not self.cors_origins:
            return [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
            ]
        return self.cors_origins
    
    @property
    def session_https_only_safe(self) -> bool:
        """Get session HTTPS setting with environment awareness."""
        if self.is_development:
            return False  # Allow HTTP in development
        return self.session_https_only
    
    @property
    def docs_enabled(self) -> bool:
        """Check if API documentation should be enabled."""
        return self.is_development or self.debug
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()
