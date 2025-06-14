"""
Beispiel für Unit-Tests mit richtigem Logger-Setup und Mocking.
"""
import logging
import pytest
import uuid
from unittest.mock import patch, MagicMock

# Import der zu testenden Funktionen
from examples.logging_example import ExampleService

# Patches für das Logging-System
@pytest.fixture
def mock_logger():
    """Mock-Logger für Tests."""
    with patch('core.logging.get_logger') as mock:
        # Mock-Logger einrichten
        logger_instance = MagicMock()
        mock.return_value = logger_instance
        yield logger_instance


class TestExampleService:
    """Tests für ExampleService mit Mock-Logger."""
    
    def test_initialization_logs_correctly(self, mock_logger):
        """Test, dass der Service seine Initialisierung korrekt loggt."""
        # Service initialisieren
        service = ExampleService()
        
        # Überprüfen, dass die Info-Meldung geloggt wurde
        mock_logger.info.assert_called_with("ExampleService initialisiert")
    
    def test_process_data_logs_start_and_completion(self, mock_logger):
        """Test, dass die Datenverarbeitung Start und Ende korrekt loggt."""
        # Testdaten
        data_id = uuid.uuid4()
        values = [{"id": "test1", "type": "standard", "value": 42}]
        
        # Service initialisieren und Methode aufrufen
        service = ExampleService()
        result = service.process_data(data_id, values)
        
        # Überprüfen, dass die Info-Meldungen geloggt wurden
        mock_logger.info.assert_any_call(
            "Starte Datenverarbeitung",
            context={"data_id": str(data_id)},
            data={"values_count": 1}
        )
        
        # Überprüfen, dass auch die Abschlussmeldung geloggt wurde
        assert any(
            call[0][0] == "Datenverarbeitung abgeschlossen" 
            for call in mock_logger.info.call_args_list
        )
    
    def test_error_logging_captures_exception(self, mock_logger):
        """Test, dass Fehler korrekt geloggt werden."""
        service = ExampleService()
        
        # Eine Exception auslösen und abfangen
        try:
            service.simulate_error_handling()
            pytest.fail("Eine Exception sollte ausgelöst werden")
        except ValueError:
            # Überprüfen, dass exception aufgerufen wurde
            assert mock_logger.exception.called
            # Überprüfen, dass critical aufgerufen wurde
            assert mock_logger.critical.called
    
    def test_sensitive_user_action_logs_warning(self, mock_logger):
        """Test, dass sensible Benutzeraktionen als Warnung geloggt werden."""
        service = ExampleService()
        user_id = uuid.uuid4()
        
        # Eine sensible Aktion ausführen
        service.handle_user_action(user_id, "delete", {"target_id": "123"})
        
        # Überprüfen, dass warning aufgerufen wurde
        mock_logger.warning.assert_called_with(
            "Sensible Benutzeraktion: delete",
            context={
                "user_id": str(user_id),
                "action": "delete",
                "security_level": "high"
            },
            data={
                "params": {"target_id": "123"},
                "authorized": True,
                "timestamp": mock_logger.warning.call_args[1]["data"]["timestamp"]
            }
        )
