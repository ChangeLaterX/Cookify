#!/usr/bin/env python3
"""
OCR Test Runner Script.

This script provides a convenient way to run different types of OCR tests
with proper configuration and reporting.

Usage:
    python run_ocr_tests.py --help
    python run_ocr_tests.py --unit              # Run only unit tests
    python run_ocr_tests.py --integration       # Run only integration tests  
    python run_ocr_tests.py --all               # Run all tests
    python run_ocr_tests.py --performance       # Run performance benchmarks
    python run_ocr_tests.py --coverage          # Run with coverage reporting
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional


class OCRTestRunner:
    """Test runner for OCR test suite."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.test_root = Path(__file__).parent
        
    def setup_environment(self, integration: bool = False, mock_mode: bool = True):
        """Setup environment variables for testing."""
        # Set test configuration
        os.environ['OCR_TEST_MOCK_MODE'] = 'false' if integration else 'true'
        os.environ['OCR_TEST_INTEGRATION'] = 'true' if integration else 'false'
        
        # Set Python path
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
            
        os.environ['PYTHONPATH'] = str(self.project_root)
        
    def check_dependencies(self, integration: bool = False) -> bool:
        """Check if required dependencies are available."""
        try:
            import pytest
        except ImportError:
            print("❌ pytest not available. Install with: pip install pytest")
            return False
            
        if integration:
            # Check for tesseract
            import shutil
            if not shutil.which('tesseract'):
                print("❌ tesseract not available. Install tesseract-ocr package.")
                return False
                
            # Check for PIL
            try:
                from PIL import Image
            except ImportError:
                print("❌ PIL not available. Install with: pip install Pillow")
                return False
                
            # Check for pytesseract
            try:
                import pytesseract
            except ImportError:
                print("❌ pytesseract not available. Install with: pip install pytesseract")
                return False
                
            print("✅ All integration test dependencies available")
        else:
            print("✅ Unit test dependencies available")
            
        return True
        
    def run_unit_tests(self, verbose: bool = False, coverage: bool = False) -> int:
        """Run unit tests only."""
        print("🧪 Running OCR Unit Tests...")
        
        self.setup_environment(integration=False)
        
        if not self.check_dependencies(integration=False):
            return 1
            
        cmd = ['python', '-m', 'pytest', str(self.test_root / 'unit')]
        
        if verbose:
            cmd.append('-v')
            
        if coverage:
            cmd.extend(['--cov=domains.ocr.services', '--cov-report=html', '--cov-report=term'])
            
        cmd.extend(['-x', '--tb=short'])  # Stop on first failure, short traceback
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode
        except KeyboardInterrupt:
            print("\n❌ Tests interrupted by user")
            return 1
            
    def run_integration_tests(self, verbose: bool = False, coverage: bool = False) -> int:
        """Run integration tests only."""
        print("🔧 Running OCR Integration Tests...")
        
        self.setup_environment(integration=True)
        
        if not self.check_dependencies(integration=True):
            return 1
            
        # Check for sample images
        data_dir = self.project_root.parent / 'data'
        required_images = ['sample_receipt.png', 'sample_receipt_blurred.png']
        
        missing_images = []
        for img in required_images:
            if not (data_dir / img).exists():
                missing_images.append(img)
                
        if missing_images:
            print(f"⚠️  Missing sample images: {missing_images}")
            print("   Generate them with: python data/generate_receipt_image.py")
            
        cmd = ['python', '-m', 'pytest', str(self.test_root / 'integration')]
        
        if verbose:
            cmd.append('-v')
            
        if coverage:
            cmd.extend(['--cov=domains.ocr.services', '--cov-report=html', '--cov-report=term'])
            
        cmd.extend(['-x', '--tb=short'])
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode
        except KeyboardInterrupt:
            print("\n❌ Tests interrupted by user")
            return 1
            
    def run_all_tests(self, verbose: bool = False, coverage: bool = False) -> int:
        """Run all OCR tests."""
        print("🚀 Running All OCR Tests...")
        
        # Run unit tests first
        print("\n" + "="*50)
        unit_result = self.run_unit_tests(verbose=verbose, coverage=False)
        
        if unit_result != 0:
            print("❌ Unit tests failed, skipping integration tests")
            return unit_result
            
        print("✅ Unit tests passed!")
        
        # Run integration tests
        print("\n" + "="*50)
        integration_result = self.run_integration_tests(verbose=verbose, coverage=coverage)
        
        if integration_result != 0:
            print("❌ Integration tests failed")
            return integration_result
            
        print("✅ All tests passed!")
        return 0
        
    def run_performance_tests(self, verbose: bool = False) -> int:
        """Run performance benchmark tests."""
        print("⚡ Running OCR Performance Tests...")
        
        self.setup_environment(integration=True)
        
        if not self.check_dependencies(integration=True):
            return 1
            
        cmd = [
            'python', '-m', 'pytest', 
            str(self.test_root / 'integration' / 'test_performance.py'),
            '-v', '--tb=short', '-s'  # Show print output for performance data
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode
        except KeyboardInterrupt:
            print("\n❌ Performance tests interrupted by user")
            return 1
            
    def run_specific_test(self, test_path: str, verbose: bool = False) -> int:
        """Run a specific test file or test function."""
        print(f"🎯 Running specific test: {test_path}")
        
        # Determine if it's an integration test
        is_integration = 'integration' in test_path
        self.setup_environment(integration=is_integration)
        
        if not self.check_dependencies(integration=is_integration):
            return 1
            
        cmd = ['python', '-m', 'pytest', test_path]
        
        if verbose:
            cmd.append('-v')
            
        cmd.extend(['--tb=short'])
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode
        except KeyboardInterrupt:
            print("\n❌ Test interrupted by user")
            return 1
            
    def generate_test_report(self) -> int:
        """Generate comprehensive test report."""
        print("📊 Generating OCR Test Report...")
        
        # Run all tests with coverage
        cmd = [
            'python', '-m', 'pytest',
            str(self.test_root),
            '--cov=domains.ocr.services',
            '--cov-report=html:htmlcov',
            '--cov-report=term-missing',
            '--cov-report=xml',
            '--junit-xml=test-results.xml',
            '-v'
        ]
        
        self.setup_environment(integration=True)
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ Test report generated successfully!")
                print("   HTML Coverage Report: htmlcov/index.html")
                print("   XML Results: test-results.xml")
            else:
                print("❌ Test report generation failed")
                
            return result.returncode
        except KeyboardInterrupt:
            print("\n❌ Report generation interrupted by user")
            return 1


def main():
    parser = argparse.ArgumentParser(
        description="OCR Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_ocr_tests.py --unit                    Run unit tests only
  python run_ocr_tests.py --integration             Run integration tests only
  python run_ocr_tests.py --all --coverage          Run all tests with coverage
  python run_ocr_tests.py --performance             Run performance benchmarks
  python run_ocr_tests.py --specific unit/test_text_extraction.py
  python run_ocr_tests.py --report                  Generate full test report
        """
    )
    
    # Test selection
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--unit', action='store_true', help='Run unit tests only')
    group.add_argument('--integration', action='store_true', help='Run integration tests only')
    group.add_argument('--all', action='store_true', help='Run all tests')
    group.add_argument('--performance', action='store_true', help='Run performance tests')
    group.add_argument('--specific', metavar='PATH', help='Run specific test file or function')
    group.add_argument('--report', action='store_true', help='Generate comprehensive test report')
    
    # Options
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--coverage', action='store_true', help='Include coverage reporting')
    
    args = parser.parse_args()
    
    runner = OCRTestRunner()
    
    try:
        if args.unit:
            return runner.run_unit_tests(verbose=args.verbose, coverage=args.coverage)
        elif args.integration:
            return runner.run_integration_tests(verbose=args.verbose, coverage=args.coverage)
        elif args.all:
            return runner.run_all_tests(verbose=args.verbose, coverage=args.coverage)
        elif args.performance:
            return runner.run_performance_tests(verbose=args.verbose)
        elif args.specific:
            return runner.run_specific_test(args.specific, verbose=args.verbose)
        elif args.report:
            return runner.generate_test_report()
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
