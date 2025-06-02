"""
Validation utility functions.
Enhanced comprehensive input validation framework for security.
"""
import re
import html
import string
import ipaddress
from typing import Any, Dict, List, Optional, Set, Union, Tuple
from urllib.parse import urlparse
from email_validator import validate_email, EmailNotValidError

# Import centralized configuration
from .validation_config import validation_config


def is_valid_email(email: str) -> bool:
    """Validate email address format."""
    try:
        # Additional length and character validation
        if not email or len(email) > 320 or len(email) < 3:
            return False
        
        # Check for dangerous characters
        if any(char in email for char in ['<', '>', '"', "'", '&']):
            return False
            
        # Use email_validator but allow test domains
        validate_email(email, check_deliverability=False)
        return True
    except (EmailNotValidError, Exception):
        return False


def is_valid_uuid(uuid_string: str) -> bool:
    """Validate UUID format."""
    if not uuid_string or len(uuid_string) != 36:
        return False
        
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(uuid_string))


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate that required fields are present and not empty."""
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    return missing_fields


def sanitize_string(text: str, max_length: Optional[int] = None, allow_html: Optional[bool] = None) -> str:
    """Sanitize string input with XSS protection."""
    if not isinstance(text, str):
        return ""
    
    # Use configuration defaults if not provided
    config = validation_config.input
    max_length = max_length if max_length is not None else config.max_string_length
    allow_html = allow_html if allow_html is not None else not config.html_escape_by_default
    
    # Remove leading/trailing whitespace if configured
    if config.strip_whitespace:
        sanitized = text.strip()
    else:
        sanitized = text
    
    # HTML escape to prevent XSS attacks unless explicitly allowed
    if not allow_html:
        sanitized = html.escape(sanitized)
    
    # Remove dangerous characters if configured
    if config.forbidden_control_chars:
        sanitized = sanitized.replace('\x00', '')  # Remove null bytes
        sanitized = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]', '', sanitized)  # Remove control characters
    
    # Truncate if max_length is specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def sanitize_url(url: str, allowed_schemes: Optional[List[str]] = None, 
                 allowed_domains: Optional[List[str]] = None,
                 allow_localhost: Optional[bool] = None) -> str:
    """Enhanced URL sanitization with domain and security validation."""
    if not isinstance(url, str) or not url.strip():
        return ""
    
    # Use configuration defaults if not provided
    config = validation_config.url
    allowed_schemes = allowed_schemes if allowed_schemes is not None else config.allowed_schemes
    allowed_domains = allowed_domains if allowed_domains is not None else config.allowed_domains
    allow_localhost = allow_localhost if allow_localhost is not None else config.allow_localhost
    
    url = url.strip()
    
    # Check maximum URL length
    if len(url) > config.max_url_length:
        return ""
    
    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception:
        return ""
    
    # Check scheme
    if not parsed.scheme:
        # Prepend https if no scheme provided
        url = 'https://' + url
        try:
            parsed = urlparse(url)
        except Exception:
            return ""
    
    if parsed.scheme.lower() not in [s.lower() for s in allowed_schemes]:
        return ""
    
    # Validate hostname
    if not parsed.netloc:
        return ""
    
    hostname = parsed.netloc.split(':')[0].lower()  # Remove port if present
    
    # Check if it's an IP address
    try:
        ip = ipaddress.ip_address(hostname)
        # Block private/reserved IPs in production unless explicitly allowed
        if not allow_localhost and (ip.is_private or ip.is_loopback or ip.is_reserved):
            return ""
    except ValueError:
        # It's a hostname, not an IP
        pass
    
    # Check against allowed domains if specified
    if allowed_domains:
        domain_allowed = False
        for allowed_domain in allowed_domains:
            if hostname == allowed_domain.lower() or hostname.endswith('.' + allowed_domain.lower()):
                domain_allowed = True
                break
        if not domain_allowed:
            return ""
    
    # Additional hostname validation
    hostname_pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    )
    if not hostname_pattern.match(hostname) and not allow_localhost:
        return ""
    
    return url


def validate_positive_integer(value: Any, max_value: Optional[int] = None, min_value: int = 1) -> bool:
    """Enhanced integer validation with configurable minimum."""
    try:
        num = int(value)
        if num < min_value:
            return False
        if max_value is not None and num > max_value:
            return False
        return True
    except (ValueError, TypeError):
        return False


def validate_phone_number(phone: str, strict_international: Optional[bool] = None) -> bool:
    """Enhanced phone number validation with configurable strictness."""
    if not phone or not isinstance(phone, str):
        return False
    
    # Use configuration default if not provided
    config = validation_config.phone
    strict_international = strict_international if strict_international is not None else config.strict_international
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Basic length validation
    if len(cleaned) < config.min_length or len(cleaned) > config.max_length + 1:  # +1 for the + sign
        return False
    
    if strict_international:
        # Strict international format validation
        # Must start with + followed by country code and number
        phone_pattern = re.compile(r'^\+[1-9]\d{7,14}$')
        return bool(phone_pattern.match(cleaned))
    else:
        # More lenient validation for various formats
        # Allow numbers with or without country code
        patterns = [
            re.compile(r'^\+[1-9]\d{7,14}$'),  # International format
            re.compile(r'^[1-9]\d{6,14}$'),    # National format without +
        ]
        return any(pattern.match(cleaned) for pattern in patterns)


def validate_country_code(country_code: str) -> bool:
    """Validate ISO 3166-1 alpha-2 country code format."""
    if not isinstance(country_code, str) or len(country_code) != 2:
        return False
    return country_code.upper().isalpha()


def sanitize_metadata_key(key: str, max_length: Optional[int] = None) -> str:
    """Enhanced metadata key sanitization with configurable length."""
    if not isinstance(key, str):
        return ""
    
    # Use configuration default if not provided
    max_length = max_length if max_length is not None else validation_config.metadata.max_key_length
    
    # Only allow alphanumeric characters, underscores, and hyphens
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', key)
    
    # Ensure it doesn't start with underscore or hyphen
    sanitized = re.sub(r'^[_-]+', '', sanitized)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # Ensure minimum length
    if len(sanitized) < 1:
        return ""
    
    return sanitized


def validate_metadata_size(metadata: Dict[str, Any], max_total_size: Optional[int] = None) -> bool:
    """Validate total metadata size in bytes."""
    if not isinstance(metadata, dict):
        return False
    
    # Use configuration default if not provided
    max_total_size = max_total_size if max_total_size is not None else validation_config.metadata.max_total_size_bytes
    
    try:
        total_size = len(str(metadata).encode('utf-8'))
        return total_size <= max_total_size
    except Exception:
        return False


def sanitize_metadata_value(value: Any, max_string_length: Optional[int] = None) -> Any:
    """Sanitize metadata values recursively."""
    # Use configuration default if not provided
    max_string_length = max_string_length if max_string_length is not None else validation_config.metadata.max_string_value_length
    
    if isinstance(value, str):
        return sanitize_string(value, max_length=max_string_length)
    elif isinstance(value, dict):
        return {
            sanitize_metadata_key(k): sanitize_metadata_value(v, max_string_length)
            for k, v in value.items()
            if sanitize_metadata_key(k)  # Only include valid keys
        }
    elif isinstance(value, list):
        max_items = validation_config.metadata.max_list_items
        return [sanitize_metadata_value(item, max_string_length) for item in value[:max_items]]
    elif isinstance(value, (int, float, bool)) or value is None:
        return value
    else:
        # Convert other types to sanitized string
        return sanitize_string(str(value), max_length=max_string_length)


def validate_password_complexity(password: str, min_length: Optional[int] = None, 
                                require_uppercase: Optional[bool] = None,
                                require_lowercase: Optional[bool] = None,
                                require_digits: Optional[bool] = None,
                                require_special: Optional[bool] = None,
                                forbidden_patterns: Optional[List[str]] = None,
                                user_info: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[str]]:
    """
    Enhanced password complexity validation with security strengthening.
    
    This function now uses the enhanced password security module that cannot be bypassed
    and includes checks for common passwords and dictionary attacks.
    
    Parameters are deprecated - the new system enforces strong defaults.
    
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    # Import the enhanced validator
    from .password_security import validate_password_strength
    
    # Use the new enhanced validation that cannot be bypassed
    is_valid, error_messages = validate_password_strength(password, user_info)
    
    return is_valid, error_messages


def validate_input_length(value: str, min_length: int = 0, max_length: int = 1000, field_name: str = "Input") -> bool:
    """Validate input string length with descriptive errors."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    
    if len(value) < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters long")
    
    if len(value) > max_length:
        raise ValueError(f"{field_name} must not exceed {max_length} characters")
    
    return True


def validate_allowed_values(value: str, allowed_values: Set[str], field_name: str = "Value", 
                           case_sensitive: bool = False) -> bool:
    """Validate that a value is in the allowed set."""
    if not case_sensitive:
        value = value.lower()
        allowed_values = {v.lower() for v in allowed_values}
    
    if value not in allowed_values:
        allowed_list = ", ".join(sorted(allowed_values))
        raise ValueError(f"{field_name} must be one of: {allowed_list}")
    
    return True


def sanitize_filename(filename: str, max_length: Optional[int] = None) -> str:
    """Sanitize filename to prevent directory traversal and invalid characters."""
    if not isinstance(filename, str):
        return ""
    
    # Use configuration default if not provided
    max_length = max_length if max_length is not None else validation_config.input.max_filename_length
    
    # Remove path separators and dangerous characters
    sanitized = re.sub(r'[<>:"|?*\\/]', '', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Limit length
    if len(sanitized) > max_length:
        # Keep extension if possible
        parts = sanitized.rsplit('.', 1)
        if len(parts) == 2 and len(parts[1]) <= 10:  # Reasonable extension length
            name_part = parts[0][:max_length - len(parts[1]) - 1]
            sanitized = f"{name_part}.{parts[1]}"
        else:
            sanitized = sanitized[:max_length]
    
    # Ensure not empty after sanitization
    if not sanitized:
        return "file"
    
    return sanitized


def validate_json_structure(data: Any, max_depth: Optional[int] = None, current_depth: int = 0) -> bool:
    """Validate JSON structure depth to prevent deeply nested objects."""
    # Use configuration default if not provided
    max_depth = max_depth if max_depth is not None else validation_config.input.max_json_depth
    
    if current_depth > max_depth:
        return False
    
    if isinstance(data, dict):
        return all(validate_json_structure(v, max_depth, current_depth + 1) for v in data.values())
    elif isinstance(data, list):
        return all(validate_json_structure(item, max_depth, current_depth + 1) for item in data)
    else:
        return True


def validate_ip_address(ip_str: str, allow_private: bool = False) -> bool:
    """Validate IP address format and optionally restrict private addresses."""
    try:
        ip = ipaddress.ip_address(ip_str)
        if not allow_private and (ip.is_private or ip.is_loopback or ip.is_reserved):
            return False
        return True
    except ValueError:
        return False


# Convenience functions for common validation patterns
def validate_user_input(value: str, max_length: Optional[int] = None, allow_html: Optional[bool] = None) -> str:
    """Validate and sanitize general user input."""
    # Use configuration defaults if not provided
    max_length = max_length if max_length is not None else validation_config.input.max_string_length
    
    sanitized = sanitize_string(value, max_length=max_length, allow_html=allow_html)
    if not sanitized.strip():
        raise ValueError("Input cannot be empty")
    return sanitized


def validate_search_query(query: str, max_length: Optional[int] = None) -> str:
    """Validate and sanitize search queries."""
    if not isinstance(query, str):
        raise ValueError("Search query must be a string")
    
    # Use configuration default if not provided
    max_length = max_length if max_length is not None else validation_config.input.max_search_query_length
    
    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', query.strip())
    
    # Basic sanitization
    sanitized = sanitize_string(sanitized, max_length=max_length)
    
    if len(sanitized) < 1:
        raise ValueError("Search query cannot be empty")
    
    return sanitized


# Export validation functions for easy import
__all__ = [
    'is_valid_email', 'is_valid_uuid', 'validate_required_fields',
    'sanitize_string', 'sanitize_url', 'validate_positive_integer',
    'validate_phone_number', 'validate_country_code', 'sanitize_metadata_key',
    'validate_metadata_size', 'sanitize_metadata_value', 'validate_password_complexity',
    'validate_input_length', 'validate_allowed_values', 'sanitize_filename',
    'validate_json_structure', 'validate_ip_address', 'validate_user_input',
    'validate_search_query'
]
