"""
Logging configuration for the FastAPI application.
"""
import logging
import logging.config
import sys
from typing import Dict, Any
from .config import settings


def setup_logging() -> None:
    """Setup application logging configuration."""
    
    # Define logging configuration
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": settings.log_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
            },
            "detailed": {
                "formatter": "detailed",
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {  # root logger
                "level": settings.log_level,
                "handlers": ["default"],
            },
            "app": {
                "level": settings.log_level,
                "handlers": ["detailed"],
                "propagate": False,
            },
            "app.domains.auth": {
                "level": "DEBUG" if settings.debug else "INFO",
                "handlers": ["detailed"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO" if settings.enable_access_log else "WARNING",
                "handlers": ["default"],
                "propagate": False,
            },
        },
    }
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Log startup message
    logger = logging.getLogger("app")
    logger.info(f"Logging configured - Level: {settings.log_level}, Debug: {settings.debug}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name."""
    return logging.getLogger(f"app.{name}")
