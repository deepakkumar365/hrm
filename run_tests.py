#!/usr/bin/env python3
"""
Simple test runner script for the HRM application.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py test_base    # Run specific test module
    python run_tests.py -v          # Run with verbose output
"""

import sys
import subprocess
import os


def main():
    """Run pytest with the given arguments."""
    # Change to the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Default arguments
    pytest_args = ["python", "-m", "pytest"]
    
    # Add user arguments
    if len(sys.argv) > 1:
        # If arguments are provided, use them
        pytest_args.extend(sys.argv[1:])
    else:
        # Default: run all tests with verbose output
        pytest_args.extend(["tests/", "-v"])
    
    # Run pytest
    try:
        result = subprocess.run(pytest_args, check=False)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()