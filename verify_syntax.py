#!/usr/bin/env python3
"""Verify Python syntax of key files"""

import py_compile
import sys

files_to_check = [
    'app.py',
    'models.py',
    'routes.py',
    'main.py',
]

all_ok = True
for filename in files_to_check:
    try:
        py_compile.compile(filename, doraise=True)
        print(f"✅ {filename} - Syntax OK")
    except py_compile.PyCompileError as e:
        print(f"❌ {filename} - Syntax Error:")
        print(f"   {e}")
        all_ok = False

if all_ok:
    print("\n🎉 All files have valid syntax!")
    sys.exit(0)
else:
    print("\n⚠️  Some files have syntax errors!")
    sys.exit(1)