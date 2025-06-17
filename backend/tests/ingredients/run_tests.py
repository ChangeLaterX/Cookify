#!/usr/bin/env python3
"""
Test Runner for Ingredients Module.

This script runs the complete test suite for the ingredients module,
including unit tests, integration tests, and generates coverage reports.
"""

import sys
import os
import subprocess
import asyncio
from pathlib import Path
from typing import List, Optional

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from tests.ingredients.config import IngredientsTestConfig


class IngredientsTestRunner:
    """Test runner for ingredients module."""
    
    def __init__(self):
        self.config = IngredientsTestConfig()
        self.test_dir = Path(__file__).parent
        self.backend_dir = self.test_dir.parent.parent
        
    def run_unit_tests(self, verbose: bool = False) -> bool:
        """Run unit tests for ingredients module."""
        print("🧪 Running Ingredients Unit Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir / "unit"),
            "--tb=short",
            "-v" if verbose else "-q"
        ]
        
        if self.config.GENERATE_COVERAGE:
            cmd.extend([
                "--cov=domains.ingredients",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov/ingredients"
            ])
        
        result = subprocess.run(cmd, cwd=self.backend_dir)
        return result.returncode == 0
    
    def run_integration_tests(self, verbose: bool = False) -> bool:
        """Run integration tests for ingredients module."""
        print("🔗 Running Ingredients Integration Tests...")
        
        if not self.config.RUN_INTEGRATION_TESTS:
            print("ℹ️  Integration tests skipped (RUN_INTEGRATION_TESTS=False)")
            return True
        
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir / "integration"),
            "--tb=short",
            "-v" if verbose else "-q",
            "--asyncio-mode=auto"
        ]
        
        if self.config.GENERATE_COVERAGE:
            cmd.extend([
                "--cov=domains.ingredients",
                "--cov-append"
            ])
        
        result = subprocess.run(cmd, cwd=self.backend_dir)
        return result.returncode == 0
    
    def run_specific_test(self, test_path: str, verbose: bool = False) -> bool:
        """Run a specific test file or test function."""
        print(f"🎯 Running Specific Test: {test_path}")
        
        cmd = [
            "python", "-m", "pytest",
            test_path,
            "--tb=short",
            "-v" if verbose else "-q"
        ]
        
        result = subprocess.run(cmd, cwd=self.backend_dir)
        return result.returncode == 0
    
    def run_all_tests(self, verbose: bool = False) -> bool:
        """Run all tests in the ingredients module."""
        print("🚀 Running All Ingredients Tests...")
        
        # Run unit tests first
        unit_success = self.run_unit_tests(verbose)
        if not unit_success:
            print("❌ Unit tests failed!")
            return False
        
        # Run integration tests
        integration_success = self.run_integration_tests(verbose)
        if not integration_success:
            print("❌ Integration tests failed!")
            return False
        
        print("✅ All ingredients tests passed!")
        return True
    
    def validate_environment(self) -> bool:
        """Validate that the test environment is properly configured."""
        print("🔍 Validating Test Environment...")
        
        # Check if required packages are installed
        try:
            import pytest
            import pydantic
            import supabase
        except ImportError as e:
            print(f"❌ Missing required package: {e}")
            return False
        
        # Check if ingredients module can be imported
        try:
            from domains.ingredients.services import IngredientsService
            from domains.ingredients.schemas import IngredientMasterCreate
        except ImportError as e:
            print(f"❌ Cannot import ingredients module: {e}")
            return False
        
        # Check test configuration
        if self.config.RUN_INTEGRATION_TESTS and not self.config.SUPABASE_URL:
            print("⚠️  Warning: Integration tests enabled but no Supabase URL configured")
        
        print("✅ Environment validation passed!")
        return True
    
    def generate_test_report(self) -> None:
        """Generate a comprehensive test report."""
        print("📊 Generating Test Report...")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir),
            "--tb=short",
            "--junit-xml=test-results/ingredients-results.xml",
            "--html=test-results/ingredients-report.html",
            "--self-contained-html"
        ]
        
        if self.config.GENERATE_COVERAGE:
            cmd.extend([
                "--cov=domains.ingredients",
                "--cov-report=html:test-results/ingredients-coverage",
                "--cov-report=xml:test-results/ingredients-coverage.xml"
            ])
        
        # Create results directory
        results_dir = self.backend_dir / "test-results"
        results_dir.mkdir(exist_ok=True)
        
        subprocess.run(cmd, cwd=self.backend_dir)
        print("📈 Test report generated in test-results/")
    
    def run_performance_tests(self) -> bool:
        """Run performance-focused tests."""
        print("⚡ Running Performance Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir),
            "-k", "performance",
            "--tb=short",
            "-v"
        ]
        
        result = subprocess.run(cmd, cwd=self.backend_dir)
        return result.returncode == 0
    
    def list_available_tests(self) -> None:
        """List all available tests in the ingredients module."""
        print("📋 Available Ingredients Tests:")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir),
            "--collect-only",
            "-q"
        ]
        
        subprocess.run(cmd, cwd=self.backend_dir)


def main():
    """Main entry point for the test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test runner for ingredients module",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --validate         # Validate environment only
    python run_tests.py --report           # Generate comprehensive report
    python run_tests.py --test test_file   # Run specific test file
    python run_tests.py --list             # List available tests
        """
    )
    
    parser.add_argument(
        "--unit", action="store_true",
        help="Run unit tests only"
    )
    parser.add_argument(
        "--integration", action="store_true", 
        help="Run integration tests only"
    )
    parser.add_argument(
        "--test", type=str,
        help="Run specific test file or function"
    )
    parser.add_argument(
        "--validate", action="store_true",
        help="Validate test environment only"
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Generate comprehensive test report"
    )
    parser.add_argument(
        "--performance", action="store_true",
        help="Run performance tests only"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List available tests"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    runner = IngredientsTestRunner()
    
    # Handle specific commands
    if args.validate:
        success = runner.validate_environment()
        sys.exit(0 if success else 1)
    
    if args.list:
        runner.list_available_tests()
        sys.exit(0)
    
    if args.report:
        runner.generate_test_report()
        sys.exit(0)
    
    # Validate environment before running tests
    if not runner.validate_environment():
        sys.exit(1)
    
    # Run tests based on arguments
    success = True
    
    if args.test:
        success = runner.run_specific_test(args.test, args.verbose)
    elif args.unit:
        success = runner.run_unit_tests(args.verbose)
    elif args.integration:
        success = runner.run_integration_tests(args.verbose)
    elif args.performance:
        success = runner.run_performance_tests()
    else:
        # Default: run all tests
        success = runner.run_all_tests(args.verbose)
    
    if success:
        print("🎉 Test run completed successfully!")
        sys.exit(0)
    else:
        print("💥 Test run failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
