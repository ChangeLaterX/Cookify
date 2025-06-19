# Logging and Error Handling Guide

## Übersicht

Dieses Dokument beschreibt die verbesserten Logging- und Fehlerbehandlungsstandards für die Cookify FastAPI-Anwendung.

## Strukturiertes Logging

### Verwendung der get_logger Funktion

Alle Module sollten den strukturierten Logger verwenden:

```python
from core.logging import get_logger

logger = get_logger(__name__)
```

### Logging-Formate

#### Info-Level Logging mit Kontext
```python
logger.info(
    "Operation completed successfully",
    context={
        "user_id": user_id,
        "operation": "user_registration",
        "endpoint": "/auth/register",
        "duration_ms": 150
    },
    data={
        "performance_metrics": {
            "processing_time_ms": 150,
            "database_queries": 3
        }
    }
)
```

#### Error-Level Logging
```python
logger.error(
    "Database operation failed",
    context={
        "operation": "user_lookup",
        "user_id": user_id,
        "error_code": "DATABASE_CONNECTION_FAILED",
        "endpoint": "/auth/login"
    }
)
```

#### Performance Logging
```python
logger.info(
    "OCR processing completed",
    context={
        "filename": "receipt.jpg",
        "file_size_bytes": 1024000,
        "confidence_score": 85.5,
        "processing_time_ms": 2340
    },
    data={
        "performance_metrics": {
            "ocr_processing_time_ms": 2340,
            "confidence_score": 85.5,
            "text_length": 1250
        }
    }
)
```

## Performance-Monitoring

### OCR-Verarbeitung

Für OCR-Endpunkte werden folgende Metriken geloggt:

- **Gesamte Request-Zeit**: Von Anfang bis Ende der HTTP-Anfrage
- **OCR-Verarbeitungszeit**: Nur die eigentliche OCR-Verarbeitung
- **Dateigröße**: Größe der hochgeladenen Datei
- **Confidence Score**: OCR-Konfidenzwert
- **Extrahierte Textlänge**: Anzahl der extrahierten Zeichen

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

### Performance-Decorator

Für automatisches Performance-Logging:

```python
from core.performance import log_performance

@log_performance("user_authentication")
async def authenticate_user(credentials: UserLogin):
    # Funktion wird automatisch mit Performance-Metriken geloggt
    pass
```

## Fehlerbehandlung

### Strukturierte Fehlerbehandlung in Routes

```python
async def route_function():
    request_start_time = time.time()
    
    try:
        # Hauptlogik
        logger.info(
            "Starting operation",
            context={
                "endpoint": "/api/endpoint",
                "operation": "data_processing"
            }
        )
        
        result = await process_data()
        
        duration_ms = int((time.time() - request_start_time) * 1000)
        
        logger.info(
            "Operation completed successfully",
            context={
                "endpoint": "/api/endpoint",
                "duration_ms": duration_ms
            }
        )
        
        return result
        
    except CustomError as e:
        duration_ms = int((time.time() - request_start_time) * 1000)
        logger.error(
            "Custom error occurred",
            context={
                "endpoint": "/api/endpoint",
                "error_code": e.error_code,
                "error_message": e.message,
                "duration_ms": duration_ms
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.message, "error_code": e.error_code}
        )
        
    except Exception as e:
        duration_ms = int((time.time() - request_start_time) * 1000)
        logger.error(
            "Unexpected error occurred",
            context={
                "endpoint": "/api/endpoint",
                "error_message": str(e),
                "duration_ms": duration_ms
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "error_code": "INTERNAL_ERROR"}
        )
```

## Best Practices

### 1. Konsistente Kontext-Felder

Verwenden Sie diese Standard-Kontext-Felder:

- `endpoint`: Der API-Endpunkt (z.B. "/ocr/extract-text")
- `operation`: Die durchgeführte Operation
- `duration_ms`: Dauer der Operation in Millisekunden
- `user_id`: Benutzer-ID (falls verfügbar)
- `request_id`: Eindeutige Request-ID (falls verfügbar)

### 2. Performance-Metriken

Loggen Sie immer:
- Start- und End-Zeitpunkte für längere Operationen
- Dateigrößen für File-Uploads
- Anzahl der verarbeiteten Elemente
- Confidence Scores für ML/AI-Operationen

### 3. Fehler-Kategorisierung

- **Validation Errors**: 400-Level mit `error_code`
- **Authentication Errors**: 401/403 mit User-Kontext
- **Not Found Errors**: 404 mit Resource-Information
- **Internal Errors**: 500 mit Exception-Details (ohne sensitive Daten)

### 4. Sensible Daten vermeiden

Niemals loggen:
- Passwörter oder API-Keys
- Persönliche Identifikationsdaten (außer IDs)
- Vollständige Dateiinhalte
- Kreditkarteninformationen

## Implementierte Verbesserungen

### OCR-Routes (/domains/ocr/routes.py)
- ✅ Strukturiertes Logging mit Kontext
- ✅ Performance-Metriken für alle OCR-Operationen
- ✅ Detaillierte Fehlerbehandlung mit Request-Timing
- ✅ Separate Metriken für OCR-Zeit vs. Gesamt-Request-Zeit

### Health-Routes (/domains/health/routes.py)
- ✅ Strukturiertes Logging für Health-Checks
- ✅ Performance-Metriken für Service-Überprüfungen
- ✅ Detaillierte Service-Status-Logging

### Ingredients-Routes (/domains/ingredients/routes.py)
- ✅ Strukturiertes Logging für Database-Operationen
- ✅ Performance-Metriken für Paginierung
- ✅ Verbesserte Fehlerbehandlung

### Auth-Routes (/domains/auth/routes.py)
- ✅ Bereits mit strukturiertem Logging implementiert
- ✅ Security-bewusstes Logging ohne sensitive Daten

### Update-Routes (/domains/update/routes.py)
- ✅ Strukturiertes Logging für Cache-Updates
- ✅ Performance-Tracking für Background-Tasks

## Monitoring und Alerting

### Log-Queries für Performance-Monitoring

```json
{
  "query": {
    "bool": {
      "must": [
        { "term": { "level": "INFO" } },
        { "exists": { "field": "data.performance_metrics" } }
      ]
    }
  },
  "aggs": {
    "avg_duration": {
      "avg": { "field": "data.performance_metrics.duration_ms" }
    }
  }
}
```

### Alert-Regeln

1. **Hohe OCR-Verarbeitungszeit**: > 5000ms
2. **Niedrige OCR-Konfidenz**: < 70%
3. **Häufige 500-Fehler**: > 5% der Requests
4. **Lange Database-Queries**: > 1000ms

## Migration bestehender Logs

Alle bestehenden `logger.info()` und `logger.error()` Aufrufe sollten schrittweise auf das neue strukturierte Format migriert werden.

### Beispiel-Migration

**Vorher:**
```python
logger.info(f"User {user_id} logged in successfully")
```

**Nachher:**
```python
logger.info(
    "User login successful",
    context={
        "user_id": user_id,
        "endpoint": "/auth/login",
        "operation": "user_login"
    }
)
```
