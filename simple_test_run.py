#!/usr/bin/env python3
"""Simple Test Proof Generator"""

import subprocess
import sys

tests = [
    ("S3 Validators", "tests/unit/test_s3_validator.py"),
    ("Lambda Tests", "tests/unit/test_lambda_integration.py"),
    ("Glue Tests", "tests/unit/test_glue_integration.py"),
    ("DocumentDB Tests", "tests/unit/test_documentdb_integration.py"),
]

print("\n" + "="*80)
print("RUNNING TESTS FOR CLIENT PROOF")
print("="*80 + "\n")

for name, test_file in tests:
    print(f"\n{'─'*80}")
    print(f"TEST: {name}")
    print(f"File: {test_file}")
    print(f"{'─'*80}\n")
    
    subprocess.run([sys.executable, "-m", "pytest", test_file, "-v"], cwd=".")

print("\n" + "="*80)
print("ALL TESTS COMPLETE")
print("="*80 + "\n")
