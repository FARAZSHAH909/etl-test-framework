#!/usr/bin/env python3
"""
Run ALL Tests and Display Results - Ready for Screenshots
"""

import subprocess
import sys
from pathlib import Path

def run_all_tests():
    """Execute all test files and display results"""
    
    print("\n" + "="*90)
    print("ETL FRAMEWORK - RUNNING ALL TESTS")
    print("="*90)
    print(f"Test Directory: tests/unit/")
    print(f"Python: {sys.version}")
    print("="*90 + "\n")
    
    # Run all unit tests
    cmd = [sys.executable, "-m", "pytest", "tests/unit/", "-v", "--tb=short", "-ra"]
    
    print(f"Command: {' '.join(cmd)}\n")
    print("-"*90 + "\n")
    
    # Run and capture output
    result = subprocess.run(cmd, cwd=".")
    
    print("\n" + "-"*90)
    print("="*90)
    print("TEST EXECUTION COMPLETE")
    print("="*90 + "\n")
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
