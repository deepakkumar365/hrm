#!/usr/bin/env python3
import py_compile
import sys

try:
    py_compile.compile('routes.py', doraise=True)
    print("✅ routes.py - Syntax OK")
    sys.exit(0)
except py_compile.PyCompileError as e:
    print(f"❌ Syntax Error in routes.py:")
    print(e)
    sys.exit(1)