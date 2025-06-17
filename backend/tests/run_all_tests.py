#!/usr/bin/env python3
"""
🧪 Cookify Universal Test Runner
A script to run all domain tests with a unified interface.
"""

import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CookifyTestRunner:
    """Universal test runner for all domains."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.start_time = None
        self.end_time = None
        
        # Available domains
        self.domains = {
            'auth': self.base_path / 'auth',
            'ingredients': self.base_path / 'ingredients', 
            'ocr': self.base_path / 'ocr'
        }
    
    def _build_pytest_command(self, domain=None, test_type=None, verbose=True, coverage=False, extra_args=None):
        """Build the pytest command."""
        cmd = ["python", "-m", "pytest"]
        
        if domain:
            if domain not in self.domains:
                raise ValueError(f"Unknown domain: {domain}. Available: {list(self.domains.keys())}")
            cmd.append(str(self.domains[domain]))
        else:
            # Run all tests
            cmd.append("tests/")
        
        if test_type:
            cmd.extend(["-m", test_type])
        
        if verbose:
            cmd.append("-v")
        
        if coverage:
            cmd.extend(["--cov=domains", "--cov-report=html", "--cov-report=term"])
        
        # Add standard options
        cmd.extend([
            "--tb=short",
            "--strict-markers",
            "--strict-config"
        ])
        
        if extra_args:
            cmd.extend(extra_args)
        
        return cmd
    
    def run_domain_tests(self, domain, test_type=None, verbose=True, coverage=False, extra_args=None):
        """Run tests for a specific domain."""
        logger.info(f"🧪 Running {domain.upper()} tests...")
        
        if test_type:
            logger.info(f"📋 Test type: {test_type}")
        
        self.start_time = datetime.now()
        
        try:
            cmd = self._build_pytest_command(
                domain=domain, 
                test_type=test_type, 
                verbose=verbose, 
                coverage=coverage, 
                extra_args=extra_args
            )
            
            logger.info(f"🚀 Command: {' '.join(cmd)}")
            result = subprocess.run(cmd, cwd=self.base_path.parent, check=False)
            
            self.end_time = datetime.now()
            duration = self.end_time - self.start_time
            
            if result.returncode == 0:
                logger.info(f"✅ {domain.upper()} tests completed successfully in {duration}")
            else:
                logger.error(f"❌ {domain.upper()} tests failed in {duration}")
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"💥 Error running {domain} tests: {e}")
            return False
    
    def run_all_tests(self, test_type=None, verbose=True, coverage=False, extra_args=None):
        """Run all domain tests."""
        logger.info("🧪 Running ALL domain tests...")
        
        self.start_time = datetime.now()
        
        try:
            cmd = self._build_pytest_command(
                domain=None, 
                test_type=test_type, 
                verbose=verbose, 
                coverage=coverage, 
                extra_args=extra_args
            )
            
            logger.info(f"🚀 Command: {' '.join(cmd)}")
            result = subprocess.run(cmd, cwd=self.base_path.parent, check=False)
            
            self.end_time = datetime.now()
            duration = self.end_time - self.start_time
            
            if result.returncode == 0:
                logger.info(f"✅ All tests completed successfully in {duration}")
            else:
                logger.error(f"❌ Some tests failed in {duration}")
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"💥 Error running tests: {e}")
            return False
    
    def list_available_tests(self):
        """List all available test domains and types."""
        logger.info("📋 Available test domains:")
        for domain, path in self.domains.items():
            if path.exists():
                logger.info(f"  • {domain} ({path})")
            else:
                logger.warning(f"  • {domain} (⚠️  path not found: {path})")
        
        logger.info("\n📋 Available test types (markers):")
        logger.info("  • unit - Unit tests")
        logger.info("  • integration - Integration tests")
        logger.info("  • auth - Auth domain tests")
        logger.info("  • ingredients - Ingredients domain tests")
        logger.info("  • ocr - OCR domain tests")
        logger.info("  • security - Security-related tests")
        logger.info("  • slow - Slow-running tests")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="🧪 Cookify Universal Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_tests.py                           # Run all tests
  python run_all_tests.py --domain auth             # Run auth tests only
  python run_all_tests.py --domain ingredients      # Run ingredients tests only
  python run_all_tests.py --type unit               # Run unit tests only
  python run_all_tests.py --domain auth --type unit # Run auth unit tests only
  python run_all_tests.py --coverage                # Run with coverage report
  python run_all_tests.py --list                    # List available options
        """
    )
    
    parser.add_argument(
        "--domain", 
        choices=["auth", "ingredients", "ocr"],
        help="Run tests for specific domain only"
    )
    
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "security", "slow"],
        help="Run specific type of tests only"
    )
    
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--quiet", 
        action="store_true",
        help="Reduce output verbosity"
    )
    
    parser.add_argument(
        "--list", 
        action="store_true",
        help="List available test domains and types"
    )
    
    parser.add_argument(
        "pytest_args", 
        nargs="*",
        help="Additional arguments to pass to pytest"
    )
    
    args = parser.parse_args()
    
    runner = CookifyTestRunner()
    
    if args.list:
        runner.list_available_tests()
        return 0
    
    verbose = not args.quiet
    
    try:
        if args.domain:
            success = runner.run_domain_tests(
                domain=args.domain,
                test_type=args.type,
                verbose=verbose,
                coverage=args.coverage,
                extra_args=args.pytest_args
            )
        else:
            success = runner.run_all_tests(
                test_type=args.type,
                verbose=verbose,
                coverage=args.coverage,
                extra_args=args.pytest_args
            )
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  Test run interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
