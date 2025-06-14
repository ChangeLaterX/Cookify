"""
Beispiel-Service, der die richtige Verwendung des strukturierten Loggers demonstriert.
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

from core.logging import get_logger

# Logger für den Service erstellen
logger = get_logger(__name__)


class ExampleService:
    """
    Ein Beispiel-Service, der verschiedene Logging-Patterns demonstriert.
    Dieser Service ist nur für Demonstrationszwecke gedacht.
    """
    
    def __init__(self):
        # Logger für die Klasse initialisieren
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info("ExampleService initialisiert")
    
    def process_data(self, data_id: UUID, values: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Demonstriert strukturiertes Logging mit Kontext und Messwerten.
        
        Args:
            data_id: ID des Datensatzes
            values: Liste von Werten zur Verarbeitung
            
        Returns:
            Verarbeitete Daten
        """
        self.logger.info(
            "Starte Datenverarbeitung",
            context={"data_id": str(data_id)},
            data={"values_count": len(values)}
        )
        
        start_time = datetime.now()
        
        try:
            # Simuliere Datenverarbeitung
            processed_values = []
            for i, item in enumerate(values):
                # Debug-Logging für einzelne Items mit detailliertem Kontext
                self.logger.debug(
                    f"Verarbeite Item {i+1}/{len(values)}",
                    context={"data_id": str(data_id), "item_index": i},
                    data={"item_type": item.get("type")}
                )
                
                # Simuliere eine Verarbeitung
                processed_item = self._transform_item(item)
                processed_values.append(processed_item)
                
            # Berechne Verarbeitungsdauer
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Erfolgs-Logging mit Performance-Metriken
            result = {
                "id": data_id,
                "processed_count": len(processed_values),
                "status": "success"
            }
            
            self.logger.info(
                "Datenverarbeitung abgeschlossen",
                context={"data_id": str(data_id)},
                data={
                    "duration_ms": round(duration_ms, 2),
                    "items_processed": len(processed_values),
                    "success_rate": "100%"
                }
            )
            
            return result
            
        except Exception as e:
            # Fehlerlogging mit Exception-Details und Kontext
            self.logger.exception(
                "Fehler bei der Datenverarbeitung",
                context={
                    "data_id": str(data_id),
                    "error_type": type(e).__name__
                },
                data={
                    "values_count": len(values)
                }
            )
            raise
    
    def _transform_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Demonstriert granulares Debug-Logging innerhalb einer Methode.
        
        Args:
            item: Zu transformierendes Item
            
        Returns:
            Transformiertes Item
        """
        # Simuliere Verarbeitungslogik
        item_type = item.get("type", "unknown")
        
        if item_type == "critical":
            # Wichtige Warnung mit spezifischem Kontext
            self.logger.warning(
                "Kritisches Item erkannt",
                context={"item_id": item.get("id")},
                data={"critical_factors": item.get("factors", [])}
            )
        
        # Simuliere eine Transformation
        return {
            **item,
            "processed": True,
            "processed_at": datetime.utcnow().isoformat()
        }
    
    def handle_user_action(self, user_id: UUID, action: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """
        Demonstriert Sicherheitsrelevantes Logging für Benutzeraktionen.
        
        Args:
            user_id: ID des Benutzers
            action: Ausgeführte Aktion
            params: Optionale Parameter der Aktion
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        self.logger.info(
            f"Benutzeraktion: {action}",
            context={
                "user_id": str(user_id),
                "action": action,
                "remote_ip": "192.168.1.1"  # In echter Anwendung von Request nehmen
            }
        )
        
        # Sensible Aktionen besonders hervorheben
        if action in ["delete", "admin", "permission_change"]:
            self.logger.warning(
                f"Sensible Benutzeraktion: {action}",
                context={
                    "user_id": str(user_id),
                    "action": action,
                    "security_level": "high"
                },
                data={
                    "params": params,
                    "authorized": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        # Simuliere Erfolg
        return True
    
    def simulate_error_handling(self) -> None:
        """
        Demonstriert verschiedene Fehler-Logging-Szenarien.
        
        Raises:
            ValueError: Für Demonstrationszwecke
        """
        # 1. Standard-Warnung
        self.logger.warning(
            "Potenzielles Problem erkannt",
            context={"subsystem": "data_processor"},
            data={"warning_code": "W123"}
        )
        
        # 2. Fehler ohne Exception
        self.logger.error(
            "Ein Fehler ist aufgetreten, aber wir machen weiter",
            context={"operation": "data_sync"},
            data={"error_details": "Connection timeout"}
        )
        
        # 3. Exception mit vollem Stack-Trace
        try:
            # Simuliere einen Fehler
            value = None
            result = len(value)  # Dies wird einen TypeError verursachen
            return result
        except TypeError as e:
            self.logger.exception(
                "Unerwarteter Fehler bei Werteberechnung",
                context={"calculation_type": "length"}
            )
            # Der Stack-Trace wird automatisch hinzugefügt
        
        # 4. Kritischer Fehler
        self.logger.critical(
            "Kritischer Systemfehler",
            context={
                "subsystem": "database",
                "severity": "high"
            },
            data={
                "connection_pool": "exhausted",
                "retry_count": 5
            }
        )
        
        # 5. Kritischer Fehler mit Exception
        raise ValueError("Simulierter kritischer Fehler für Logging-Demo")


# Beispiel für die Verwendung in Anwendungscode
def example_usage():
    """Demonstriert die Verwendung des ExampleService mit strukturiertem Logging."""
    
    service_logger = get_logger("example_usage")
    service_logger.info("Starte Beispiel-Nutzung des ExampleService")
    
    service = ExampleService()
    
    # Beispieldaten
    import uuid
    data_id = uuid.uuid4()
    values = [
        {"id": "item1", "type": "standard", "value": 42},
        {"id": "item2", "type": "critical", "value": 99, "factors": ["security", "integrity"]},
        {"id": "item3", "type": "standard", "value": 17}
    ]
    
    try:
        result = service.process_data(data_id, values)
        service_logger.info(
            "Datenverarbeitung erfolgreich",
            data={"result": result}
        )
        
        # Benutzeraktion demonstrieren
        user_id = uuid.uuid4()
        service.handle_user_action(user_id, "data_export", {"format": "csv"})
        
        # Fehlerbehandlung demonstrieren (wird eine Exception auslösen)
        try:
            service.simulate_error_handling()
        except ValueError as e:
            service_logger.error(
                "Erwartete ValueError aufgefangen",
                context={"error_message": str(e)}
            )
    
    except Exception as e:
        service_logger.exception("Unbehandelte Ausnahme in example_usage")
        raise
    
    finally:
        service_logger.info("Beispiel-Nutzung des ExampleService beendet")


if __name__ == "__main__":
    # Dieses Skript kann direkt ausgeführt werden, um die Logging-Funktionalität zu testen
    example_usage()
