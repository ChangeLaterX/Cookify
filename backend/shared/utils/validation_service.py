"""
Comprehensive Input Validation Service.
This service provides high-level validation methods for common use cases.
"""

from typing import Dict, Any, List, Optional, Tuple
from .validation import (
    validate_password_complexity,
    sanitize_metadata_value,
    validate_metadata_size,
    sanitize_metadata_key,
    validate_phone_number,
    sanitize_url,
    validate_user_input,
    validate_search_query,
    is_valid_email,
    is_valid_uuid,
    validate_required_fields,
    sanitize_string,
    validate_positive_integer,
    validate_country_code,
    sanitize_filename,
    validate_json_structure,
    validate_ip_address,
)

# Import centralized settings
from core.config import settings


class ValidationService:
    """
    High-level validation service that combines multiple validation functions
    for comprehensive input validation.
    """

    @staticmethod
    def validate_user_registration(
        data: Dict[str, Any],
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Comprehensive validation for user registration data.

        Returns:
            Tuple of (is_valid, error_messages, sanitized_data)
        """
        errors = []
        sanitized = {}

        # Required fields
        required = settings.USER_REGISTRATION_REQUIRED_FIELDS
        missing_fields = validate_required_fields(data, required)
        if missing_fields:
            errors.extend(
                [f"Missing required field: {field}" for field in missing_fields]
            )
            return False, errors, {}

        # Email validation
        email = data.get("email", "").strip()
        if not is_valid_email(email):
            errors.append("Invalid email address format")
        else:
            sanitized["email"] = email.lower()

        # Password validation
        password = data.get("password", "")
        is_valid_password, password_errors = validate_password_complexity(password)
        if not is_valid_password:
            errors.extend(password_errors)
        else:
            sanitized["password"] = password

        # Phone validation (optional)
        phone = data.get("phone")
        if phone:
            if validate_phone_number(phone):
                sanitized["phone"] = phone
            else:
                errors.append("Invalid phone number format")

        # Metadata validation (optional)
        metadata = data.get("user_metadata")
        if metadata:
            if not validate_metadata_size(metadata):
                errors.append("User metadata too large")
            else:
                # Check for forbidden keys
                forbidden_keys = settings.METADATA_FORBIDDEN_KEYS
                for key in metadata.keys():
                    if key.lower() in forbidden_keys:
                        errors.append(f"Metadata cannot contain sensitive field: {key}")
                        break
                else:
                    # Sanitize metadata
                    sanitized_metadata = {}
                    for key, value in metadata.items():
                        sanitized_key = sanitize_metadata_key(key)
                        if sanitized_key:
                            sanitized_metadata[sanitized_key] = sanitize_metadata_value(
                                value
                            )
                    sanitized["user_metadata"] = sanitized_metadata

        return len(errors) == 0, errors, sanitized

    @staticmethod
    def validate_user_update(
        data: Dict[str, Any],
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Comprehensive validation for user profile update data.

        Returns:
            Tuple of (is_valid, error_messages, sanitized_data)
        """
        errors = []
        sanitized = {}

        # Email validation (optional)
        email = data.get("email")
        if email:
            email = email.strip()
            if not is_valid_email(email):
                errors.append("Invalid email address format")
            else:
                sanitized["email"] = email.lower()

        # Phone validation (optional)
        phone = data.get("phone")
        if phone:
            if validate_phone_number(phone):
                sanitized["phone"] = phone
            else:
                errors.append("Invalid phone number format")

        # Metadata validation (optional)
        metadata = data.get("user_metadata")
        if metadata:
            if not validate_metadata_size(metadata):
                errors.append("User metadata too large")
            else:
                forbidden_keys = settings.METADATA_FORBIDDEN_KEYS
                for key in metadata.keys():
                    if key.lower() in forbidden_keys:
                        errors.append(f"Metadata cannot contain sensitive field: {key}")
                        break
                else:
                    sanitized_metadata = {}
                    for key, value in metadata.items():
                        sanitized_key = sanitize_metadata_key(key)
                        if sanitized_key:
                            sanitized_metadata[sanitized_key] = sanitize_metadata_value(
                                value
                            )
                    sanitized["user_metadata"] = sanitized_metadata

        return len(errors) == 0, errors, sanitized

    @staticmethod
    def validate_password_reset(
        data: Dict[str, Any],
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validation for password reset requests.

        Returns:
            Tuple of (is_valid, error_messages, sanitized_data)
        """
        errors = []
        sanitized = {}

        # Required fields
        required = settings.PASSWORD_RESET_REQUIRED_FIELDS
        missing_fields = validate_required_fields(data, required)
        if missing_fields:
            errors.extend(
                [f"Missing required field: {field}" for field in missing_fields]
            )
            return False, errors, {}

        # Email validation
        email = data.get("email", "").strip()
        if not is_valid_email(email):
            errors.append("Invalid email address format")
        else:
            sanitized["email"] = email.lower()

        return len(errors) == 0, errors, sanitized

    @staticmethod
    def validate_password_update(
        data: Dict[str, Any],
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validation for password update requests.

        Returns:
            Tuple of (is_valid, error_messages, sanitized_data)
        """
        errors = []
        sanitized = {}

        # Required fields
        required = settings.PASSWORD_UPDATE_REQUIRED_FIELDS
        missing_fields = validate_required_fields(data, required)
        if missing_fields:
            errors.extend(
                [f"Missing required field: {field}" for field in missing_fields]
            )
            return False, errors, {}

        # Password validation
        password = data.get("password", "")
        is_valid_password, password_errors = validate_password_complexity(password)
        if not is_valid_password:
            errors.extend(password_errors)
        else:
            sanitized["password"] = password

        return len(errors) == 0, errors, sanitized

    @staticmethod
    def validate_magic_link_request(
        data: Dict[str, Any],
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validation for magic link requests.

        Returns:
            Tuple of (is_valid, error_messages, sanitized_data)
        """
        errors = []
        sanitized = {}

        # Required fields
        required = settings.MAGIC_LINK_REQUIRED_FIELDS
        missing_fields = validate_required_fields(data, required)
        if missing_fields:
            errors.extend(
                [f"Missing required field: {field}" for field in missing_fields]
            )
            return False, errors, {}

        # Email validation
        email = data.get("email", "").strip()
        if not is_valid_email(email):
            errors.append("Invalid email address format")
        else:
            sanitized["email"] = email.lower()

        # Redirect URL validation (optional)
        redirect_to = data.get("redirect_to")
        if redirect_to:
            sanitized_url = sanitize_url(redirect_to)
            if not sanitized_url:
                errors.append("Invalid redirect URL")
            else:
                sanitized["redirect_to"] = sanitized_url

        return len(errors) == 0, errors, sanitized

    @staticmethod
    def validate_otp_verification(
        data: Dict[str, Any],
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validation for OTP verification requests.

        Returns:
            Tuple of (is_valid, error_messages, sanitized_data)
        """
        errors = []
        sanitized = {}

        # Required fields
        required = settings.OTP_VERIFICATION_REQUIRED_FIELDS
        missing_fields = validate_required_fields(data, required)
        if missing_fields:
            errors.extend(
                [f"Missing required field: {field}" for field in missing_fields]
            )
            return False, errors, {}

        # Email validation
        email = data.get("email", "").strip()
        if not is_valid_email(email):
            errors.append("Invalid email address format")
        else:
            sanitized["email"] = email.lower()

        # Token validation
        token = data.get("token", "").strip()
        if not token:
            errors.append("Token cannot be empty")
        elif not token.isdigit():
            errors.append("Token must contain only digits")
        elif (
            len(token) < settings.OTP_TOKEN_MIN_LENGTH
            or len(token) > settings.OTP_TOKEN_MAX_LENGTH
        ):
            errors.append(
                f"Token must be {settings.OTP_TOKEN_MIN_LENGTH}-{settings.OTP_TOKEN_MAX_LENGTH} digits long"
            )
        else:
            sanitized["token"] = token

        # Type validation
        otp_type = data.get("type", "").strip().lower()
        allowed_types = set(settings.OTP_ALLOWED_TYPES)
        if otp_type not in allowed_types:
            errors.append(f"Type must be one of: {', '.join(sorted(allowed_types))}")
        else:
            sanitized["type"] = otp_type

        return len(errors) == 0, errors, sanitized

    @staticmethod
    def validate_search_request(
        data: Dict[str, Any],
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validation for search requests.

        Returns:
            Tuple of (is_valid, error_messages, sanitized_data)
        """
        errors = []
        sanitized: Dict[str, Any] = {}

        # Query validation
        query = data.get("query", "").strip()
        if not query:
            errors.append("Search query cannot be empty")
        else:
            try:
                sanitized_query = validate_search_query(query)
                sanitized["query"] = sanitized_query
            except ValueError as e:
                errors.append(str(e))

        # Limit validation (optional)
        limit = data.get("limit")
        if limit is not None:
            if not validate_positive_integer(
                limit,
                max_value=settings.SEARCH_LIMIT_MAX_VALUE,
                min_value=settings.SEARCH_LIMIT_MIN_VALUE,
            ):
                errors.append(
                    f"Limit must be a positive integer between {settings.SEARCH_LIMIT_MIN_VALUE} and {settings.SEARCH_LIMIT_MAX_VALUE}"
                )
            else:
                sanitized["limit"] = int(limit)

        # Offset validation (optional)
        offset = data.get("offset")
        if offset is not None:
            if not validate_positive_integer(offset, min_value=0):
                errors.append("Offset must be a non-negative integer")
            else:
                sanitized["offset"] = int(offset)

        return len(errors) == 0, errors, sanitized

    @staticmethod
    def validate_api_request_common(
        data: Dict[str, Any],
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Common validation for API requests (pagination, sorting, etc.).

        Returns:
            Tuple of (is_valid, error_messages, sanitized_data)
        """
        errors = []
        sanitized: Dict[str, Any] = {}

        # Pagination
        page = data.get("page")
        if page is not None:
            if not validate_positive_integer(
                page, min_value=settings.PAGINATION_PAGE_MIN
            ):
                errors.append("Page must be a positive integer")
            else:
                sanitized["page"] = int(page)

        per_page = data.get("per_page")
        if per_page is not None:
            if not validate_positive_integer(
                per_page,
                max_value=settings.PAGINATION_PER_PAGE_MAX,
                min_value=settings.PAGINATION_PER_PAGE_MIN,
            ):
                errors.append(
                    f"Per page must be between {settings.PAGINATION_PER_PAGE_MIN} and {settings.PAGINATION_PER_PAGE_MAX}"
                )
            else:
                sanitized["per_page"] = int(per_page)

        # Sorting
        sort_by = data.get("sort_by")
        if sort_by:
            try:
                sanitized_sort = validate_user_input(
                    sort_by, max_length=settings.API_SORT_BY_MAX_LENGTH
                )
                sanitized["sort_by"] = sanitized_sort
            except ValueError as e:
                errors.append(f"Invalid sort_by: {e}")

        sort_order = data.get("sort_order")
        if sort_order:
            if sort_order.lower() not in settings.API_ALLOWED_SORT_ORDERS:
                errors.append(
                    f"Sort order must be one of: {', '.join(settings.API_ALLOWED_SORT_ORDERS)}"
                )
            else:
                sanitized["sort_order"] = sort_order.lower()

        return len(errors) == 0, errors, sanitized


# Create a global instance
validation_service = ValidationService()

# Export the service
__all__ = ["ValidationService", "validation_service"]
