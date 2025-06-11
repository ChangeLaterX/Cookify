#!/usr/bin/env python3
"""
🎯 Beispiele für die direkte Verwendung des CookifyTestRunner
Zeigt wie die Test-Methoden direkt mit eigenen Parametern aufgerufen werden können.
"""

from backend.tests.test_runner import CookifyTestRunner

def example_direct_method_calls():
    """Beispiele für direkte Methoden-Aufrufe mit eigenen Parametern."""
    
    # Test Runner erstellen
    runner = CookifyTestRunner()
    
    print("🧪 Beispiele für direkte Test-Runner Verwendung")
    print("=" * 60)
    
    # Beispiel 1: Email Tests mit Coverage und maxfail
    print("\n📧 Beispiel 1: Email-Verifikation Tests mit speziellen Parametern")
    runner.run_email_verification_tests(
        verbose=True,
        coverage=True,
        extra_args=["--maxfail=3", "--tb=long"]
    )
    
    # Beispiel 2: Unit Tests nur quiet
    print("\n🔧 Beispiel 2: Unit Tests (quiet mode)")
    runner.run_unit_tests(
        verbose=False,
        coverage=False
    )
    
    # Beispiel 3: Security Tests mit speziellen pytest Optionen
    print("\n🔒 Beispiel 3: Security Tests mit pytest Optionen")
    runner.run_security_tests(
        verbose=True,
        coverage=False,
        extra_args=["--tb=no", "--disable-warnings"]
    )
    
    # Beispiel 4: Custom Tests mit eigenem Marker
    print("\n🎯 Beispiel 4: Custom Tests mit eigenem Marker")
    runner.run_custom_tests(
        marker="email_verification and unit",
        verbose=True,
        coverage=True,
        extra_args=["--tb=short"]
    )
    
    # Beispiel 5: Performance Tests mit spezieller Konfiguration
    print("\n⚡ Beispiel 5: Performance Tests")
    runner.run_performance_tests(
        verbose=True,
        coverage=False,
        extra_args=["--durations=10"]  # Zeige langsamste 10 Tests
    )

def example_programmatic_usage():
    """Beispiel für programmatische Verwendung in anderen Skripten."""
    
    runner = CookifyTestRunner()
    
    # Verschiedene Test-Szenarien
    test_scenarios = [
        {
            'name': 'Schnelle Tests',
            'method': runner.run_unit_tests,
            'params': {'verbose': False, 'coverage': False}
        },
        {
            'name': 'Email Tests mit Coverage',
            'method': runner.run_email_verification_tests,
            'params': {'verbose': True, 'coverage': True}
        },
        {
            'name': 'Alle Tests mit Stop bei erstem Fehler',
            'method': runner.run_all_auth_tests,
            'params': {
                'verbose': True, 
                'coverage': False,
                'extra_args': ['--maxfail=1']
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🎯 {scenario['name']}")
        result = scenario['method'](**scenario['params'])
        if result == 0:
            print(f"✅ {scenario['name']} erfolgreich")
        else:
            print(f"❌ {scenario['name']} fehlgeschlagen")

def example_custom_configurations():
    """Beispiele für verschiedene Konfigurationen."""
    
    runner = CookifyTestRunner()
    
    # Konfiguration 1: Entwickler-Modus (schnell, nur Fehler)
    print("\n👨‍💻 Entwickler-Modus: Schnelle Tests")
    runner.run_unit_tests(
        verbose=False,
        coverage=False,
        extra_args=["--tb=line", "--quiet"]
    )
    
    # Konfiguration 2: CI/CD-Modus (vollständig mit Coverage)
    print("\n🔄 CI/CD-Modus: Vollständige Tests mit Coverage")
    runner.run_all_auth_tests(
        verbose=True,
        coverage=True,
        extra_args=["--tb=short", "--strict-markers"]
    )
    
    # Konfiguration 3: Debug-Modus (sehr verbose)
    print("\n🐛 Debug-Modus: Detaillierte Ausgabe")
    runner.run_email_verification_tests(
        verbose=True,
        coverage=False,
        extra_args=["--tb=long", "--capture=no", "-s"]
    )
    
    # Konfiguration 4: Performance-Analyse
    print("\n📊 Performance-Analyse")
    runner.run_performance_tests(
        verbose=True,
        coverage=False,
        extra_args=["--durations=0", "--tb=no"]  # Alle Zeiten anzeigen
    )

if __name__ == "__main__":
    print("🧪 CookifyTestRunner - Direkte Methoden-Beispiele")
    print("=" * 60)
    
    # Wähle was ausgeführt werden soll
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "direct":
            example_direct_method_calls()
        elif sys.argv[1] == "programmatic":
            example_programmatic_usage()
        elif sys.argv[1] == "configs":
            example_custom_configurations()
        else:
            print("❌ Unbekannte Option. Verwende: direct, programmatic, oder configs")
    else:
        print("💡 Verwendung:")
        print("  python examples.py direct        # Direkte Methoden-Aufrufe")
        print("  python examples.py programmatic  # Programmatische Verwendung")
        print("  python examples.py configs       # Verschiedene Konfigurationen")
        print("\n📚 Oder importiere CookifyTestRunner in dein eigenes Skript:")
        print("  from test_runner import CookifyTestRunner")
        print("  runner = CookifyTestRunner()")
        print("  runner.run_email_verification_tests(coverage=True, extra_args=['--maxfail=1'])")
