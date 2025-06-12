#!/usr/bin/env python3
"""
🧪 Cookify Test Runner
A simple script to execute tests with a single command.
"""

import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class CookifyTestRunner:
    """Cookify Test Runner with separate methods for each test category."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.test_file = None  # Default to None, will be set dynamically
        self.start_time = None
        self.end_time = None
    
    def _build_base_command(self, verbose=True, coverage=False, marker=None, extra_args=None, test_path=None):
        """Build the base pytest command."""
        test_path = test_path or self.test_file or "tests/**/*.py"  # Default to glob pattern
        cmd = [
            "python", "-m", "pytest", 
            test_path,
            "-v" if verbose else "-q",
            "--tb=short",
            "--color=yes"
        ]
        
        # Add marker
        if marker:
            cmd.extend(["-m", marker])
        
        # Add coverage
        if coverage:
            cmd.extend([
                "--cov=domains.auth",
                "--cov-report=term",
                "--cov-report=html"
            ])
        
        # Additional arguments
        if extra_args:
            cmd.extend(extra_args)
        
        return cmd
    
    def _execute_tests(self, cmd, test_description, coverage=False):
        """Execute tests and show results."""
        self._print_header(test_description, cmd)
        
        self.start_time = datetime.now()
        result = subprocess.run(cmd, cwd=self.base_path)
        self.end_time = datetime.now()
        
        self._print_footer(result.returncode, coverage)
        return result.returncode
    
    def _print_header(self, test_description, cmd):
        """Print test header."""
        logger.info(f"🎯 Focus: {test_description}")
        logger.info(f"🚀 Starting {test_description}...")
        logger.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)
        
        cmd_str = " ".join(cmd)
        logger.info(f"📝 Execution: {cmd_str}")
        logger.info("=" * 70)
    
    def _print_footer(self, return_code, coverage=False):
        """Print test footer with results."""
        logger.info("=" * 70)
        if self.end_time:
            logger.info(f"📅 Finished: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")

        if return_code == 0:
            logger.info("✅ All Auth Tests passed successfully!")
            if coverage:
                logger.info("📊 Coverage report available at: htmlcov/index.html")
            logger.info("\n🎯 Test Categories:")
            logger.info("  • Unit Tests: AuthService, Schemas, Models")
            logger.info("  • Email Verification: Registration → Verification → Login")
            logger.info("  • Integration: API Routes and Endpoints")
            logger.info("  • Security: SQL Injection, XSS, Rate Limiting")
            logger.info("  • Performance: Response Times, Memory, Concurrency")
        else:
            logger.info("❌ Some tests failed!")
            logger.info(f"💡 Tip: Check the output above for details.")
    
    def run_all_auth_tests(self, **kwargs):
        """Execute all Authentication Tests.
        
        Args:
            verbose (bool): Verbose output (default: True)
            coverage (bool): Coverage Report (default: False)
            extra_args (list): Additional pytest arguments
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        cmd = self._build_base_command(verbose=verbose, coverage=coverage, extra_args=extra_args)
        return self._execute_tests(cmd, "All Auth Tests", coverage)
    
    def run_email_verification_tests(self, **kwargs):
        """Run only Email Verification Tests.
        
        Args:
            verbose (bool): Verbose output (default: True)
            coverage (bool): Coverage Report (default: False)
            extra_args (list): Additional pytest arguments
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
        return self._execute_tests(cmd, "Email Verification Tests", coverage)
    
    def run_unit_tests(self, **kwargs):
        """Run only Unit Tests.
        
        Args:
            verbose (bool): Verbose output (default: True)
            coverage (bool): Coverage Report (default: False)
            extra_args (list): Additional pytest arguments
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
        """Run only Integration Tests.
        
        Args:
            verbose (bool): Verbose output (default: True)
            coverage (bool): Coverage Report (default: False)
            extra_args (list): Additional pytest arguments
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
        """Run only Security Tests.
        
        Args:
            verbose (bool): Verbose output (default: True)
            coverage (bool): Coverage Report (default: False)
            extra_args (list): Additional pytest arguments
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
        """Run only Performance Tests.
        
        Args:
            verbose (bool): Verbose output (default: True)
            coverage (bool): Coverage Report (default: False)
            extra_args (list): Additional pytest arguments
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
        """Execute tests with custom parameters.
        
        Args:
            marker (str): Pytest marker (e.g. "email_verification", "unit")
            verbose (bool): Verbose output (default: True)
            coverage (bool): Coverage Report (default: False)
            extra_args (list): Additional pytest arguments
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
    # AUTH ENDPOINT-SPECIFIC TESTS
    # =============================================================================
    
    def run_login_tests(self, **kwargs):
        """Execute only Login-related tests.
        
        Tests: authenticate_user, login endpoints, invalid credentials
        """
        verbose = kwargs.get('verbose', True)
        coverage = kwargs.get('coverage', False)
        extra_args = kwargs.get('extra_args', [])
        
        # Specific test names for login functionality
        login_tests = [
            "test_authenticate_user_success",
            "test_login_endpoint_success", 
            "test_login_endpoint_invalid_credentials",
            "test_login_before_email_verification"
        ]
        
        # Add test-specific arguments
        test_args = []
        for test in login_tests:
            test_args.extend(["-k", test])
        
        # Connect all test names with OR
        test_filter = " or ".join(login_tests)
        extra_args.extend(["-k", test_filter])
        
        cmd = self._build_base_command(
            verbose=verbose,
            coverage=coverage,
            extra_args=extra_args
        )
        return self._execute_tests(cmd, "Login Tests", coverage)
    
    def run_register_tests(self, **kwargs):
        """Execute only Registration-related tests.
        
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
        """Execute only Email Verification-related tests.
        
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
        """Execute only Password-related tests.
        
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
        """Execute only Token-related tests.
        
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
        """Execute only Logout-related tests.
        
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
        """Execute only Schema Validation tests.
        
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
        """Execute only API Endpoint tests.
        
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
        description='🧪 Cookify Test Runner - Simple Test Execution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py --auth                    # All Auth Tests
  python test_runner.py --auth --coverage         # With Coverage Report
  python test_runner.py --auth --email            # Only Email Verification
  python test_runner.py --auth --unit             # Only Unit Tests
  python test_runner.py --auth --security         # Only Security Tests
  
Endpoint-specific Tests:
  python test_runner.py --auth --login            # Only Login Tests
  python test_runner.py --auth --register         # Only Registration Tests
  python test_runner.py --auth --verify           # Only Email Verification Tests
  python test_runner.py --auth --password         # Only Password Tests
  python test_runner.py --auth --token            # Only Token Tests
  python test_runner.py --auth --logout           # Only Logout Tests
  python test_runner.py --auth --schema           # Only Schema Tests
  python test_runner.py --auth --endpoint         # Only API Endpoint Tests
  
Direct Method Calls (programmatic):
  runner = CookifyTestRunner()
  runner.run_email_verification_tests(verbose=True, coverage=True)
  runner.run_login_tests(extra_args=["--maxfail=1"])
        """
    )
    
    # Main Options
    parser.add_argument('--test-path', type=str, 
                       help='📂 Path to specific tests or test directory (e.g. tests/test_auth.py)')
    parser.add_argument('--auth', action='store_true', 
                       help='🎯 Execute all Authentication Tests')
    
    # Test Categories
    parser.add_argument('--email', action='store_true',
                       help='📧 Only Email Verification Tests')
    parser.add_argument('--unit', action='store_true',
                       help='🔧 Only Unit Tests')
    parser.add_argument('--integration', action='store_true',
                       help='🔗 Only Integration Tests')
    parser.add_argument('--security', action='store_true',
                       help='🔒 Only Security Tests')
    parser.add_argument('--performance', action='store_true',
                       help='⚡ Only Performance Tests')
    
    # Endpoint-specific Tests
    parser.add_argument('--login', action='store_true',
                       help='🔑 Only Login Tests')
    parser.add_argument('--register', action='store_true',
                       help='📝 Only Registration Tests')
    parser.add_argument('--verify', action='store_true',
                       help='✅ Only Email Verification Tests')
    parser.add_argument('--password', action='store_true',
                       help='🔐 Only Password Tests')
    parser.add_argument('--token', action='store_true',
                       help='🎫 Only Token Tests')
    parser.add_argument('--logout', action='store_true',
                       help='🚪 Only Logout Tests')
    parser.add_argument('--schema', action='store_true',
                       help='📋 Only Schema Validation Tests')
    parser.add_argument('--endpoint', action='store_true',
                       help='🌐 Only API Endpoint Tests')
    
    # Additional Options
    parser.add_argument('--coverage', action='store_true',
                       help='📊 Generate Coverage Report')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='🤫 Less verbose output')
    parser.add_argument('--maxfail', type=int,
                       help='🛑 Stop after N failures')
    parser.add_argument('--marker', type=str,
                       help='🏷️ Use custom marker')
    
    args = parser.parse_args()
    
    # Check if --auth was specified
    if not args.auth:
        logger.info("❌ Error: --auth parameter required!")
        logger.info("💡 Usage: python test_runner.py --auth")
        logger.info("📖 For help: python test_runner.py --help")
        return 1
    
    # Create Test Runner
    runner = CookifyTestRunner()
    
    # Prepare parameters for all methods
    test_kwargs = {
        'verbose': not args.quiet,
        'coverage': args.coverage,
        'extra_args': []
    }
    
    # Additional pytest arguments
    if args.maxfail:
        test_kwargs['extra_args'].append(f"--maxfail={args.maxfail}")
    
    # Set test path if specified
    if args.test_path:
        runner.test_file = args.test_path

    # Determine which test method to call
    # First check: Endpoint-specific tests
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
    
    # Then: Test categories
    elif args.marker:
        # Custom marker
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
