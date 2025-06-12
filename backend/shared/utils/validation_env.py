"""
Environment-specific validation configuration loader.
This module configures the validation framework based on the application environment.
"""

import os
from typing import Optional
from .validation_config import (
    validation_config,
    configure_for_production,
    configure_for_development,
    configure_for_testing
)


def load_validation_config(environment: Optional[str] = None) -> None:
    """
    Load validation configuration based on environment.
    
    Args:
        environment: Environment name ('production', 'development', 'testing').
                    If None, will try to detect from ENV environment variable.
    """
    if environment is None:
        environment = os.getenv('ENV', 'development').lower()
    
    environment = environment.lower()
    
    if environment == 'production':
        configure_for_production()
        print(f"🔒 Validation configured for PRODUCTION environment")
    elif environment == 'testing':
        configure_for_testing()
        print(f"🧪 Validation configured for TESTING environment")
    else:  # development or any other environment
        configure_for_development()
        print(f"🛠️ Validation configured for DEVELOPMENT environment")
    
    # Log configuration summary
    config_summary = validation_config.get_config_summary()
    print(f"   Password min length: {config_summary['password']['min_length']}")
    print(f"   Metadata max size: {config_summary['metadata']['max_size_kb']}KB")
    print(f"   URL localhost allowed: {config_summary['url']['allow_localhost']}")


def get_validation_settings() -> dict:
    """
    Get current validation settings for debugging/monitoring.
    
    Returns:
        Dictionary with current validation configuration
    """
    return {
        'environment': os.getenv('ENV', 'development'),
        'config_summary': validation_config.get_config_summary(),
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }


# Ensure validation is explicitly configured by the caller
if not hasattr(validation_config, '_configured'):
    validation_config._configured = False


__all__: list[str] = ['load_validation_config', 'get_validation_settings']
