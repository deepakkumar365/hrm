#!/usr/bin/env python3
import ast
import sys

try:
    print("Checking routes/routes.py syntax...")
    with open('routes/routes.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    ast.parse(code)
    print("✅ No syntax errors found!")
    
    # Also show file info
    lines = code.split('\n')
    print(f"Total lines: {len(lines)}")
    
except SyntaxError as e:
    print(f"❌ Syntax Error: {e}")
    print(f"   Line {e.lineno}: {e.text}")
    if e.offset:
        print(f"   {' ' * (e.offset - 1)}^")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
