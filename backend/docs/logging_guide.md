# Advanced Logging & Performance Guidelines (as of June 2025)

## Structured Logging & Performance Metrics

Since June 2025, Cookify uses structured logging with performance tracking for all critical endpoints. Key improvements:

- **Use `get_logger(__name__)` in all modules**
- **Context and data fields**: Always use `context` and `data` parameters for machine-readable logs
- **Performance logging**: Log explicit duration (`duration_ms`), file size, confidence scores etc. for all important operations (e.g. OCR, database, health checks)
- **Performance logging decorator**: Use `@log_performance` from `core/performance.py` for automatic timing and logging
- **Error handling**: Errors are always logged with context, error code and timing

### Example: OCR Performance Log

```python
logger.info(
    "OCR text extraction completed successfully",
    context={
        "filename": image.filename,
        "file_size_bytes": len(image_data),
        "extracted_text_length": len(result.extracted_text),
        "confidence_score": result.confidence,
        "ocr_processing_time_ms": result.processing_time_ms,
        "total_request_time_ms": request_duration_ms,
        "endpoint": "/ocr/extract-text"
    },
    data={
        "performance_metrics": {
            "file_size_bytes": len(image_data),
            "ocr_processing_time_ms": result.processing_time_ms,
            "total_request_time_ms": request_duration_ms,
            "confidence_score": result.confidence
        }
    }
)
```

### Example: Performance Logging Decorator

```python
from core.performance import log_performance

@log_performance("ocr_processing")
async def process_receipt_with_ocr(image: UploadFile):
    ... # Function is automatically logged with timing and success/error tracking
```

### Error Logging with Timing

```python
try:
    ... # Operation
except CustomError as e:
    logger.error(
        "Custom error occurred",
        context={
            "endpoint": "/api/endpoint",
            "error_code": e.error_code,
            "error_message": e.message,
            "duration_ms": duration_ms
        }
    )
    raise
```

## Best Practices (2025 Update)

- Always use structured logs with context
- Log performance metrics for all critical operations
- Never log sensitive data
- Always log errors with error code, context and duration
- Use the new decorators for performance and DB logging
- See also: `docs/improved_logging_guide.md` for complete examples and monitoring strategies

---

# Logging Guide for Cookify Backend

## Overview

The Cookify backend uses an extended, structured logging system based on Python's standard `logging` module. The system provides the following features:

- Structured logs with uniform format (text or JSON)
- Context-based logging for better traceability
- Automatic enrichment of logs with metadata
- Performance optimization through caching of logger instances
- Configurable log levels for different application parts
- Support for file and console logging

## Using Logger

### Getting a Logger

Always use the `get_logger` function to obtain a logger:

```python
from core.logging import get_logger

# Typically call with __name__ to use the module name
logger = get_logger(__name__)

# Or with a custom name
logger = get_logger("custom.name")
```

### Logging with Different Levels

```python
# Basic logging levels
logger.trace("Very detailed debug information")
logger.debug("Debug information for developers")
logger.info("General information about application flows")
logger.warning("Warning that requires attention")
logger.error("Error that impairs functionality")
logger.critical("Critical error requiring immediate action")

# For exceptions with automatic stacktrace
try:
    # Code that might fail
    raise ValueError("Example exception")
except Exception as e:
    logger.exception("An exception occurred")
```

### Structured Logging with Context

```python
# Logging with additional context
logger.info(
    "User logged in",
    context={
        "user_id": "abc123",
        "ip_address": "192.168.1.1"
    }
)

# Logging with context and structured data
logger.info(
    "Order completed",
    context={"user_id": "abc123"},
    data={
        "order_id": "order-123",
        "items_count": 5,
        "total_price": 49.99
    }
)
```

## Best Practices

### Using Log Levels Correctly

- **TRACE**: Very detailed information, only for deep debugging purposes
- **DEBUG**: Detail information for developers during development and debugging
- **INFO**: General information about normal application flows
- **WARNING**: Potentially problematic situations requiring attention
- **ERROR**: Errors that prevent an operation but the application continues
- **CRITICAL**: Critical errors that might terminate the application

### Structured Logs for Machine Processing

Always use the `context` and `data` parameter for structured information instead of embedding them in the message:

```python
# DON'T:
logger.info(f"User {user_id} ordered {items_count} items for {total_price}€")

# BETTER:
logger.info(
    "Order completed",
    context={"user_id": user_id},
    data={"items_count": items_count, "total_price": total_price}
)
```

### Protecting Personal Data

- Never log passwords, tokens or other confidential information
- Limit personal data to what's necessary, especially at higher log levels
- Truncate long personal identifiers when needed (e.g. "user@exa...com")

### Performance Optimization

For extensive or complex log messages, check if the corresponding log level is enabled first:

```python
if logger.isEnabledFor(logging.DEBUG):
    complex_debug_info = generate_expensive_debug_info()
    logger.debug("Complex debug info", data=complex_debug_info)
```

## Configuration

The logging configuration is defined in `core/config.py` and can be adjusted via environment variables:

- `LOG_LEVEL`: General log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FORMAT_JSON`: True for JSON format, False for text format
- `LOG_TO_FILE`: True to write logs to files
- `LOG_DIR`: Directory for log files
- `CONSOLE_LOG_LEVEL`: Log level for console output
- `DOMAINS_LOG_LEVEL`: Log level for domain modules
- `MIDDLEWARE_LOG_LEVEL`: Log level for middleware modules

## Examples of Typical Logging Patterns

### Authentication and Security

```python
# Successful login
logger.info(
    "User logged in",
    context={"user_id": user.id, "ip_address": client_ip}
)

# Failed login
logger.warning(
    "Login failed",
    context={
        "username": username,  # Don't log full email
        "ip_address": client_ip,
        "attempt_count": attempt_count
    }
)

# Security-relevant event
logger.error(
    "Rate limit exceeded",
    context={
        "ip_address": client_ip,
        "endpoint": request.url.path,
        "violations_count": violations_count
    }
)
```

### API Requests and Performance

```python
# API request with duration
logger.info(
    "API request processed",
    context={
        "endpoint": request.url.path,
        "method": request.method,
        "duration_ms": duration_ms,
        "status_code": response.status_code
    }
)

# Database operations
logger.debug(
    "Database query executed",
    context={"table": "users", "operation": "SELECT"},
    data={"query_duration_ms": query_time, "results_count": len(results)}
)
```

### Error Handling

```python
try:
    # Perform operation
    result = perform_operation()
    return result
except ValueError as e:
    # Known error case
    logger.warning(
        "Invalid input data",
        context={"operation": "perform_operation"},
        data={"validation_errors": str(e)}
    )
    raise
except Exception as e:
    # Unexpected error
    logger.exception(
        "Unexpected error in operation",
        context={"operation": "perform_operation"}
    )
    # Exception is automatically logged with stack trace
    raise
```

## Logging Configuration in Development

For local development we recommend:

```bash
LOG_LEVEL=DEBUG
LOG_FORMAT_JSON=False
LOG_TO_FILE=False
```

## Logging Configuration in Production

For production environments we recommend:

```bash
LOG_LEVEL=INFO
LOG_FORMAT_JSON=True
LOG_TO_FILE=True
LOG_DIR=/var/log/cookify
```
