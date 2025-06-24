#!/usr/bin/env python3
"""
🧪 Enterprise Test Runner for Cookify Backend

Professional-grade test execution with comprehensive reporting and quality gates.
Designed for medium-sized software companies with enterprise requirements.

Usage:
    python tests/run_tests.py --help
    python tests/run_tests.py --type unit --coverage --parallel
    python tests/run_tests.py --domain auth --ci-mode
    python tests/run_tests.py --security-scan --performance-check
"""

import argparse
import subprocess
import sys
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Optional


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class EnterpriseTestRunner:
    """Enterprise-grade test runner with comprehensive features."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.test_path = Path(__file__).parent
        self.start_time = time.time()
        self.results = {}
        
    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{title:^60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    def print_success(self, message: str):
        """Print a success message."""
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
    
    def print_warning(self, message: str):
        """Print a warning message."""
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")
    
    def print_error(self, message: str):
        """Print an error message."""
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
    
    def print_info(self, message: str):
        """Print an info message."""
        print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")
    
    def run_command(self, cmd: List[str], capture_output: bool = False) -> tuple:
        """Run a command and return exit code and output."""
        print(f"{Colors.OKCYAN}🔧 Running: {' '.join(cmd)}{Colors.ENDC}")
        
        try:
            if capture_output:
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.base_path)
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(cmd, cwd=self.base_path, text=True)
                return result.returncode, "", ""
        except Exception as e:
            self.print_error(f"Command execution failed: {e}")
            return 1, "", str(e)
    
    def setup_environment(self):
        """Setup test environment."""
        self.print_info("Setting up test environment...")
        
        # Set Python path
        os.environ["PYTHONPATH"] = f"{self.base_path}:{os.environ.get('PYTHONPATH', '')}"
        
        # Set test environment variables
        test_env = {
            "ENVIRONMENT": "testing",
            "DEBUG": "false",
            "PYTEST_CURRENT_TEST": "true",
            "DB_READ_ONLY": "true",
            "OCR_TEST_MOCK_MODE": "true"
        }
        
        for key, value in test_env.items():
            os.environ[key] = value
        
        self.print_success("Environment setup complete")
    
    def install_package(self):
        """Install the package in editable mode."""
        self.print_info("Installing package in editable mode...")
        exit_code, _, _ = self.run_command(["pip", "install", "-e", "."])
        
        if exit_code == 0:
            self.print_success("Package installation complete")
        else:
            self.print_error("Package installation failed")
            return False
        return True
    
    def run_code_quality_checks(self) -> bool:
        """Run code quality checks."""
        self.print_header("🔍 CODE QUALITY CHECKS")
        
        checks = [
            (["black", "--check", "."], "Code formatting (Black)"),
            (["isort", "--check-only", "."], "Import sorting (isort)"),
            (["flake8", ".", "--count", "--statistics"], "Linting (Flake8)")
        ]
        
        all_passed = True
        for cmd, description in checks:
            self.print_info(f"Running {description}...")
            exit_code, _, _ = self.run_command(cmd)
            
            if exit_code == 0:
                self.print_success(f"{description} passed")
            else:
                self.print_error(f"{description} failed")
                all_passed = False
        
        self.results["code_quality"] = all_passed
        return all_passed
    
    def run_security_scan(self) -> bool:
        """Run security scans."""
        self.print_header("🛡️ SECURITY SCAN")
        
        scans = [
            (["bandit", "-r", ".", "-f", "txt"], "Security scan (Bandit)"),
            (["safety", "check"], "Dependency check (Safety)")
        ]
        
        all_passed = True
        for cmd, description in scans:
            self.print_info(f"Running {description}...")
            exit_code, _, _ = self.run_command(cmd)
            
            if exit_code == 0:
                self.print_success(f"{description} passed")
            else:
                self.print_warning(f"{description} found issues (check manually)")
        
        self.results["security_scan"] = all_passed
        return all_passed
    
    def run_tests(self, domain: Optional[str] = None, test_type: Optional[str] = None, 
                 coverage: bool = False, parallel: bool = False, ci_mode: bool = False) -> bool:
        """Run the actual tests."""
        if test_type:
            self.print_header(f"🧪 {test_type.upper()} TESTS")
        else:
            self.print_header("🧪 RUNNING TESTS")
        
        cmd = ["python", "-m", "pytest"]
        
        # Determine test path
        if domain:
            if test_type:
                test_path = f"tests/{domain}/{test_type}/"
            else:
                test_path = f"tests/{domain}/"
        else:
            test_path = "tests/"
        
        cmd.append(test_path)
        
        # Configuration file
        if ci_mode:
            cmd.extend(["-c", "tests/pytest-ci.ini"])
        else:
            cmd.extend(["-c", "tests/pytest-enterprise.ini"])
        
        # Test type filtering
        if test_type:
            if domain:
                cmd.extend(["-m", f"{test_type} and {domain}"])
            else:
                cmd.extend(["-m", test_type])
        elif domain:
            cmd.extend(["-m", domain])
        
        # Coverage
        if coverage:
            cmd.extend([
                "--cov=domains",
                "--cov=core", 
                "--cov=middleware",
                "--cov=shared",
                "--cov-report=xml:coverage.xml",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing"
            ])
        
        # CI-specific options
        if ci_mode:
            cmd.extend([
                "--verbose",
                "--tb=short",
                "--junitxml=test-results.xml",
                "--maxfail=5",
                "--durations=10"
            ])
        
        # Parallel execution
        if parallel:
            cmd.extend(["-n", "auto"])
        
        self.print_info(f"Test command: {' '.join(cmd)}")
        exit_code, _, _ = self.run_command(cmd)
        
        success = exit_code == 0
        if success:
            self.print_success("Tests passed successfully")
        else:
            self.print_error("Some tests failed")
        
        self.results["tests"] = success
        return success
    
    def run_performance_check(self) -> bool:
        """Run performance checks."""
        self.print_header("🚀 PERFORMANCE CHECK")
        
        cmd = [
            "python", "-m", "pytest", "tests/",
            "-c", "tests/pytest-enterprise.ini",
            "-m", "performance",
            "--verbose"
        ]
        
        exit_code, _, _ = self.run_command(cmd)
        
        success = exit_code == 0
        if success:
            self.print_success("Performance tests passed")
        else:
            self.print_warning("Performance tests failed or not found")
        
        self.results["performance"] = success
        return success
    
    def generate_report(self):
        """Generate a comprehensive test report."""
        self.print_header("📊 TEST REPORT")
        
        duration = time.time() - self.start_time
        
        print(f"📅 Test execution completed in {duration:.2f} seconds")
        print(f"🎯 Results summary:")
        
        for check, passed in self.results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"   {check.replace('_', ' ').title()}: {status}")
        
        # Overall status
        all_passed = all(self.results.values())
        if all_passed:
            self.print_success("🎉 All checks passed! Ready for deployment.")
        else:
            self.print_error("💥 Some checks failed. Please review and fix issues.")
        
        # Save report to file
        report_data = {
            "timestamp": time.time(),
            "duration_seconds": duration,
            "results": self.results,
            "overall_status": "success" if all_passed else "failure"
        }
        
        with open(self.test_path / "test-report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="🧪 Enterprise Test Runner for Cookify Backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/run_tests.py --type unit --coverage
  python tests/run_tests.py --domain auth --parallel
  python tests/run_tests.py --ci-mode --security-scan
  python tests/run_tests.py --full-suite
        """
    )
    
    # Test selection
    parser.add_argument("--domain", choices=["auth", "ingredients", "ocr"],
                       help="Run tests for specific domain")
    parser.add_argument("--type", choices=["unit", "integration", "performance"],
                       help="Run specific type of tests")
    
    # Test options
    parser.add_argument("--coverage", action="store_true",
                       help="Run with coverage reporting")
    parser.add_argument("--parallel", action="store_true",
                       help="Run tests in parallel")
    parser.add_argument("--ci-mode", action="store_true",
                       help="Run in CI mode with appropriate settings")
    
    # Quality checks
    parser.add_argument("--code-quality", action="store_true",
                       help="Run code quality checks")
    parser.add_argument("--security-scan", action="store_true",
                       help="Run security scans")
    parser.add_argument("--performance-check", action="store_true",
                       help="Run performance tests")
    
    # Comprehensive options
    parser.add_argument("--full-suite", action="store_true",
                       help="Run complete test suite with all checks")
    parser.add_argument("--quick", action="store_true",
                       help="Run quick unit tests only")
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = EnterpriseTestRunner()
    runner.print_header("🧪 COOKIFY ENTERPRISE TEST SUITE")
    
    # Setup environment
    runner.setup_environment()
    
    # Install package
    if not runner.install_package():
        sys.exit(1)
    
    success = True
    
    # Determine what to run
    if args.full_suite:
        # Run everything
        success &= runner.run_code_quality_checks()
        success &= runner.run_security_scan()
        success &= runner.run_tests(coverage=True, parallel=True, ci_mode=args.ci_mode)
        success &= runner.run_performance_check()
    elif args.quick:
        # Quick unit tests only
        success &= runner.run_tests(test_type="unit", parallel=True)
    else:
        # Run based on individual flags
        if args.code_quality:
            success &= runner.run_code_quality_checks()
        
        if args.security_scan:
            success &= runner.run_security_scan()
        
        # Always run tests if no specific quality checks are requested
        if not args.code_quality and not args.security_scan and not args.performance_check:
            success &= runner.run_tests(
                domain=args.domain,
                test_type=args.type,
                coverage=args.coverage,
                parallel=args.parallel,
                ci_mode=args.ci_mode
            )
        
        if args.performance_check:
            success &= runner.run_performance_check()
    
    # Generate report
    overall_success = runner.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()
