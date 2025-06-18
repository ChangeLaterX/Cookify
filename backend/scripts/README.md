# Backend Scripts

Dieser Ordner enthält Scripts, die beim Start der FastAPI-Anwendung ausgeführt werden. Die Scripts sind dafür da, Daten zu laden, Caches zu initialisieren und andere Startup-Aufgaben zu erledigen.

## Überblick

### Dateien

- **`__init__.py`** - Package-Initialisierung
- **`startup.py`** - Hauptmanager für Startup-Scripts
- **`ingredient_loader.py`** - Lädt alle Ingredient-Namen aus der Supabase-Datenbank
- **`routes.py`** - API-Endpoints zum Monitoring der Scripts
- **`README.md`** - Diese Dokumentation

## Ingredients Cache

### Zweck

Das `ingredient_loader.py` Script lädt beim Start der Anwendung alle Ingredient-Namen aus der `ingredient_master` Tabelle in Supabase und cached sie im Arbeitsspeicher. Dies ist für die OCR-Erkennung wichtig, damit erkannte Texte gegen bekannte Ingredients abgeglichen werden können.

### Funktionalität

- **Automatisches Laden**: Beim FastAPI-Start werden alle Ingredients geladen
- **Caching**: Daten werden 1 Stunde im Cache gehalten
- **Refresh-Mechanismus**: Cache kann manuell oder automatisch aktualisiert werden
- **OCR-Integration**: Bereit für die Zuordnung von OCR-erkannten Texten

### Hauptfunktionen

```python
# Alle Ingredient-Namen für OCR-Matching abrufen
ingredient_names = get_ingredient_names_for_ocr()

# Suche nach Ingredients in OCR-Text
matches = search_ingredient_matches("tomato chicken breast", max_matches=5)

# Cache-Status prüfen
stats = get_ingredient_cache_stats()

# Cache manuell aktualisieren  
success = await refresh_ingredient_cache()
```

## Startup Manager

### Konzept

Der `StartupScriptManager` verwaltet die Ausführung aller Startup-Scripts:

1. Scripts werden registriert
2. Beim FastAPI-Start werden alle Scripts ausgeführt
3. Ergebnisse werden geloggt und können überwacht werden

### Neue Scripts hinzufügen

1. Script-Funktion erstellen (muss `async` sein und `bool` zurückgeben)
2. In `register_startup_scripts()` registrieren:

```python
def register_startup_scripts() -> None:
    startup_manager.register_script(initialize_ingredient_cache)
    startup_manager.register_script(your_new_script)  # Hier hinzufügen
```

## API Monitoring

### Verfügbare Endpoints

- **`GET /api/scripts/status`** - Status aller Scripts und Caches
- **`GET /api/scripts/ingredients/cache/stats`** - Ingredient-Cache Statistiken
- **`POST /api/scripts/ingredients/cache/refresh`** - Cache manuell aktualisieren
- **`GET /api/scripts/ingredients/names`** - Alle Ingredient-Namen abrufen
- **`GET /api/scripts/ingredients/search?text=...`** - Test-Suche für OCR-Matching

### Beispiel-Responses

```json
// GET /api/scripts/status
{
  "startup_scripts": {
    "total_scripts": 1,
    "successful_scripts": 1,
    "failed_scripts": 0,
    "all_successful": true
  },
  "ingredient_cache": {
    "total_ingredients": 245,
    "last_updated": "2025-06-18T10:30:00",
    "cache_valid": true,
    "cache_duration_hours": 1
  },
  "status": "healthy"
}
```

```json
// GET /api/scripts/ingredients/search?text=chicken tomato rice
{
  "search_text": "chicken tomato rice",
  "max_matches": 5,
  "found_matches": 3,
  "matches": [
    "Chicken Breast",
    "Tomato",
    "Brown Rice"
  ]
}
```

## Für OCR-Integration

### Später verwenden

Wenn die OCR-Zuordnung implementiert wird, können diese Funktionen verwendet werden:

```python
from scripts.ingredient_loader import (
    get_ingredient_names_for_ocr,
    search_ingredient_matches
)

# In OCR-Service:
def match_ocr_to_ingredients(ocr_text: str) -> List[str]:
    # Alle bekannten Ingredients abrufen
    known_ingredients = get_ingredient_names_for_ocr()
    
    # Oder direkte Suche verwenden
    matches = search_ingredient_matches(ocr_text, max_matches=10)
    
    return matches
```

### Cache-Management

Der Cache wird automatisch verwaltet:
- Lädt beim Start
- Prüft Gültigkeit vor Zugriff
- Kann manuell aktualisiert werden
- Läuft nach 1 Stunde ab

## Logging

Alle Script-Aktivitäten werden geloggt:
- Startup-Erfolg/Fehler
- Cache-Operationen
- Datenbankzugriffe
- Performance-Metriken

## Fehlerbehandlung

- Scripts können einzeln fehlschlagen ohne die gesamte Anwendung zu stoppen
- Fehler werden geloggt aber nicht fatal
- Cache-Fehler führen zu Warnings, nicht zu Crashes
- Fallback-Mechanismen für kritische Operationen

## Nächste Schritte

1. **OCR-Integration**: Die geladenen Ingredient-Namen in den OCR-Service einbinden
2. **Fuzzy-Matching**: Erweiterte String-Matching-Algorithmen implementieren
3. **Performance-Optimierung**: Cache-Strategien verfeinern
4. **Weitere Caches**: Ähnliche Scripts für andere Datentypen erstellen
