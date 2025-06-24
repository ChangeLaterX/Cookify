"""
Utility functions and helpers.
"""

# Import validation framework components
from .validation import (
    is_valid_email,
    is_valid_uuid,
    sanitize_filename,
    sanitize_metadata_key,
    sanitize_metadata_value,
    sanitize_string,
    sanitize_url,
    validate_allowed_values,
    validate_country_code,
    validate_input_length,
    validate_ip_address,
    validate_json_structure,
    validate_metadata_size,
    validate_password_complexity,
    validate_phone_number,
    validate_positive_integer,
    validate_required_fields,
    validate_search_query,
    validate_user_input,
)
from .validation_config import ValidationConfigManager, validation_config
from .validation_service import ValidationService, validation_service

# Export all validation components
__all__ = [
    # Core validation functions
    "is_valid_email",
    "is_valid_uuid",
    "validate_required_fields",
    "sanitize_string",
    "sanitize_url",
    "validate_positive_integer",
    "validate_phone_number",
    "validate_country_code",
    "sanitize_metadata_key",
    "validate_metadata_size",
    "sanitize_metadata_value",
    "validate_password_complexity",
    "validate_input_length",
    "validate_allowed_values",
    "sanitize_filename",
    "validate_json_structure",
    "validate_ip_address",
    "validate_user_input",
    "validate_search_query",
    # Configuration management
    "validation_config",
    "ValidationConfigManager",
    # High-level validation service
    "validation_service",
    "ValidationService",
]
