#!/usr/bin/env python3
"""
🧪 Cookify Test Runner
Einfaches Skript zum Ausführen von Tests mit einem Befehl.
"""

import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path


class CookifyTestRunner:
    """Cookify Test Runner mit separaten Methoden für jede Test-Kategorie."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.test_file = "tests/test_auth_complete.py"
        self.start_time = None
        self.end_time = None
    
    def _build_base_command(self, verbose=True, coverage=False, marker=None, extra_args=None):
        """Erstelle den Basis-pytest-Befehl."""
        cmd = [
            "python", "-m", "pytest", 
            self.test_file,
            "-v" if verbose else "-q",
            "--tb=short",
            "--color=yes"
        ]
        
        # Marker hinzufügen
        if marker:
            cmd.extend(["-m", marker])
        
        # Coverage hinzufügen
        if coverage:
            cmd.extend([
                "--cov=domains.auth",
                "--cov-report=term",
                "--cov-report=html"
            ])
        
        # Zusätzliche Argumente
        if extra_args:
            cmd.extend(extra_args)
        
        return cmd
    
    def _execute_tests(self, cmd, test_description, coverage=False):
        """Führe Tests aus und zeige Ergebnisse an."""
        self._print_header(test_description, cmd)
        
        self.start_time = datetime.now()
        result = subprocess.run(cmd, cwd=self.base_path)
        self.end_time = datetime.now()
        
        self._print_footer(result.returncode, coverage)
        return result.returncode
    
    def _print_header(self, test_description, cmd):
        """Drucke Test-Header."""
        print(f"🎯 Fokus: {test_description}")
        print("🚀 Starte Cookify Auth Tests...")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        cmd_str = " ".join(cmd)
        print(f"📝 Ausführung: {cmd_str}")
        print("=" * 70)
    
    def _print_footer(self, return_code, coverage=False):
        """Drucke Test-Footer mit Ergebnissen."""
        print("=" * 70)
        if self.end_time:
            print(f"📅 Beendet: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if return_code == 0:
            print("✅ Alle Auth-Tests erfolgreich bestanden!")
            if coverage:
                print("📊 Coverage-Report verfügbar unter: htmlcov/index.html")
            print("\n🎯 Test-Kategorien:")
            print("  • Unit Tests: AuthService, Schemas, Models")
            print("  • Email Verification: Registrierung → Verifikation → Login")
            print("  • Integration: API Routes und Endpoints")
            print("  • Security: SQL Injection, XSS, Rate Limiting")
            print("  • Performance: Response Times, Memory, Concurrency")
        else:
            print("❌ Einige Tests sind fehlgeschlagen!")
            print("💡 Tipp: Überprüfe die Ausgabe oben für Details.")
    
    def run_all_auth_tests(self, **kwargs):
        """Führe alle Authentication Tests aus.
        
        Args:
            verbose (bool): Verbose Ausgabe (default: True)
            coverage (bool): Coverage Report (default: False)
            extra_args (list): Zusätzliche pytest Argumente
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        cmd = self._build_base_command(verbose=verbose, coverage=coverage, extra_args=extra_args)
        return self._execute_tests(cmd, "Alle Auth-Tests", coverage)
    
    def run_email_verification_tests(self, **kwargs):
        """Führe nur Email-Verifikation Tests aus.
        
        Args:
            verbose (bool): Verbose Ausgabe (default: True)
            coverage (bool): Coverage Report (default: False)
            extra_args (list): Zusätzliche pytest Argumente
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        cmd = self._build_base_command(
            verbose=verbose, 
            coverage=coverage, 
            marker="email_verification",
            extra_args=extra_args
        )
        return self._execute_tests(cmd, "Email-Verifikation Tests", coverage)
    
    def run_unit_tests(self, **kwargs):
        """Führe nur Unit Tests aus.
        
        Args:
            verbose (bool): Verbose Ausgabe (default: True)
            coverage (bool): Coverage Report (default: False)
            extra_args (list): Zusätzliche pytest Argumente
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        cmd = self._build_base_command(
            verbose=verbose, 
            coverage=coverage, 
            marker="unit",
            extra_args=extra_args
        )
        return self._execute_tests(cmd, "Unit Tests", coverage)
    
    def run_integration_tests(self, **kwargs):
        """Führe nur Integration Tests aus.
        
        Args:
            verbose (bool): Verbose Ausgabe (default: True)
            coverage (bool): Coverage Report (default: False)
            extra_args (list): Zusätzliche pytest Argumente
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        cmd = self._build_base_command(
            verbose=verbose, 
            coverage=coverage, 
            marker="integration",
            extra_args=extra_args
        )
        return self._execute_tests(cmd, "Integration Tests", coverage)
    
    def run_security_tests(self, **kwargs):
        """Führe nur Security Tests aus.
        
        Args:
            verbose (bool): Verbose Ausgabe (default: True)
            coverage (bool): Coverage Report (default: False)
            extra_args (list): Zusätzliche pytest Argumente
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        cmd = self._build_base_command(
            verbose=verbose, 
            coverage=coverage, 
            marker="security",
            extra_args=extra_args
        )
        return self._execute_tests(cmd, "Security Tests", coverage)
    
    def run_performance_tests(self, **kwargs):
        """Führe nur Performance Tests aus.
        
        Args:
            verbose (bool): Verbose Ausgabe (default: True)
            coverage (bool): Coverage Report (default: False)
            extra_args (list): Zusätzliche pytest Argumente
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        cmd = self._build_base_command(
            verbose=verbose, 
            coverage=coverage, 
            marker="slow",
            extra_args=extra_args
        )
        return self._execute_tests(cmd, "Performance Tests", coverage)
    
    def run_custom_tests(self, marker=None, **kwargs):
        """Führe Tests mit benutzerdefinierten Parametern aus.
        
        Args:
            marker (str): Pytest Marker (z.B. "email_verification", "unit")
            verbose (bool): Verbose Ausgabe (default: True)
            coverage (bool): Coverage Report (default: False)
            extra_args (list): Zusätzliche pytest Argumente
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        description = f"Custom Tests" + (f" (Marker: {marker})" if marker else "")
        
        cmd = self._build_base_command(
            verbose=verbose, 
            coverage=coverage, 
            marker=marker,
            extra_args=extra_args
        )
        return self._execute_tests(cmd, description, coverage)
    
    # =============================================================================
    # AUTH ENDPOINT-SPEZIFISCHE TESTS
    # =============================================================================
    
    def run_login_tests(self, **kwargs):
        """Führe nur Login-bezogene Tests aus.
        
        Tests: authenticate_user, login endpoints, invalid credentials
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        # Spezifische Test-Namen für Login-Funktionalität
        login_tests = [
            "test_authenticate_user_success",
            "test_login_endpoint_success", 
            "test_login_endpoint_invalid_credentials",
            "test_login_before_email_verification"
        ]
        
        # Test-spezifische Argumente hinzufügen
        test_args = []
        for test in login_tests:
            test_args.extend(["-k", test])
        
        # Verbinde alle Test-Namen mit OR
        test_filter = " or ".join([f"test_name.endswith('{test}')" for test in login_tests])
        extra_args.extend(["-k", test_filter])
        
        cmd = self._build_base_command(
            verbose=verbose,
            coverage=coverage,
            extra_args=extra_args
        )
        return self._execute_tests(cmd, "Login Tests", coverage)
    
    def run_register_tests(self, **kwargs):
        """Führe nur Registrierungs-bezogene Tests aus.
        
        Tests: register_user, registration endpoints
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        register_filter = "register"
        extra_args.extend(["-k", register_filter])
        
        cmd = self._build_base_command(
            verbose=verbose,
            coverage=coverage,
            extra_args=extra_args
        )
        return self._execute_tests(cmd, "Registration Tests", coverage)
    
    def run_verify_tests(self, **kwargs):
        """Führe nur Email-Verifikations-bezogene Tests aus.
        
        Tests: verify_email, verification endpoints, resend verification
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        verify_filter = "verify"
        extra_args.extend(["-k", verify_filter])
        
        cmd = self._build_base_command(
            verbose=verbose,
            coverage=coverage,
            extra_args=extra_args
        )
        return self._execute_tests(cmd, "Email Verification Tests", coverage)
    
    def run_password_tests(self, **kwargs):
        """Führe nur Password-bezogene Tests aus.
        
        Tests: password reset, password security, password validation
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        password_filter = "password"
        extra_args.extend(["-k", password_filter])
        
        cmd = self._build_base_command(
            verbose=verbose,
            coverage=coverage,
            extra_args=extra_args
        )
        return self._execute_tests(cmd, "Password Tests", coverage)
    
    def run_token_tests(self, **kwargs):
        """Führe nur Token-bezogene Tests aus.
        
        Tests: token generation, token validation, refresh tokens
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        token_filter = "token"
        extra_args.extend(["-k", token_filter])
        
        cmd = self._build_base_command(
            verbose=verbose,
            coverage=coverage,
            extra_args=extra_args
        )
        return self._execute_tests(cmd, "Token Tests", coverage)
    
    def run_logout_tests(self, **kwargs):
        """Führe nur Logout-bezogene Tests aus.
        
        Tests: logout functionality, session cleanup
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        logout_filter = "logout"
        extra_args.extend(["-k", logout_filter])
        
        cmd = self._build_base_command(
            verbose=verbose,
            coverage=coverage,
            extra_args=extra_args
        )
        return self._execute_tests(cmd, "Logout Tests", coverage)
    
    def run_schema_tests(self, **kwargs):
        """Führe nur Schema-Validierungs Tests aus.
        
        Tests: Pydantic schema validation, input validation
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        schema_filter = "schema"
        extra_args.extend(["-k", schema_filter])
        
        cmd = self._build_base_command(
            verbose=verbose,
            coverage=coverage,
            extra_args=extra_args
        )
        return self._execute_tests(cmd, "Schema Validation Tests", coverage)
    
    def run_endpoint_tests(self, **kwargs):
        """Führe nur API Endpoint Tests aus.
        
        Tests: HTTP endpoints, route testing
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        endpoint_filter = "endpoint"
        extra_args.extend(["-k", endpoint_filter])
        
        cmd = self._build_base_command(
            verbose=verbose,
            coverage=coverage,
            extra_args=extra_args
        )
        return self._execute_tests(cmd, "API Endpoint Tests", coverage)


def main():
    parser = argparse.ArgumentParser(
        description='🧪 Cookify Test Runner - Einfache Test-Ausführung',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python test_runner.py --auth                    # Alle Auth-Tests
  python test_runner.py --auth --coverage         # Mit Coverage-Report
  python test_runner.py --auth --email            # Nur Email-Verifikation
  python test_runner.py --auth --unit             # Nur Unit Tests
  python test_runner.py --auth --security         # Nur Security Tests
  
Endpoint-spezifische Tests:
  python test_runner.py --auth --login            # Nur Login Tests
  python test_runner.py --auth --register         # Nur Registration Tests
  python test_runner.py --auth --verify           # Nur Email-Verifikation Tests
  python test_runner.py --auth --password         # Nur Password Tests
  python test_runner.py --auth --token            # Nur Token Tests
  python test_runner.py --auth --logout           # Nur Logout Tests
  python test_runner.py --auth --schema           # Nur Schema Tests
  python test_runner.py --auth --endpoint         # Nur API Endpoint Tests
  
Direkte Methoden-Aufrufe (programmatisch):
  runner = CookifyTestRunner()
  runner.run_email_verification_tests(verbose=True, coverage=True)
  runner.run_login_tests(extra_args=["--maxfail=1"])
        """
    )
    
    # Haupt-Optionen
    parser.add_argument('--auth', action='store_true', 
                       help='🎯 Alle Authentication Tests ausführen')
    
    # Test-Kategorien
    parser.add_argument('--email', action='store_true',
                       help='📧 Nur Email-Verifikation Tests')
    parser.add_argument('--unit', action='store_true',
                       help='🔧 Nur Unit Tests')
    parser.add_argument('--integration', action='store_true',
                       help='🔗 Nur Integration Tests')
    parser.add_argument('--security', action='store_true',
                       help='🔒 Nur Security Tests')
    parser.add_argument('--performance', action='store_true',
                       help='⚡ Nur Performance Tests')
    
    # Endpoint-spezifische Tests
    parser.add_argument('--login', action='store_true',
                       help='🔑 Nur Login Tests')
    parser.add_argument('--register', action='store_true',
                       help='📝 Nur Registration Tests')
    parser.add_argument('--verify', action='store_true',
                       help='✅ Nur Email-Verifikation Tests')
    parser.add_argument('--password', action='store_true',
                       help='🔐 Nur Password Tests')
    parser.add_argument('--token', action='store_true',
                       help='🎫 Nur Token Tests')
    parser.add_argument('--logout', action='store_true',
                       help='🚪 Nur Logout Tests')
    parser.add_argument('--schema', action='store_true',
                       help='📋 Nur Schema Validation Tests')
    parser.add_argument('--endpoint', action='store_true',
                       help='🌐 Nur API Endpoint Tests')
    
    # Zusätzliche Optionen
    parser.add_argument('--coverage', action='store_true',
                       help='📊 Coverage-Report generieren')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='🤫 Weniger verbose Ausgabe')
    parser.add_argument('--maxfail', type=int,
                       help='🛑 Stoppe nach N Fehlern')
    parser.add_argument('--marker', type=str,
                       help='🏷️ Benutzerdefinierten Marker verwenden')
    
    args = parser.parse_args()
    
    # Prüfen ob --auth angegeben wurde
    if not args.auth:
        print("❌ Fehler: --auth Parameter erforderlich!")
        print("💡 Verwendung: python test_runner.py --auth")
        print("📖 Für Hilfe: python test_runner.py --help")
        return 1
    
    # Test Runner erstellen
    runner = CookifyTestRunner()
    
    # Parameter für alle Methoden vorbereiten
    test_kwargs = {
        'verbose': not args.quiet,
        'coverage': args.coverage,
        'extra_args': []
    }
    
    # Zusätzliche pytest-Argumente
    if args.maxfail:
        test_kwargs['extra_args'].append(f"--maxfail={args.maxfail}")
    
    # Bestimme welche Test-Methode aufgerufen werden soll
    # Zuerst prüfen: Endpoint-spezifische Tests
    if args.login:
        return runner.run_login_tests(**test_kwargs)
    elif args.register:
        return runner.run_register_tests(**test_kwargs)
    elif args.verify:
        return runner.run_verify_tests(**test_kwargs)
    elif args.password:
        return runner.run_password_tests(**test_kwargs)
    elif args.token:
        return runner.run_token_tests(**test_kwargs)
    elif args.logout:
        return runner.run_logout_tests(**test_kwargs)
    elif args.schema:
        return runner.run_schema_tests(**test_kwargs)
    elif args.endpoint:
        return runner.run_endpoint_tests(**test_kwargs)
    
    # Dann: Test-Kategorien
    elif args.marker:
        # Benutzerdefinierter Marker
        return runner.run_custom_tests(marker=args.marker, **test_kwargs)
    elif args.email:
        return runner.run_email_verification_tests(**test_kwargs)
    elif args.unit:
        return runner.run_unit_tests(**test_kwargs)
    elif args.integration:
        return runner.run_integration_tests(**test_kwargs)
    elif args.security:
        return runner.run_security_tests(**test_kwargs)
    elif args.performance:
        return runner.run_performance_tests(**test_kwargs)
    else:
        return runner.run_all_auth_tests(**test_kwargs)


if __name__ == "__main__":
    sys.exit(main())
