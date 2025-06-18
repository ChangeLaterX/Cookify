"""
Enhanced configuration management for the FastAPI application.

This module provides a centralized configuration system using Pydantic's BaseSettings.
All constants are defined in uppercase. Sensitive values are loaded from environment 
variables (.env), while default values are defined directly in the code.

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
from typing import Optional, List, Set, Tuple
from dataclasses import field
import secrets
import os


class Settings(BaseSettings):
    """
    Application configuration with automatic environment variable loading.
    
    Secret configuration values are loaded directly from environment variables using os.getenv.
    Non-secret values have default values defined in this class and can be overridden
    by environment variables if needed.
    
    Important notes on configuration:
    - Secret values are always loaded from environment variables (.env)
    - Most other settings can be adjusted directly in the code
    - Environment variables can be used for temporary overrides
    
    Settings are loaded in the following order:
    1. Environment variables
    2. .env file values (for secrets)
    3. Default values defined in this class
    
    Secret values loaded from the .env file:
    - SUPABASE_URL, SUPABASE_KEY
    - JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION
    - SESSION_SECRET_KEY
    """
    # Application Settings
    # These settings can be overridden by environment variables with the same name
    APP_NAME: str = "Cookify Meal Planning API"
    DEBUG: bool = True  # Set to False in production environments
    DOCS_URL: Optional[str] = "/docs"
    REDOC_URL: Optional[str] = "/redoc"
    VERSION: str = "0.1.0"

    # Environment detection
    ENVIRONMENT: str = "development"  # 'development' or 'production'

    # Supabase Configuration - SENSITIVE, loaded from environment variables
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # Security Settings - SENSITIVE, loaded from environment variables
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET", "") or secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRATION", "30"))
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", "") or secrets.token_urlsafe(32)

    # Authentication Settings
    REQUIRE_EMAIL_VERIFICATION: bool = False
    PASSWORD_MIN_LENGTH: int = 8
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    FRONTEND_URL: str = "http://localhost:3000"

    # Rate Limiting Settings
    RATE_LIMITING_ENABLED: bool = True  # Base setting, overridden by rate_limiting_enabled_safe property
    RATE_LIMIT_LOGIN_ATTEMPTS: int = 5  # Login attempts per window
    RATE_LIMIT_LOGIN_WINDOW_MINUTES: int = 15  # Window for login attempts
    RATE_LIMIT_REGISTRATION_ATTEMPTS: int = 3  # Registration attempts per window
    RATE_LIMIT_REGISTRATION_WINDOW_MINUTES: int = 5  # Window for registration attempts
    RATE_LIMIT_PASSWORD_RESET_ATTEMPTS: int = 3  # Password reset attempts per window
    RATE_LIMIT_PASSWORD_RESET_WINDOW_MINUTES: int = 60  # Window for password reset attempts

    # Cache Settings
    USER_CACHE_TTL_SECONDS: int = 300  # 5 minutes
    ENABLE_USER_CACHE: bool = True

    # CORS Configuration - restrictive by default
    # If the environment variable exists, it will be loaded as a JSON array
    # Example: CORS_ORIGINS='["http://localhost:3000","http://localhost:8000"]'
    CORS_ORIGINS: List[str] = []  # Loaded from CORS_ORIGINS environment variable if available
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_ALLOW_HEADERS: List[str] = ["Authorization", "Content-Type", "X-Request-ID"]

    # Middleware Settings
    TRUSTED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    ENABLE_TRUSTED_HOST_MIDDLEWARE: bool = True  # Enable by default for security
    SESSION_HTTPS_ONLY: bool = True  # Enable HTTPS by default
    SESSION_SAME_SITE: str = "strict"  # More secure default

    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FORMAT_JSON: bool = False  # True for JSON-formatted logs, False for text
    CONSOLE_LOG_LEVEL: str = "INFO"
    DOMAINS_LOG_LEVEL: str = "DEBUG" if DEBUG else "INFO"
    MIDDLEWARE_LOG_LEVEL: str = "DEBUG" if DEBUG else "INFO"
    LOG_TO_FILE: bool = False  # True to write logs to files
    LOG_DIR: str = "backend/logs"  # Directory for log files
    ENABLE_ACCESS_LOG: bool = True  # Enable HTTP access logging

    # Security Headers Settings
    # Enable or disable security headers middleware.
    # When enabled, the application will enforce security headers such as HSTS, CSP, etc.,
    # to enhance security in production environments.
    SECURITY_HEADERS_ENABLED: bool = True
    HSTS_MAX_AGE: int = 31536000  # 1 year in seconds
    HSTS_INCLUDE_SUBDOMAINS: bool = True
    HSTS_PRELOAD: bool = False  # Can be enabled in production
    CSP_REPORT_URI: Optional[str] = None  # For CSP violation reporting
    CUSTOM_SECURITY_HEADERS: Optional[dict] = None  # Additional custom headers

    # Password Security Settings
    PASSWORD_MIN_SECURITY_LENGTH: int = 6  # Minimum password length for security checks
    PASSWORD_MAX_LENGTH: int = 128  # Maximum password length
    PASSWORD_MIN_UNIQUE_CHARS: int = 6  # Minimum unique characters required
    PASSWORD_MAX_REPEATED_CHAR_RATIO: float = 0.4  # Maximum ratio of repeated characters
    PASSWORD_MIN_CHAR_TYPES: int = 3  # Minimum character types required (out of 4)
    PASSWORD_MIN_ENTROPY_SCORE: int = 35  # Minimum entropy score
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGITS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    PASSWORD_STRENGTH_VERY_STRONG_THRESHOLD: int = 90  # Score thresholds for password strength
    PASSWORD_STRENGTH_STRONG_THRESHOLD: int = 75
    PASSWORD_STRENGTH_GOOD_THRESHOLD: int = 60
    PASSWORD_STRENGTH_FAIR_THRESHOLD: int = 45
    PASSWORD_STRENGTH_WEAK_THRESHOLD: int = 25
    PASSWORD_RECOMMENDED_MIN_LENGTH: int = 16  # Recommended minimum length for warnings
    PASSWORD_BONUS_MIN_LENGTH: int = 20  # Length for additional security bonus
    PASSWORD_MIN_UNIQUE_CHARS_BONUS: int = 12  # Unique chars for bonus

    # Rate Limiting Advanced Settings
    RATE_LIMIT_PROGRESSIVE_MULTIPLIER: float = 2.0  # Progressive delay multiplier
    RATE_LIMIT_MAX_PROGRESSIVE_DELAY: int = 300  # Maximum progressive delay in seconds (5 minutes)
    RATE_LIMIT_CLEANUP_INTERVAL: int = 600  # Cleanup interval in seconds (10 minutes)
    RATE_LIMIT_CLEANUP_CUTOFF: int = 3600  # Data cutoff time in seconds (1 hour)
    RATE_LIMIT_USER_AGENT_LENGTH: int = 50  # Maximum user agent length for tracking
    RATE_LIMIT_RESET_PASSWORD_ATTEMPTS: int = 5  # Password reset confirmation attempts
    RATE_LIMIT_RESET_PASSWORD_WINDOW: int = 900  # Password reset window in seconds (15 minutes)
    RATE_LIMIT_VERIFY_EMAIL_ATTEMPTS: int = 5  # Email verification attempts
    RATE_LIMIT_VERIFY_EMAIL_WINDOW: int = 300  # Email verification window in seconds (5 minutes)
    RATE_LIMIT_RESEND_VERIFICATION_ATTEMPTS: int = 2  # Resend verification attempts
    RATE_LIMIT_RESEND_VERIFICATION_WINDOW: int = 1800  # Resend verification window in seconds (30 minutes)
    RATE_LIMIT_REFRESH_TOKEN_ATTEMPTS: int = 20  # Token refresh attempts
    RATE_LIMIT_REFRESH_TOKEN_WINDOW: int = 300  # Token refresh window in seconds (5 minutes)
    RATE_LIMIT_DEFAULT_AUTH_ATTEMPTS: int = 10  # Default auth endpoint attempts
    RATE_LIMIT_DEFAULT_AUTH_WINDOW: int = 600  # Default auth window in seconds (10 minutes)

    # Validation Settings
    VALIDATION_METADATA_MAX_KEY_LENGTH: int = 50  # Maximum metadata key length
    VALIDATION_METADATA_MAX_TOTAL_SIZE: int = 1024  # Maximum total metadata size in bytes
    VALIDATION_EMAIL_MIN_LENGTH: int = 3  # Minimum email part length for personal info check
    VALIDATION_NAME_MIN_LENGTH: int = 3  # Minimum name length for personal info check
    VALIDATION_USER_ID_MIN_LENGTH: int = 4  # Minimum user ID length for personal info check

    # Common Password Pattern Settings
    COMMON_PASSWORD_YEAR_LIST: List[str] = ["2024", "2025", "2026", "21", "22", "23", "24", "25"]
    COMMON_PASSWORD_PREFIX_LIST: List[str] = ["my", "the", "new", "old"]
    COMMON_PASSWORD_SUFFIX_LIST: List[str] = ["123", "1", "!", "?", ".", "@", "#", "$", "0", "00"]
    COMMON_PASSWORD_MIN_VARIATION_LENGTH: int = 4  # Minimum length for password variations

    # Dictionary Attack Pattern Settings
    INCREMENTAL_PATTERN_LIST: List[str] = ["0123", "1234", "2345", "3456", "4567", "5678", "6789", "9876", "8765", "7654", "6543", "5432", "4321", "3210"]
    ALTERNATING_PATTERN_LIST: List[str] = ["0101", "1010", "1212", "2121", "abab", "baba"]

    # Security Pattern Timeouts and Limits
    LEET_SPEAK_SUBSTITUTIONS: dict = field(default_factory=lambda: {
        'a': ['4', '@'], 'e': ['3', '€'], 'i': ['1', '!'], 'o': ['0'],
        's': ['5', '$'], 't': ['7'], 'l': ['1', '!'], 'g': ['9', '§']
    })

    # Entropy Calculation Settings
    ENTROPY_LOWERCASE_CHARS: int = 26
    ENTROPY_UPPERCASE_CHARS: int = 26  
    ENTROPY_DIGIT_CHARS: int = 10

    # Date and Time Settings
    DATE_CALCULATION_HOURS_PER_DAY: int = 24
    DATE_CALCULATION_MINUTES_PER_HOUR: int = 60
    DATE_CALCULATION_SECONDS_PER_MINUTE: int = 60
    DATE_CALCULATION_MILLISECONDS_PER_SECOND: int = 1000
    DATE_DAYS_THRESHOLD_MONTH: int = 30  # Days threshold for month calculation

    # File and Content Limits
    MAX_FILE_SIZE_BYTES: int = 1048576  # 1MB default file size limit
    MAX_CONTENT_LENGTH: int = 1024  # Maximum content length for various operations

    # Default Expiration Times (in days)
    DEFAULT_PANTRY_SHORT_EXPIRATION: int = 3
    DEFAULT_PANTRY_MEDIUM_EXPIRATION: int = 7  
    DEFAULT_PANTRY_LONG_EXPIRATION: int = 14
    DEFAULT_PANTRY_EXPIRED_DAYS: int = 1  # Days in the past for expired items

    # Input Validation Settings
    INPUT_MAX_STRING_LENGTH: int = 1000
    INPUT_MAX_SEARCH_QUERY_LENGTH: int = 200
    INPUT_MAX_FILENAME_LENGTH: int = 255
    INPUT_MAX_JSON_DEPTH: int = 10
    INPUT_FORBIDDEN_CONTROL_CHARS: bool = True
    INPUT_HTML_ESCAPE_BY_DEFAULT: bool = True
    INPUT_STRIP_WHITESPACE: bool = True

    # URL Validation Settings
    URL_ALLOWED_SCHEMES: List[str] = ["http", "https"]
    URL_ALLOWED_DOMAINS: List[str] = []  # Empty list means all domains allowed
    URL_ALLOW_LOCALHOST: bool = True
    URL_ALLOW_PRIVATE_IPS: bool = False
    URL_MAX_URL_LENGTH: int = 2048

    # Phone Validation Settings
    PHONE_STRICT_INTERNATIONAL: bool = True
    PHONE_MIN_LENGTH: int = 7
    PHONE_MAX_LENGTH: int = 15
    PHONE_REQUIRE_COUNTRY_CODE: bool = True
    PHONE_ALLOWED_COUNTRY_CODES: Set[str] = set()  # Empty set means all are allowed

    # Metadata Validation Settings (already included above with validation_ prefix)
    METADATA_MAX_NESTING_DEPTH: int = 5
    METADATA_FORBIDDEN_KEYS: Set[str] = field(default_factory=lambda: {
        "password", "token", "secret", "key", "auth", "session",
        "api_key", "private_key", "access_token", "refresh_token", 
        "credentials", "jwt", "bearer", "authorization"
    })
    METADATA_MAX_STRING_VALUE_LENGTH: int = 1000
    METADATA_MAX_LIST_ITEMS: int = 100

    # Security Token Settings
    SECURITY_TOKEN_LENGTH: int = 32  # Length for generated tokens and secret keys

    # HTTP Status Code Settings
    HTTP_STATUS_SERVER_ERROR_THRESHOLD: int = 500  # Threshold for server errors
    HTTP_STATUS_CLIENT_ERROR_THRESHOLD: int = 400  # Threshold for client errors
    HTTP_RETRY_AFTER_DEFAULT: int = 60  # Default retry-after header value in seconds
    HTTP_UNPROCESSABLE_ENTITY: int = 422  # HTTP status for validation errors
    HTTP_INTERNAL_SERVER_ERROR: int = 500  # HTTP status for internal errors

    # Security Headers Settings (Additional)
    SECURITY_HSTS_MAX_AGE_DEFAULT: int = 31536000  # Default HSTS max age (1 year) for middleware fallback
    SECURITY_XSS_PROTECTION: str = "1; mode=block"  # X-XSS-Protection header value
    SECURITY_CONTENT_TYPE_OPTIONS: str = "nosniff"  # X-Content-Type-Options header value
    SECURITY_FRAME_OPTIONS: str = "DENY"  # X-Frame-Options header value
    SECURITY_REFERRER_POLICY: str = "strict-origin-when-cross-origin"  # Referrer-Policy header value

    # Content Security Policy Settings
    CSP_DEFAULT_SRC: str = "'self'"
    CSP_SCRIPT_SRC_DEV: str = "'self' 'unsafe-inline' 'unsafe-eval' localhost:* 127.0.0.1:* https://unpkg.com https://cdn.jsdelivr.net"
    CSP_SCRIPT_SRC_PROD: str = "'self'"
    CSP_STYLE_SRC_DEV: str = "'self' 'unsafe-inline' fonts.googleapis.com https://unpkg.com https://cdn.jsdelivr.net"
    CSP_STYLE_SRC_PROD: str = "'self' 'unsafe-inline'"
    CSP_FONT_SRC_DEV: str = "'self' fonts.gstatic.com https://unpkg.com https://cdn.jsdelivr.net"
    CSP_FONT_SRC_PROD: str = "'self'"
    CSP_IMG_SRC: str = "'self' data: blob: https:"
    CSP_CONNECT_SRC_DEV: str = "'self' localhost:* 127.0.0.1:* ws: wss:"
    CSP_CONNECT_SRC_PROD: str = "'self'"
    CSP_FRAME_ANCESTORS: str = "'none'"
    CSP_BASE_URI: str = "'self'"
    CSP_FORM_ACTION: str = "'self'"

    # Permissions Policy Settings
    PERMISSIONS_POLICY_CAMERA: str = "()"
    PERMISSIONS_POLICY_MICROPHONE: str = "()"
    PERMISSIONS_POLICY_GEOLOCATION: str = "()"
    PERMISSIONS_POLICY_PAYMENT: str = "()"
    PERMISSIONS_POLICY_USB: str = "()"
    PERMISSIONS_POLICY_MAGNETOMETER: str = "()"
    PERMISSIONS_POLICY_GYROSCOPE: str = "()"
    PERMISSIONS_POLICY_ACCELEROMETER: str = "()"
    PERMISSIONS_POLICY_AMBIENT_LIGHT: str = "()"
    PERMISSIONS_POLICY_AUTOPLAY: str = "()"
    PERMISSIONS_POLICY_ENCRYPTED_MEDIA: str = "()"
    PERMISSIONS_POLICY_FULLSCREEN: str = "(self)"
    PERMISSIONS_POLICY_PICTURE_IN_PICTURE: str = "()"

    # Rate Limiting Display Settings
    RATE_LIMIT_WINDOW_DISPLAY_MINUTES: int = 15  # Display value for rate limit window
    RATE_LIMIT_USER_AGENT_TRUNCATE_LENGTH: int = 50  # Length to truncate user agent in logs

    # Email Validation Settings
    EMAIL_MAX_LENGTH: int = 320  # Maximum email length
    EMAIL_MIN_LENGTH: int = 3  # Minimum email length
    EMAIL_DANGEROUS_CHARS: List[str] = ["<", ">", '"', "'", "&"]  # Characters to reject in emails

    # UUID Validation Settings
    UUID_LENGTH: int = 36  # Standard UUID length
    UUID_PATTERN: str = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'

    # Password Complexity Pattern Settings
    PASSWORD_FORBIDDEN_PATTERNS: List[str] = [
        r'(.)\1{3,}',  # 4+ repeated characters
        r'(0123|1234|2345|3456|4567|5678|6789|9876|8765|7654|6543|5432|4321|3210)',  # Sequential numbers
        r'(abcd|bcde|cdef|defg|efgh|fghi|ghij|hijk|ijkl|jklm|klmn|lmno|mnop|nopq|opqr|pqrs|qrst|rstu|stuv|tuvw|uvwx|vwxy|wxyz)',  # Sequential letters
        r'(qwer|wert|erty|rtyu|tyui|yuio|uiop|asdf|sdfg|dfgh|fghj|ghjk|hjkl|zxcv|xcvb|cvbn|vbnm)',  # Keyboard patterns
        r'^(password|admin|user|guest|login|welcome|secret|temp|test|demo)$',  # Common passwords
        r'^(123|abc|qwe|asd|zxc)$',  # Simple patterns
        r'^(password123|admin123|welcome123|letmein|qwerty123)$'  # Common combinations
    ]

    # Special Character Settings for Password Validation
    PASSWORD_SPECIAL_CHARS: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    PASSWORD_SPECIAL_CHARS_EXTENDED: str = "!@#$%^&*()_+-=[]{}|;:,.<>?~`"

    # Common Password Dictionary
    COMMON_PASSWORD_DICTIONARY: List[str] = [
        "password", "123456", "password123", "admin", "qwerty", "letmein", 
        "welcome", "monkey", "dragon", "master", "shadow", "123456789",
        "football", "baseball", "superman", "batman", "princess", "sunshine",
        "iloveyou", "trustno1", "starwars", "charlie", "mercedes", "chelsea",
        "liverpool", "manchester", "arsenal", "barcelona", "real", "madrid",
        "london", "paris", "newyork", "losangeles", "chicago", "boston",
        "toronto", "sydney", "melbourne", "berlin", "moscow", "tokyo",
        "beijing", "mumbai", "delhi", "shanghai", "bangkok", "singapore",
        "computer", "internet", "download", "program", "system", "windows",
        "username", "userid", "login", "logout", "signin", "signup",
        "register", "account", "profile", "settings", "config", "admin",
        "administrator", "root", "user", "guest", "anonymous", "public",
        "private", "personal", "business", "company", "corporate", "official",
        "government", "education", "university", "college", "school", "student",
        "teacher", "professor", "doctor", "engineer", "manager", "director",
        "president", "secretary", "assistant", "employee", "worker", "staff",
        "family", "mother", "father", "sister", "brother", "daughter", "son",
        "husband", "wife", "boyfriend", "girlfriend", "friend", "buddy",
        "birthday", "anniversary", "holiday", "christmas", "newyear", "valentine",
        "weekend", "holiday", "christmas", "newyear", "valentine",
        "company", "work", "office", "business", "money", "dollar",
        "super", "awesome", "amazing", "fantastic", "wonderful", "beautiful",
        "smart", "intelligent", "genius", "winner", "champion", "success",
        "lucky", "fortune", "magic", "power", "strong", "force",
        "apple", "google", "microsoft", "facebook", "twitter", "instagram",
        "linkedin", "youtube", "amazon", "netflix", "spotify", "gmail",
        "email", "internet", "website", "online", "digital", "computer",
        "laptop", "mobile", "phone", "device", "technology", "software",
        "ninja", "warrior", "samurai", "knight", "king", "queen",
        "prince", "princess", "angel", "devil", "god", "heaven",
        "earth", "world", "universe", "galaxy", "star", "moon",
        "sun", "light", "dark", "black", "white", "red", "blue",
        "green", "yellow", "orange", "purple", "pink", "silver", "gold"
    ]

    # Health Monitoring Settings
    # Configuration for health check endpoints and monitoring system
    HEALTH_MONITORING_ENABLED: bool = True  # Enable health monitoring system
    HEALTH_SYSTEM_MONITORING_ENABLED: bool = True  # Enable system resource monitoring
    HEALTH_PERFORMANCE_METRICS_ENABLED: bool = True  # Enable performance metrics collection
    HEALTH_EXTERNAL_SERVICE_CHECKS_ENABLED: bool = True  # Enable external service checks

    # Health Check Timeouts (milliseconds)
    HEALTH_DATABASE_QUERY_TIMEOUT: int = 5000  # Database health check timeout
    HEALTH_DATABASE_CONNECTION_TIMEOUT: int = 3000  # Database connection timeout
    HEALTH_AUTH_CHECK_TIMEOUT: int = 2000  # Authentication service timeout
    HEALTH_INGREDIENTS_QUERY_TIMEOUT: int = 3000  # Ingredients service timeout
    HEALTH_RECEIPT_OCR_CHECK_TIMEOUT: int = 1000  # Receipt OCR check timeout
    HEALTH_OVERALL_CHECK_TIMEOUT: int = 30  # Overall health check timeout (seconds)

    # Response Time Thresholds (milliseconds)
    HEALTH_RESPONSE_TIME_WARNING: int = 1000  # Warning threshold for response times
    HEALTH_RESPONSE_TIME_CRITICAL: int = 5000  # Critical threshold for response times

    # System Resource Thresholds (percentages)
    HEALTH_MEMORY_USAGE_WARNING: float = 80.0  # Memory usage warning threshold
    HEALTH_MEMORY_USAGE_CRITICAL: float = 95.0  # Memory usage critical threshold
    HEALTH_CPU_USAGE_WARNING: float = 80.0  # CPU usage warning threshold
    HEALTH_CPU_USAGE_CRITICAL: float = 95.0  # CPU usage critical threshold
    HEALTH_DISK_USAGE_WARNING: float = 85.0  # Disk usage warning threshold
    HEALTH_DISK_USAGE_CRITICAL: float = 95.0  # Disk usage critical threshold

    # Health Check Caching (seconds)
    HEALTH_DETAILED_CHECK_CACHE_TTL: int = 30  # Cache detailed health checks
    HEALTH_QUICK_CHECK_CACHE_TTL: int = 10  # Cache quick health checks

    # Health Check Retry Configuration
    HEALTH_MAX_RETRIES: int = 2  # Maximum retries for failed health checks
    HEALTH_RETRY_DELAY: float = 0.5  # Delay between retries (seconds)
    HEALTH_MAX_CONCURRENT_CHECKS: int = 10  # Maximum concurrent health checks

    # Health Metrics Collection
    HEALTH_METRICS_MAX_RETENTION: int = 1000  # Maximum metrics to retain per service
    HEALTH_ALERT_RETENTION_HOURS: int = 24  # Hours to retain alert history
    HEALTH_METRICS_CLEANUP_INTERVAL: int = 3600  # Cleanup interval (seconds)

    # Health Alert Thresholds
    HEALTH_CONSECUTIVE_FAILURES_ALERT: int = 3  # Alert after N consecutive failures
    HEALTH_DEGRADED_SERVICES_ALERT_PERCENT: float = 50.0  # Alert if >50% services degraded
    HEALTH_ALERT_COOLDOWN_MINUTES: int = 15  # Cooldown between similar alerts

    # Health Check Service Names
    HEALTH_SERVICE_NAMES: List[str] = ["auth", "ingredients", "receipt", "database", "system", "cache"]

    # Health Endpoint Settings
    HEALTH_ENDPOINT_PREFIX: str = "/health"  # Health endpoints prefix
    HEALTH_INCLUDE_SYSTEM_INFO: bool = True  # Include system info in detailed checks
    HEALTH_INCLUDE_PERFORMANCE_METRICS: bool = True  # Include performance metrics
    HEALTH_MASK_SENSITIVE_INFO: bool = True  # Mask sensitive information in health responses

    # Common Password Substitutions
    COMMON_PASSWORD_SUBSTITUTIONS: List[Tuple[str, str]] = [
        ("password", "p4ssw0rd"), ("password", "passw0rd"), ("password", "p@ssword"),
        ("admin", "4dmin"), ("admin", "@dmin"), ("welcome", "w3lcome"),
        ("hello", "h3llo"), ("love", "l0ve"), ("money", "m0ney")
    ]

    # Hostname Validation Pattern
    HOSTNAME_VALIDATION_PATTERN: str = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'

    # Control Characters Regex Pattern
    CONTROL_CHARS_PATTERN: str = r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]'

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
        return self.ENVIRONMENT.lower() in ("production", "prod") or not self.DEBUG

    @property
    def is_development(self) -> bool:
        """Check if the application is running in development mode."""
        return self.ENVIRONMENT.lower() in ("development", "dev") and self.DEBUG

    @property
    def rate_limiting_enabled_safe(self) -> bool:
        """Get rate limiting setting with debug mode awareness."""
        if self.DEBUG:
            return False  # Disable rate limiting in debug mode
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

    # Database Column Length Settings
    # These match Supabase auth.users table schema - DO NOT CHANGE unless schema changes
    DB_EMAIL_COLUMN_LENGTH: int = 255  # Standard email column length
    DB_TOKEN_COLUMN_LENGTH: int = 255  # Standard token column length  
    DB_PHONE_COLUMN_LENGTH: int = 15   # International phone number length
    DB_STATUS_COLUMN_LENGTH: int = 10  # Status field length

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "env_nested_delimiter": "__",
        "case_sensitive": True,
        "validate_default": True,
        "env_prefix": ""  # Don't use prefixes for environment variables
    }

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

    def print_config(self, mask_secrets: bool = True) -> None:
        """
        Prints the current configuration, useful for debugging purposes.
        
        Args:
            mask_secrets: If True, sensitive values will be masked
        """
        import json
        from pprint import pprint

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
        pprint(config_dict)
        print("\n=== Environment Overrides ===")
        pprint(self.show_environment_overrides())
        print("===============================\n")


# Global settings instance
settings = Settings()
