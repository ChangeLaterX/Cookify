# Logging Guide für Cookify Backend

## Übersicht

Das Cookify-Backend verwendet ein erweitertes, strukturiertes Logging-System, das auf dem Python-Standard `logging`-Modul aufbaut. Das System bietet folgende Funktionen:

- Strukturierte Logs mit einheitlichem Format (Text oder JSON)
- Kontext-basiertes Logging für bessere Nachvollziehbarkeit
- Automatische Anreicherung von Logs mit Metadaten
- Leistungsoptimierung durch Caching von Logger-Instanzen
- Konfigurierbare Log-Level für verschiedene Anwendungsteile
- Unterstützung für Datei- und Konsolen-Logging

## Logger verwenden

### Logger abrufen

Verwende immer die `get_logger`-Funktion, um einen Logger zu erhalten:

```python
from core.logging import get_logger

# Typischerweise mit __name__ aufrufen, um den Modulnamen zu verwenden
logger = get_logger(__name__)

# Oder mit einem benutzerdefinierten Namen
logger = get_logger("custom.name")
```

### Logging mit verschiedenen Ebenen

```python
# Grundlegende Logging-Ebenen
logger.trace("Sehr detaillierte Debug-Informationen")
logger.debug("Debug-Informationen für Entwickler")
logger.info("Allgemeine Informationen über Anwendungsabläufe")
logger.warning("Warnung, die Aufmerksamkeit erfordert")
logger.error("Fehler, der die Funktionalität beeinträchtigt")
logger.critical("Kritischer Fehler, der sofortiges Handeln erfordert")

# Für Exceptions mit automatischem Stacktrace
try:
    # Code, der fehlschlagen könnte
    raise ValueError("Beispiel-Exception")
except Exception as e:
    logger.exception("Eine Exception ist aufgetreten")
```

### Strukturiertes Logging mit Kontext

```python
# Logging mit zusätzlichem Kontext
logger.info(
    "Benutzer hat sich angemeldet", 
    context={
        "user_id": "abc123",
        "ip_address": "192.168.1.1"
    }
)

# Logging mit Kontext und strukturierten Daten
logger.info(
    "Bestellung abgeschlossen", 
    context={"user_id": "abc123"}, 
    data={
        "order_id": "order-123",
        "items_count": 5,
        "total_price": 49.99
    }
)
```

## Best Practices

### Log-Ebenen richtig verwenden

- **TRACE**: Sehr detaillierte Informationen, nur für tiefgreifende Debugging-Zwecke
- **DEBUG**: Detailinformationen für Entwickler während der Entwicklung und zum Debuggen
- **INFO**: Allgemeine Informationen über normale Anwendungsabläufe
- **WARNING**: Potenziell problematische Situationen, die Aufmerksamkeit erfordern
- **ERROR**: Fehler, die eine Operation verhindern, aber die Anwendung läuft weiter
- **CRITICAL**: Kritische Fehler, die die Anwendung möglicherweise beenden

### Strukturierte Logs für maschinelle Verarbeitung

Verwende immer den `context` und `data` Parameter für strukturierte Informationen statt sie in die Nachricht einzubauen:

```python
# NICHT SO:
logger.info(f"User {user_id} hat {items_count} Artikel für {total_price}€ bestellt")

# BESSER SO:
logger.info(
    "Bestellung abgeschlossen",
    context={"user_id": user_id},
    data={"items_count": items_count, "total_price": total_price}
)
```

### Persönliche Daten schützen

- Logge niemals Passwörter, Tokens oder andere vertrauliche Informationen
- Beschränke personenbezogene Daten auf das Nötigste, speziell bei höheren Log-Ebenen
- Kürze lange persönliche Identifikatoren bei Bedarf (z.B. "user@exa...com")

### Performance-Optimierung

Bei umfangreichen oder komplexen Log-Nachrichten, prüfe vorher ob das entsprechende Log-Level aktiviert ist:

```python
if logger.isEnabledFor(logging.DEBUG):
    complex_debug_info = generate_expensive_debug_info()
    logger.debug("Komplexe Debug-Info", data=complex_debug_info)
```

## Konfiguration

Die Logging-Konfiguration wird in `core/config.py` definiert und kann über Umgebungsvariablen angepasst werden:

- `LOG_LEVEL`: Allgemeines Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FORMAT_JSON`: True für JSON-Format, False für Text-Format
- `LOG_TO_FILE`: True um Logs in Dateien zu schreiben
- `LOG_DIR`: Verzeichnis für Log-Dateien
- `CONSOLE_LOG_LEVEL`: Log-Level für Konsolenausgaben
- `DOMAINS_LOG_LEVEL`: Log-Level für Domain-Module
- `MIDDLEWARE_LOG_LEVEL`: Log-Level für Middleware-Module

## Beispiele für typische Logging-Muster

### Authentifizierung und Sicherheit

```python
# Erfolgreiche Anmeldung
logger.info(
    "Benutzer angemeldet",
    context={"user_id": user.id, "ip_address": client_ip}
)

# Fehlgeschlagene Anmeldung
logger.warning(
    "Anmeldung fehlgeschlagen",
    context={
        "username": username,  # E-Mail nicht vollständig loggen
        "ip_address": client_ip,
        "attempt_count": attempt_count
    }
)

# Sicherheitsrelevantes Ereignis
logger.error(
    "Rate-Limit überschritten",
    context={
        "ip_address": client_ip,
        "endpoint": request.url.path,
        "violations_count": violations_count
    }
)
```

### API-Anfragen und Leistung

```python
# API-Anfrage mit Dauer
logger.info(
    "API-Anfrage verarbeitet",
    context={
        "endpoint": request.url.path,
        "method": request.method,
        "duration_ms": duration_ms,
        "status_code": response.status_code
    }
)

# Datenbankoperationen
logger.debug(
    "Datenbankabfrage ausgeführt",
    context={"table": "users", "operation": "SELECT"},
    data={"query_duration_ms": query_time, "results_count": len(results)}
)
```

### Fehlerbehandlung

```python
try:
    # Operation durchführen
    result = perform_operation()
    return result
except ValueError as e:
    # Bekannter Fehlerfall
    logger.warning(
        "Ungültige Eingabedaten",
        context={"operation": "perform_operation"},
        data={"validation_errors": str(e)}
    )
    raise
except Exception as e:
    # Unerwarteter Fehler
    logger.exception(
        "Unerwarteter Fehler bei Operation",
        context={"operation": "perform_operation"}
    )
    # Exception wird automatisch mit Stack-Trace geloggt
    raise
```

## Logging-Konfiguration in der Entwicklung

Für die lokale Entwicklung empfehlen wir:

```
LOG_LEVEL=DEBUG
LOG_FORMAT_JSON=False
LOG_TO_FILE=False
```

## Logging-Konfiguration in Produktion

Für Produktionsumgebungen empfehlen wir:

```
LOG_LEVEL=INFO
LOG_FORMAT_JSON=True
LOG_TO_FILE=True
LOG_DIR=/var/log/cookify
```
