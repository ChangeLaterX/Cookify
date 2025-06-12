"""
Enhanced configuration management for the FastAPI application.
"""
from pydantic_settings import BaseSettings
from typing import Optional, List, Set, Tuple
from dataclasses import field
import secrets
import os


class Settings(BaseSettings):
    # Application Settings
    app_name: str = "APP API"
    debug: bool = True if os.getenv("DEBUG") == "true" else False
    docs_url: Optional[str] = "/docs"
    redoc_url: Optional[str] = "/redoc"
    version: str = "0.1.0"

    # Environment detection
    environment: str = "production"

    # Supabase Configuration
    vite_supabase_url: str = ""
    vite_supabase_anon_key: str = ""

    # Security Settings
    jwt_secret_key: str = secrets.token_urlsafe(32)
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    session_secret_key: str = secrets.token_urlsafe(32)

    # Authentication Settings
    require_email_verification: bool = False
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    frontend_url: str = "http://localhost:3000"

    # Rate Limiting Settings
    rate_limiting_enabled: bool = True  # Base setting, overridden by rate_limiting_enabled_safe property
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

    # Password Security Settings
    password_min_length: int = 6  # Minimum password length
    password_max_length: int = 128  # Maximum password length
    password_min_unique_chars: int = 6  # Minimum unique characters required
    password_max_repeated_char_ratio: float = 0.4  # Maximum ratio of repeated characters
    password_min_char_types: int = 3  # Minimum character types required (out of 4)
    password_min_entropy_score: int = 35  # Minimum entropy score
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digits: bool = True
    password_require_special: bool = True
    password_strength_very_strong_threshold: int = 90  # Score thresholds for password strength
    password_strength_strong_threshold: int = 75
    password_strength_good_threshold: int = 60
    password_strength_fair_threshold: int = 45
    password_strength_weak_threshold: int = 25
    password_recommended_min_length: int = 16  # Recommended minimum length for warnings
    password_bonus_min_length: int = 20  # Length for additional security bonus
    password_min_unique_chars_bonus: int = 12  # Unique chars for bonus
    
    # Rate Limiting Advanced Settings
    rate_limit_progressive_multiplier: float = 2.0  # Progressive delay multiplier
    rate_limit_max_progressive_delay: int = 300  # Maximum progressive delay in seconds (5 minutes)
    rate_limit_cleanup_interval: int = 600  # Cleanup interval in seconds (10 minutes)
    rate_limit_cleanup_cutoff: int = 3600  # Data cutoff time in seconds (1 hour)
    rate_limit_user_agent_length: int = 50  # Maximum user agent length for tracking
    rate_limit_reset_password_attempts: int = 5  # Password reset confirmation attempts
    rate_limit_reset_password_window: int = 900  # Password reset window in seconds (15 minutes)
    rate_limit_verify_email_attempts: int = 5  # Email verification attempts
    rate_limit_verify_email_window: int = 300  # Email verification window in seconds (5 minutes)
    rate_limit_resend_verification_attempts: int = 2  # Resend verification attempts
    rate_limit_resend_verification_window: int = 1800  # Resend verification window in seconds (30 minutes)
    rate_limit_refresh_token_attempts: int = 20  # Token refresh attempts
    rate_limit_refresh_token_window: int = 300  # Token refresh window in seconds (5 minutes)
    rate_limit_default_auth_attempts: int = 10  # Default auth endpoint attempts
    rate_limit_default_auth_window: int = 600  # Default auth window in seconds (10 minutes)
    
    # Validation Settings
    validation_metadata_max_key_length: int = 50  # Maximum metadata key length
    validation_metadata_max_total_size: int = 1024  # Maximum total metadata size in bytes
    validation_email_min_length: int = 3  # Minimum email part length for personal info check
    validation_name_min_length: int = 3  # Minimum name length for personal info check
    validation_user_id_min_length: int = 4  # Minimum user ID length for personal info check
    
    # Common Password Pattern Settings
    common_password_year_list: List[str] = ["2024", "2025", "2026", "21", "22", "23", "24", "25"]
    common_password_prefix_list: List[str] = ["my", "the", "new", "old"]
    common_password_suffix_list: List[str] = ["123", "1", "!", "?", ".", "@", "#", "$", "0", "00"]
    common_password_min_variation_length: int = 4  # Minimum length for password variations
    
    # Dictionary Attack Pattern Settings
    incremental_pattern_list: List[str] = ["0123", "1234", "2345", "3456", "4567", "5678", "6789", "9876", "8765", "7654", "6543", "5432", "4321", "3210"]
    alternating_pattern_list: List[str] = ["0101", "1010", "1212", "2121", "abab", "baba"]
    
    # Security Pattern Timeouts and Limits
    leet_speak_substitutions: dict = field(default_factory=lambda: {
        'a': ['4', '@'], 'e': ['3', '€'], 'i': ['1', '!'], 'o': ['0'],
        's': ['5', '$'], 't': ['7'], 'l': ['1', '!'], 'g': ['9', '§']
    })
    
    # Entropy Calculation Settings
    entropy_lowercase_chars: int = 26
    entropy_uppercase_chars: int = 26  
    entropy_digit_chars: int = 10
    
    # Date and Time Settings
    date_calculation_hours_per_day: int = 24
    date_calculation_minutes_per_hour: int = 60
    date_calculation_seconds_per_minute: int = 60
    date_calculation_milliseconds_per_second: int = 1000
    date_days_threshold_month: int = 30  # Days threshold for month calculation
    
    # File and Content Limits
    max_file_size_bytes: int = 1048576  # 1MB default file size limit
    max_content_length: int = 1024  # Maximum content length for various operations
    
    # Default Expiration Times (in days)
    default_pantry_short_expiration: int = 3
    default_pantry_medium_expiration: int = 7  
    default_pantry_long_expiration: int = 14
    default_pantry_expired_days: int = 1  # Days in the past for expired items
    
    # Input Validation Settings
    input_max_string_length: int = 1000
    input_max_search_query_length: int = 200
    input_max_filename_length: int = 255
    input_max_json_depth: int = 10
    input_forbidden_control_chars: bool = True
    input_html_escape_by_default: bool = True
    input_strip_whitespace: bool = True
    
    # URL Validation Settings
    url_allowed_schemes: List[str] = ["http", "https"]
    url_allowed_domains: List[str] = []  # Empty list means all domains allowed
    url_allow_localhost: bool = True
    url_allow_private_ips: bool = False
    url_max_url_length: int = 2048
    
    # Phone Validation Settings
    phone_strict_international: bool = True
    phone_min_length: int = 7
    phone_max_length: int = 15
    phone_require_country_code: bool = True
    phone_allowed_country_codes: Set[str] = set()  # Empty set means all are allowed
    
    # Metadata Validation Settings (already included above with validation_ prefix)
    metadata_max_nesting_depth: int = 5
    metadata_forbidden_keys: Set[str] = field(default_factory=lambda: {
        "password", "token", "secret", "key", "auth", "session",
        "api_key", "private_key", "access_token", "refresh_token", 
        "credentials", "jwt", "bearer", "authorization"
    })
    metadata_max_string_value_length: int = 1000
    metadata_max_list_items: int = 100

    # Security Token Settings
    security_token_length: int = 32  # Length for generated tokens and secret keys
    
    # HTTP Status Code Settings
    http_status_server_error_threshold: int = 500  # Threshold for server errors
    http_status_client_error_threshold: int = 400  # Threshold for client errors
    http_retry_after_default: int = 60  # Default retry-after header value in seconds
    http_unprocessable_entity: int = 422  # HTTP status for validation errors
    http_internal_server_error: int = 500  # HTTP status for internal errors
    
    # Security Headers Settings (Additional)
    security_hsts_max_age_default: int = 31536000  # Default HSTS max age (1 year) for middleware fallback
    security_xss_protection: str = "1; mode=block"  # X-XSS-Protection header value
    security_content_type_options: str = "nosniff"  # X-Content-Type-Options header value
    security_frame_options: str = "DENY"  # X-Frame-Options header value
    security_referrer_policy: str = "strict-origin-when-cross-origin"  # Referrer-Policy header value
    
    # Content Security Policy Settings
    csp_default_src: str = "'self'"
    csp_script_src_dev: str = "'self' 'unsafe-inline' 'unsafe-eval' localhost:* 127.0.0.1:* https://unpkg.com https://cdn.jsdelivr.net"
    csp_script_src_prod: str = "'self'"
    csp_style_src_dev: str = "'self' 'unsafe-inline' fonts.googleapis.com https://unpkg.com https://cdn.jsdelivr.net"
    csp_style_src_prod: str = "'self' 'unsafe-inline'"
    csp_font_src_dev: str = "'self' fonts.gstatic.com https://unpkg.com https://cdn.jsdelivr.net"
    csp_font_src_prod: str = "'self'"
    csp_img_src: str = "'self' data: blob: https:"
    csp_connect_src_dev: str = "'self' localhost:* 127.0.0.1:* ws: wss:"
    csp_connect_src_prod: str = "'self'"
    csp_frame_ancestors: str = "'none'"
    csp_base_uri: str = "'self'"
    csp_form_action: str = "'self'"
    
    # Permissions Policy Settings
    permissions_policy_camera: str = "()"
    permissions_policy_microphone: str = "()"
    permissions_policy_geolocation: str = "()"
    permissions_policy_payment: str = "()"
    permissions_policy_usb: str = "()"
    permissions_policy_magnetometer: str = "()"
    permissions_policy_gyroscope: str = "()"
    permissions_policy_accelerometer: str = "()"
    permissions_policy_ambient_light: str = "()"
    permissions_policy_autoplay: str = "()"
    permissions_policy_encrypted_media: str = "()"
    permissions_policy_fullscreen: str = "(self)"
    permissions_policy_picture_in_picture: str = "()"
    
    # Rate Limiting Display Settings
    rate_limit_window_display_minutes: int = 15  # Display value for rate limit window
    rate_limit_user_agent_truncate_length: int = 50  # Length to truncate user agent in logs
    
    # Email Validation Settings
    email_max_length: int = 320  # Maximum email length
    email_min_length: int = 3  # Minimum email length
    email_dangerous_chars: List[str] = ["<", ">", '"', "'", "&"]  # Characters to reject in emails
    
    # UUID Validation Settings
    uuid_length: int = 36  # Standard UUID length
    uuid_pattern: str = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    
    # Password Complexity Pattern Settings
    password_forbidden_patterns: List[str] = [
        r'(.)\1{3,}',  # 4+ repeated characters
        r'(0123|1234|2345|3456|4567|5678|6789|9876|8765|7654|6543|5432|4321|3210)',  # Sequential numbers
        r'(abcd|bcde|cdef|defg|efgh|fghi|ghij|hijk|ijkl|jklm|klmn|lmno|mnop|nopq|opqr|pqrs|qrst|rstu|stuv|tuvw|uvwx|vwxy|wxyz)',  # Sequential letters
        r'(qwer|wert|erty|rtyu|tyui|yuio|uiop|asdf|sdfg|dfgh|fghj|ghjk|hjkl|zxcv|xcvb|cvbn|vbnm)',  # Keyboard patterns
        r'^(password|admin|user|guest|login|welcome|secret|temp|test|demo)$',  # Common passwords
        r'^(123|abc|qwe|asd|zxc)$',  # Simple patterns
        r'^(password123|admin123|welcome123|letmein|qwerty123)$'  # Common combinations
    ]
    
    # Special Character Settings for Password Validation
    password_special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    password_special_chars_extended: str = "!@#$%^&*()_+-=[]{}|;:,.<>?~`"
    
    # Common Password Dictionary
    common_password_dictionary: List[str] = [
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
    
    # Common Password Substitutions
    common_password_substitutions: List[Tuple[str, str]] = [
        ("password", "p4ssw0rd"), ("password", "passw0rd"), ("password", "p@ssword"),
        ("admin", "4dmin"), ("admin", "@dmin"), ("welcome", "w3lcome"),
        ("hello", "h3llo"), ("love", "l0ve"), ("money", "m0ney")
    ]
    
    # Hostname Validation Pattern
    hostname_validation_pattern: str = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    
    # Control Characters Regex Pattern
    control_chars_pattern: str = r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]'
    
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
    def rate_limiting_enabled_safe(self) -> bool:
        """Get rate limiting setting with debug mode awareness."""
        if self.debug:
            return False  # Disable rate limiting in debug mode
        return self.rate_limiting_enabled

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

    # Database Column Length Settings
    # These match Supabase auth.users table schema - DO NOT CHANGE unless schema changes
    db_email_column_length: int = 255  # Standard email column length
    db_token_column_length: int = 255  # Standard token column length  
    db_phone_column_length: int = 15   # International phone number length
    db_status_column_length: int = 10  # Status field length

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()