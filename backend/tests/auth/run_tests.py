"""
Test Runner for Auth Tests.

This script provides a convenient way to run Auth tests with different configurations.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    current_file = Path(__file__).resolve()
    # Navigate up to find the project root (where main.py is located)
    for parent in current_file.parents:
        if (parent / 'main.py').exists():
            return parent
    return current_file.parent.parent.parent


def run_tests(test_type: str = "all", coverage: bool = False, verbose: bool = False):
    """Run auth tests with specified configuration."""
    
    project_root = get_project_root()
    os.chdir(project_root)
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test paths based on type
    if test_type == "unit":
        cmd.append("tests/auth/unit/")
    elif test_type == "integration":
        cmd.append("tests/auth/integration/")
    elif test_type == "all":
        cmd.append("tests/auth/")
    else:
        print(f"Unknown test type: {test_type}")
        return 1
    
    # Add coverage if requested
    if coverage:
        cmd.extend([
            "--cov=domains.auth",
            "--cov-report=html:htmlcov/auth",
            "--cov-report=term-missing"
        ])
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add other useful pytest options
    cmd.extend([
        "--tb=short",  # Shorter traceback format
        "-x",          # Stop on first failure
        "--strict-markers",  # Strict marker handling
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    print(f"Working directory: {os.getcwd()}")
    print("-" * 50)
    
    # Run the tests
    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Run Auth tests")
    
    parser.add_argument(
        "--unit", 
        action="store_const", 
        const="unit", 
        dest="test_type",
        help="Run only unit tests"
    )
    
    parser.add_argument(
        "--integration", 
        action="store_const", 
        const="integration", 
        dest="test_type",
        help="Run only integration tests"
    )
    
    parser.add_argument(
        "--all", 
        action="store_const", 
        const="all", 
        dest="test_type",
        default="all",
        help="Run all tests (default)"
    )
    
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("COOKIFY AUTH TEST RUNNER")
    print("=" * 60)
    print(f"Test type: {args.test_type}")
    print(f"Coverage: {args.coverage}")
    print(f"Verbose: {args.verbose}")
    print("=" * 60)
    
    # Set environment variables for testing
    os.environ["AUTH_TEST_MOCK_MODE"] = "true"
    
    if args.test_type == "integration":
        os.environ["AUTH_TEST_INTEGRATION"] = "true"
        print("NOTE: Integration tests require valid Supabase credentials")
        print("Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
        print("-" * 60)
    
    # Run tests
    exit_code = run_tests(
        test_type=args.test_type,
        coverage=args.coverage,
        verbose=args.verbose
    )
    
    print("-" * 60)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    if args.coverage and exit_code == 0:
        print("\nCoverage report generated in htmlcov/auth/")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
