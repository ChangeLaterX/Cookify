# Use Python 3.12.11 slim as base image for better performance and security
FROM python:3.12.11-slim

# Set metadata labels for better container management
LABEL maintainer="Cookify Team"
LABEL version="1.0"
LABEL description="Cookify API with OCR capabilities"

# Set working directory
WORKDIR /backend

# Install system dependencies with security focus
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    tesseract-ocr \
    tesseract-ocr-eng \
    libmagic1 \
    ca-certificates \
    && (apt-get install -y --no-install-recommends tesseract-ocr-deu || echo "German language pack not available") \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y

# Create non-root user early for security
RUN adduser --disabled-password --gecos '' --shell /bin/false --uid 1000 appuser

# Copy requirements first for better Docker layer caching
COPY --chown=appuser:appuser requirements.txt .

# Install Python dependencies with security considerations
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --require-hashes -r requirements.txt \
    || pip install --no-cache-dir -r requirements.txt

# Install additional security packages
RUN pip install --no-cache-dir python-magic

# Create secure directories before copying application
RUN mkdir -p /tmp/ocr_secure /backend/logs \
    && chown -R appuser:appuser /tmp/ocr_secure /backend/logs /backend \
    && chmod 700 /tmp/ocr_secure

# Copy the backend application with proper ownership
COPY --chown=appuser:appuser . .

# Set environment variables for security and optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/backend \
    TMPDIR=/tmp/ocr_secure \
    HOME=/backend \
    USER=appuser

# Switch to non-root user before creating scripts
USER appuser

# Create healthcheck script with proper error handling
RUN echo '#!/bin/bash\n\
set -e\n\
if curl -f --max-time 10 --retry 3 --retry-delay 1 http://localhost:8000/api/health > /dev/null 2>&1; then\n\
    echo "Health check passed"\n\
    exit 0\n\
else\n\
    echo "Health check failed"\n\
    exit 1\n\
fi' > /backend/healthcheck.sh \
    && chmod +x /backend/healthcheck.sh

# Expose port 8000
EXPOSE 8000

# Add healthcheck with improved configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD ["/backend/healthcheck.sh"]

# Start the application with settings optimized for low-resource servers
CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--access-log", \
     "--log-level", "info", \
     "--no-server-header"]