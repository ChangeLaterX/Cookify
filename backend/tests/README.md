# 🧪 Test Architecture Guide

## Überblick

Die Test-Architektur wurde aufgeräumt und ist jetzt modular und domain-spezifisch organisiert.

## Struktur

```
tests/
├── conftest.py              # Globale Fixtures (cross-domain)
├── pytest.ini              # Pytest-Konfiguration
├── run_all_tests.py         # Universeller Test-Runner
├── auth/                    # Auth Domain Tests
│   ├── config.py            # Auth-spezifische Konfiguration
│   ├── fixtures/            # Auth Test-Daten
│   ├── unit/                # Auth Unit Tests
│   ├── integration/         # Auth Integration Tests
│   ├── utils/               # Auth Test-Hilfsmittel
│   └── run_tests.py         # Auth-spezifischer Runner
├── ingredients/             # Ingredients Domain Tests
│   ├── config.py            # Ingredients-spezifische Konfiguration
│   ├── fixtures/            # Ingredients Test-Daten
│   ├── unit/                # Ingredients Unit Tests
│   ├── integration/         # Ingredients Integration Tests
│   ├── utils/               # Ingredients Test-Hilfsmittel
│   └── run_tests.py         # Ingredients-spezifischer Runner
└── ocr/                     # OCR Domain Tests
    ├── config.py            # OCR-spezifische Konfiguration
    ├── fixtures/            # OCR Test-Daten
    ├── unit/                # OCR Unit Tests
    ├── integration/         # OCR Integration Tests
    ├── utils/               # OCR Test-Hilfsmittel
    └── run_tests.py         # OCR-spezifischer Runner
```

## Test-Ausführung

### Universeller Test-Runner

```bash
# Alle Tests ausführen
python tests/run_all_tests.py

# Nur Auth-Tests
python tests/run_all_tests.py --domain auth

# Nur Unit Tests
python tests/run_all_tests.py --type unit

# Auth Unit Tests mit Coverage
python tests/run_all_tests.py --domain auth --type unit --coverage

# Verfügbare Optionen anzeigen
python tests/run_all_tests.py --list
```

### Domain-spezifische Test-Runner

```bash
# Auth Tests
cd tests/auth && python run_tests.py

# Ingredients Tests  
cd tests/ingredients && python run_tests.py

# OCR Tests
cd tests/ocr && python run_tests.py
```

### Direkte Pytest-Aufrufe

```bash
# Alle Tests
pytest tests/

# Spezifische Domain
pytest tests/auth/

# Mit Markern
pytest -m "unit and auth"
pytest -m "integration and ingredients"
pytest -m "not slow"
```

## Fixtures

### Globale Fixtures (conftest.py)
- `test_client` - FastAPI TestClient
- `async_test_client` - Async HTTP Client
- `mock_supabase_client` - Supabase Mock
- `mock_environment_variables` - Umgebungsvariablen Mock
- `auth_headers` - Authorization Headers
- `mock_jwt_token` - JWT Token Mock

### Domain-spezifische Fixtures
Jede Domain hat ihre eigenen Fixtures in `config.py` und `fixtures/`.

## Test-Marker

- `@pytest.mark.unit` - Unit Tests
- `@pytest.mark.integration` - Integration Tests
- `@pytest.mark.auth` - Auth Domain Tests
- `@pytest.mark.ingredients` - Ingredients Domain Tests
- `@pytest.mark.ocr` - OCR Domain Tests
- `@pytest.mark.security` - Security Tests
- `@pytest.mark.slow` - Langsame Tests

## Beispiel Test

```python
import pytest
from tests.auth.config import AuthTestBase
from tests.auth.utils.mocks import with_mocked_auth

class TestUserRegistration(AuthTestBase):
    
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_user_registration(self):
        with with_mocked_auth() as mock_ctx:
            # Test implementation
            pass
```

## Migration von alten Tests

1. ✅ Alte einzelne Test-Dateien entfernt (`auth.py`, `test_ingredients.py`, etc.)
2. ✅ `conftest.py` refactored für cross-domain Fixtures
3. ✅ Universeller Test-Runner erstellt
4. ✅ Pytest-Konfiguration aktualisiert

## Vorteile der neuen Architektur

- 🏗️ **Modularer Aufbau**: Jede Domain hat ihre eigenen Tests
- 🔄 **Wiederverwendbarkeit**: Gemeinsame Fixtures in conftest.py
- 🎯 **Fokussiert**: Domain-spezifische Mocks und Hilfsmittel
- 🚀 **Flexibel**: Verschiedene Test-Runner je nach Bedarf
- 📊 **Coverage**: Integrierte Coverage-Reports
- 🏷️ **Marker**: Einfache Test-Filterung

## Performance Tests

### Konfiguration

Die OCR Performance-Tests verwenden jetzt konfigurierbare Schwellenwerte für verschiedene Umgebungen:

```bash
# Schnelle Konfiguration für verschiedene Umgebungen
./backend/scripts/configure_performance_tests.sh development
./backend/scripts/configure_performance_tests.sh production
./backend/scripts/configure_performance_tests.sh ci

# Aktuelle Konfiguration anzeigen
./backend/scripts/configure_performance_tests.sh show
```

### Manuelle Konfiguration

```bash
# Beispiel für Produktionsumgebung
export OCR_TEST_MAX_AVG_LATENCY_MS=60000        # 60 Sekunden
export OCR_TEST_MAX_E2E_AVG_MS=90000            # 90 Sekunden
export OCR_TEST_MIN_THROUGHPUT_TPS=0.02         # 0.02 tasks/sec

# Performance Tests ausführen
pytest backend/tests/ocr/integration/test_performance.py -v
```

Siehe [Performance Test Configuration Guide](../docs/performance_test_configuration.md) für detaillierte Informationen.

## Standard Test-Ausführung
