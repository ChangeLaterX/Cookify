"""
Centralized validation configuration for the Input Validation Framework.
This file defines all validation rules and settings in one place.
"""

from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field

from core.config import settings


@dataclass
class PasswordValidationConfig:
    """Configuration for password complexity validation."""

    min_length: int = settings.PASSWORD_MIN_LENGTH
    max_length: int = settings.PASSWORD_MAX_LENGTH
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special: bool = True
    forbidden_patterns: List[str] = field(
        default_factory=lambda: [
            r"(.)\1{3,}",  # Four or more repeated characters (more lenient)
            r"123456",  # Longer sequential numbers
            r"abcdef",  # Longer sequential letters
            r"^password",  # Password at start (case insensitive)
            r"^admin",  # Admin at start
            r"^qwerty",  # Qwerty at start
            r"^letmein",  # Common password
            r"^welcome",  # Common password
            r"^secret",  # Common password
        ]
    )
    max_repeated_chars_ratio: float = settings.VALIDATION_MAX_REPEATED_CHARS_RATIO


@dataclass
class MetadataValidationConfig:
    """Configuration for metadata validation."""

    max_total_size_bytes: int = settings.VALIDATION_MAX_TOTAL_SIZE_BYTES  # 10KB
    max_key_length: int = 50
    max_string_value_length: int = 1000
    max_list_items: int = 100
    max_nesting_depth: int = 5

    # Keys that are forbidden in metadata
    forbidden_keys: Set[str] = field(
        default_factory=lambda: {
            "password",
            "token",
            "secret",
            "key",
            "auth",
            "session",
            "api_key",
            "private_key",
            "access_token",
            "refresh_token",
            "credentials",
            "jwt",
            "bearer",
            "authorization",
        }
    )


@dataclass
class PhoneValidationConfig:
    """Configuration for phone number validation."""

    strict_international: bool = True
    min_length: int = 7
    max_length: int = 15
    require_country_code: bool = True
    allowed_country_codes: Set[str] = field(
        default_factory=set
    )  # Empty set means all are allowed


@dataclass
class URLValidationConfig:
    """Configuration for URL validation."""

    allowed_schemes: List[str] = field(default_factory=lambda: ["http", "https"])
    allowed_domains: List[str] = field(
        default_factory=list
    )  # Empty list means all domains allowed
    allow_localhost: bool = True
    allow_private_ips: bool = False
    max_url_length: int = 2048


@dataclass
class InputValidationConfig:
    """Configuration for general input validation."""

    max_string_length: int = 1000
    max_search_query_length: int = 200
    max_filename_length: int = 255
    max_json_depth: int = 10

    # Characters that are always stripped/removed
    forbidden_control_chars: bool = True
    html_escape_by_default: bool = True
    strip_whitespace: bool = True


class ValidationConfigManager:
    """Centralized manager for all validation configurations."""

    def __init__(self) -> None:
        self.password = PasswordValidationConfig()
        self.metadata = MetadataValidationConfig()
        self.phone = PhoneValidationConfig()
        self.url = URLValidationConfig()
        self.input = InputValidationConfig()

        self._configured: bool = False

    def update_password_config(self, **kwargs) -> None:
        """Update password validation configuration."""
        for key, value in kwargs.items():
            if hasattr(self.password, key):
                setattr(self.password, key, value)

    def update_metadata_config(self, **kwargs) -> None:
        """Update metadata validation configuration."""
        for key, value in kwargs.items():
            if hasattr(self.metadata, key):
                setattr(self.metadata, key, value)

    def update_phone_config(self, **kwargs) -> None:
        """Update phone validation configuration."""
        for key, value in kwargs.items():
            if hasattr(self.phone, key):
                setattr(self.phone, key, value)

    def update_url_config(self, **kwargs) -> None:
        """Update URL validation configuration."""
        for key, value in kwargs.items():
            if hasattr(self.url, key):
                setattr(self.url, key, value)

    def update_input_config(self, **kwargs) -> None:
        """Update input validation configuration."""
        for key, value in kwargs.items():
            if hasattr(self.input, key):
                setattr(self.input, key, value)

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of all validation configurations."""
        return {
            "password": {
                "min_length": self.password.min_length,
                "max_length": self.password.max_length,
                "requires_complexity": True,
                "forbidden_patterns_count": len(self.password.forbidden_patterns),
            },
            "metadata": {
                "max_size_kb": self.metadata.max_total_size_bytes // 1024,
                "max_key_length": self.metadata.max_key_length,
                "forbidden_keys_count": len(self.metadata.forbidden_keys),
            },
            "phone": {
                "strict_international": self.phone.strict_international,
                "require_country_code": self.phone.require_country_code,
            },
            "url": {
                "allowed_schemes": self.url.allowed_schemes,
                "allow_localhost": self.url.allow_localhost,
                "max_length": self.url.max_url_length,
            },
            "input": {
                "max_string_length": self.input.max_string_length,
                "html_escape_default": self.input.html_escape_by_default,
                "max_json_depth": self.input.max_json_depth,
            },
        }


# Global configuration instance
validation_config = ValidationConfigManager()


# Environment-specific configurations
def configure_for_production():
    """Configure validation for production environment."""
    validation_config.update_password_config(
        min_length=12,  # Stricter in production
        forbidden_patterns=validation_config.password.forbidden_patterns
        + [
            r"company",  # Add company-specific patterns
            r"2024|2025",  # Current years
        ],
    )

    validation_config.update_url_config(allow_localhost=False, allow_private_ips=False)

    validation_config.update_metadata_config(
        max_total_size_bytes=8192,  # Smaller in production
    )


def configure_for_development():
    """Configure validation for development environment."""
    validation_config.update_password_config(
        min_length=8,  # More lenient in development
    )

    validation_config.update_url_config(allow_localhost=True, allow_private_ips=True)


def configure_for_testing():
    """Configure validation for testing environment."""
    validation_config.update_password_config(
        min_length=6, require_special=False  # Very lenient for testing
    )

    validation_config.update_metadata_config(
        max_total_size_bytes=1024,  # Small for testing
    )


# Export the configuration manager
__all__ = [
    "ValidationConfigManager",
    "validation_config",
    "configure_for_production",
    "configure_for_development",
    "configure_for_testing",
]
