# Verwende Python 3.10 slim als Basis-Image für bessere Performance
FROM python:3.10-slim

# Setze Arbeitsverzeichnis
WORKDIR /backend

# Installiere System-Dependencies (inkl. curl für Healthcheck)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Kopiere Requirements und installiere Python-Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere die Backend-Anwendung
COPY . .

# Erstelle einen Non-Root-User für Sicherheit
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /backend
USER appuser

# Exponiere Port 8000 (um mit lokaler Entwicklung konsistent zu sein)
EXPOSE 8000

# Healthcheck für Container-Status mit verbessertem Endpoint
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Starte die Anwendung mit optimierten Einstellungen
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--access-log"]