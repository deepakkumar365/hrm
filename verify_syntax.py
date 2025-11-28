#!/usr/bin/env python
import ast

try:
    with open('D:/DEV/HRM/hrm/routes.py', 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    
    ast.parse(code)
    print("[SUCCESS] routes.py syntax is valid!")
    
except SyntaxError as e:
    print(f"[ERROR] Syntax error: {e}")
    exit(1)
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)