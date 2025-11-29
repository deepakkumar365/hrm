#!/usr/bin/env python3
import sys

try:
    with open('routes.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"Total lines: {len(lines)}")
        print("\nLast 50 lines:")
        print("=" * 80)
        for i, line in enumerate(lines[-50:], start=len(lines)-49):
            print(f"{i:4d}: {line.rstrip()}")
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)