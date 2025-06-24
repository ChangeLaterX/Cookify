"""
Professional logging configuration for the FastAPI application.

This module provides an enhanced logging system with the following features:
- Structured logging with consistent formats (text or JSON)
- Flexible routing of logs to different output destinations
- Automatic context information in each log (process ID, thread ID)
- Customizable log levels for different application parts
- Performance optimization for production environments
- Support for structured logs and tracing

Usage:
    # Get logger for a module
    from core.logging import get_logger
    logger = get_logger(__name__)

    # Logging with different levels
    logger.info("Informative message")
    logger.warning("Warning")
    logger.error("Error occurred", extra={"context": {"user_id": 123}})

    # Structured logging with additional context
    logger.info(
        "User login",
        extra={
            "context": {
                "user_id": "abc123",
                "ip_address": "192.168.1.1",
                "request_id": "req-123"
            }
        }
    )
"""

import json
import logging
import logging.config
import os
import platform
import socket
import sys
import time
import traceback
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from .config import settings

# Konstanten für Log-Level-Namen
TRACE = 5  # Niedrigeres Level als DEBUG
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# Mapping von String-Namen zu numerischen Log-Levels
LOG_LEVEL_MAP = {
    "TRACE": TRACE,
    "DEBUG": DEBUG,
    "INFO": INFO,
    "WARNING": WARNING,
    "ERROR": ERROR,
    "CRITICAL": CRITICAL,
}


class JsonFormatter(logging.Formatter):
    """
    Formatter for JSON-formatted logs.

    Produces machine-readable logs in JSON format with a consistent structure.
    Automatically adds metadata such as timestamp, process ID, etc.
    """

    def __init__(self, include_stack_info: bool = False) -> None:
        """
        Initializes the JSON formatter.

        Args:
            include_stack_info: Whether stack traces should be included
        """
        super().__init__()
        self.include_stack_info = include_stack_info
        self.hostname = socket.gethostname()

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats the log entry as a JSON string.

        Args:
            record: The LogRecord to be formatted

        Returns:
            JSON-formatted log entry as a string
        """
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "process": {"id": record.process, "name": record.processName},
            "thread": {"id": record.thread, "name": record.threadName},
            "code_location": {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
                "module": record.module,
            },
            "system": {"hostname": self.hostname, "environment": settings.ENVIRONMENT},
        }

        # Zusätzlicher Kontext aus dem extra-Parameter
        if hasattr(record, "context") and isinstance(record.context, dict):
            log_data["context"] = record.context

        # Zusätzliche strukturierte Daten
        if hasattr(record, "data") and isinstance(record.data, dict):
            log_data["data"] = record.data

        # Fehlerinformationen hinzufügen, wenn vorhanden
        if record.exc_info and self.include_stack_info:
            exception_type, exception_value, exception_tb = record.exc_info
            formatted_exception = traceback.format_exception(
                exception_type, exception_value, exception_tb
            )
            log_data["exception"] = {
                "type": exception_type.__name__ if exception_type else None,
                "message": str(exception_value) if exception_value else None,
                "stacktrace": formatted_exception,
            }

        # Formatieren als JSON mit UTF-8-Kodierung
        return json.dumps(log_data, ensure_ascii=False, default=str)


class StructuredLogger:
    """
    Enhanced logger with support for structured logging.

    Provides a consistent interface for logging with additional context
    and structured data.
    """

    def __init__(self, logger: logging.Logger):
        """
        Initializes the StructuredLogger.

        Args:
            logger: The standard logger to be used
        """
        self._logger = logger

    def _log(
        self,
        level: int,
        msg: str,
        context: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        exc_info: Any = None,
    ) -> None:
        """
        Generic logging method with context and structured data.

        Args:
            level: Log level (DEBUG, INFO, etc.)
            msg: The log message
            context: Additional context for the log entry
            data: Structured data for the log entry
            exc_info: Exception information
        """
        extra = {}
        if context:
            extra["context"] = context
        if data:
            extra["data"] = data

        self._logger.log(level, msg, extra=extra if extra else None, exc_info=exc_info)

    def trace(
        self,
        msg: str,
        context: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Trace-level logging with context.

        Args:
            msg: The log message
            context: Additional context for the log entry
            data: Structured data for the log entry
        """
        self._log(TRACE, msg, context, data)

    def debug(
        self,
        msg: str,
        context: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Debug-level logging with context.

        Args:
            msg: The log message
            context: Additional context for the log entry
            data: Structured data for the log entry
        """
        self._log(DEBUG, msg, context, data)

    def info(
        self,
        msg: str,
        context: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Info-level logging with context.

        Args:
            msg: The log message
            context: Additional context for the log entry
            data: Structured data for the log entry
        """
        self._log(INFO, msg, context, data)

    def warning(
        self,
        msg: str,
        context: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Warning-level logging with context.

        Args:
            msg: The log message
            context: Additional context for the log entry
            data: Structured data for the log entry
        """
        self._log(WARNING, msg, context, data)

    def error(
        self,
        msg: str,
        context: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        exc_info: Any = None,
    ) -> None:
        """
        Error-level logging with context and optional exception info.

        Args:
            msg: The log message
            context: Additional context for the log entry
            data: Structured data for the log entry
            exc_info: Exception information (True, Exception or Exception tuple)
        """
        self._log(ERROR, msg, context, data, exc_info=exc_info)

    def critical(
        self,
        msg: str,
        context: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        exc_info: Any = None,
    ) -> None:
        """
        Critical-Level Logging mit Kontext und optionalem Exception-Info.

        Args:
            msg: Die Log-Nachricht
            context: Zusätzlicher Kontext für den Log-Eintrag
            data: Strukturierte Daten für den Log-Eintrag
            exc_info: Exception-Informationen (True, Exception oder Exception-Tuple)
        """
        self._log(CRITICAL, msg, context, data, exc_info=exc_info)

    def exception(
        self,
        msg: str,
        context: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Exception-Logging mit automatischem Exception-Info.

        Args:
            msg: Die Log-Nachricht
            context: Zusätzlicher Kontext für den Log-Eintrag
            data: Strukturierte Daten für den Log-Eintrag
        """
        self._log(ERROR, msg, context, data, exc_info=True)


def setup_logging() -> None:
    """
    Konfiguriert das Logging-System für die Anwendung.

    Diese Funktion sollte früh beim Anwendungsstart aufgerufen werden,
    bevor andere Module importiert werden.
    """
    # TRACE-Level hinzufügen, falls es noch nicht existiert
    if not hasattr(logging, "TRACE"):
        logging.TRACE = TRACE
        logging.addLevelName(TRACE, "TRACE")

    # Log-Verzeichnis erstellen, falls es nicht existiert
    if settings.LOG_TO_FILE:
        log_dir = Path(settings.LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)

    # Log-Format basierend auf Einstellungen auswählen
    use_json_format = settings.LOG_FORMAT_JSON

    # Log-Konfiguration definieren
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {"()": JsonFormatter, "include_stack_info": True},
        },
        "handlers": {
            "console": {
                "level": settings.CONSOLE_LOG_LEVEL,
                "formatter": "json" if use_json_format else "detailed",
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {  # Root-Logger
                "level": settings.LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "app": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "app.domains": {
                "level": settings.DOMAINS_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "app.middleware": {
                "level": settings.MIDDLEWARE_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO" if settings.ENABLE_ACCESS_LOG else "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

    # Datei-Handler hinzufügen, wenn LOG_TO_FILE aktiviert ist
    if settings.LOG_TO_FILE:
        # Datei für allgemeine Logs
        logging_config["handlers"]["file"] = {
            "level": settings.LOG_LEVEL,
            "formatter": "json" if use_json_format else "detailed",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(Path(settings.LOG_DIR) / "app.log"),
            "when": "midnight",
            "backupCount": 14,
            "encoding": "utf-8",
        }

        # Separate Datei für Fehler
        logging_config["handlers"]["error_file"] = {
            "level": "ERROR",
            "formatter": "json" if use_json_format else "detailed",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(Path(settings.LOG_DIR) / "error.log"),
            "when": "midnight",
            "backupCount": 30,  # Längere Aufbewahrung für Fehler
            "encoding": "utf-8",
        }

        # Handler zu allen Loggern hinzufügen
        for logger_name in logging_config["loggers"]:
            logging_config["loggers"][logger_name]["handlers"].extend(
                ["file", "error_file"]
            )

    # Logging-Konfiguration anwenden
    logging.config.dictConfig(logging_config)

    # Startmeldung loggen
    logger = logging.getLogger("app")
    logger.info(
        f"Logging-System initialisiert",
        extra={
            "context": {
                "log_level": settings.LOG_LEVEL,
                "environment": settings.ENVIRONMENT,
                "json_format": use_json_format,
                "log_to_file": settings.LOG_TO_FILE,
                "hostname": socket.gethostname(),
                "python_version": platform.python_version(),
            }
        },
    )


@lru_cache(maxsize=100)
def get_logger(name: str) -> StructuredLogger:
    """
    Gibt eine Instanz des erweiterten strukturierten Loggers zurück.

    Der Logger-Name wird automatisch mit dem 'app'-Präfix versehen, wenn er
    nicht bereits beginnt. Die Funktion verwendet ein LRU-Cache um die
    Performance bei häufigen Aufrufen zu optimieren.

    Args:
        name: Name des Loggers (typischerweise __name__)

    Returns:
        Eine Instanz von StructuredLogger

    Beispiel:
        logger = get_logger(__name__)
        logger.info("Anwendung gestartet", context={"user_id": "abc123"})
    """
    # Logger-Namen normalisieren
    if name.startswith("app."):
        logger_name = name
    elif name == "__main__":
        logger_name = "app.main"
    else:
        logger_name = f"app.{name}"

    # Standard-Logger abrufen und als StructuredLogger zurückgeben
    std_logger = logging.getLogger(logger_name)
    return StructuredLogger(std_logger)
