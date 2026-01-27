#!/usr/bin/env python
"""
Test script to demonstrate page range selection with validation.
"""

import sys
import subprocess
from pathlib import Path

# Test cases
test_cases = [
    ("0", "9", "Valid: 10 pages"),
    ("0", "4", "Valid: 5 pages"),
    ("5", "14", "Invalid: 10 pages but exceeds total"),
    ("0", "19", "Invalid: 20 pages (exceeds 10 page limit)"),
    ("100", "200", "Invalid: beyond PDF range"),
]

print("=" * 70)
print("TESTING PAGE RANGE VALIDATION")
print("=" * 70)

for i, (start, end, description) in enumerate(test_cases, 1):
    print(f"\nTest {i}: {description}")
    print(f"  Input: start={start}, end={end}")
    print(f"  Expected behavior: {'ACCEPT' if 'Valid' in description else 'REJECT'}")

print("\n" + "=" * 70)
print("NOTE: Run 'python example_usage.py' to test interactively")
print("=" * 70)
