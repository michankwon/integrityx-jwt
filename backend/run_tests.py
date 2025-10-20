#!/usr/bin/env python3
"""
Test runner script for loan document sealing tests.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --coverage         # Run with coverage report
    python run_tests.py --verbose          # Run with verbose output
    python run_tests.py --specific test_name  # Run specific test
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path


def run_tests(coverage=False, verbose=False, specific_test=None):
    """Run the test suite with specified options."""
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    if specific_test:
        cmd.append(f"test_loan_documents.py::{specific_test}")
    else:
        cmd.append("test_loan_documents.py")
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    if coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])
    
    # Add additional options
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    print("=" * 60)
    
    # Run tests
    try:
        result = subprocess.run(cmd, check=True)
        print("=" * 60)
        print("✅ All tests passed!")
        
        if coverage:
            print("\n📊 Coverage report generated in htmlcov/index.html")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("=" * 60)
        print("❌ Tests failed!")
        print(f"Exit code: {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install test dependencies:")
        print("pip install -r requirements-test.txt")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run loan document sealing tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--specific", "-s", help="Run specific test method")
    
    args = parser.parse_args()
    
    success = run_tests(
        coverage=args.coverage,
        verbose=args.verbose,
        specific_test=args.specific
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

