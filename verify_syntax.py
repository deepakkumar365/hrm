#!/usr/bin/env python3
"""Verify that routes.py has no syntax errors"""
import py_compile
import sys

try:
    py_compile.compile('routes.py', doraise=True)
    print("✅ SUCCESS: routes.py has valid Python syntax!")
    print("✅ The application should now start without syntax errors!")
    sys.exit(0)
except py_compile.PyCompileError as e:
    print(f"❌ SYNTAX ERROR: {e}")
    sys.exit(1)