#!/usr/bin/env python
import py_compile
import sys

try:
    py_compile.compile('D:/Projects/HRMS/hrm/routes.py', doraise=True)
    print("✅ routes.py syntax is valid!")
    sys.exit(0)
except py_compile.PyCompileError as e:
    print(f"❌ Syntax error in routes.py:")
    print(e)
    sys.exit(1)