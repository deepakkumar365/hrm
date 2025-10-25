#!/usr/bin/env python
"""Build check script - validates all modules can be imported"""

import sys
import importlib

test_modules = [
    'app',
    'models', 
    'auth',
    'forms',
    'utils',
    'routes',
    'routes_leave',
    'routes_masters',
    'routes_access_control'
]

print("[BUILD CHECK] Starting comprehensive module validation...")
print("=" * 60)

errors = []
for module_name in test_modules:
    try:
        importlib.import_module(module_name)
        print(f"[OK] {module_name:30s} - Imported successfully")
    except Exception as e:
        error_msg = f"[ERROR] {module_name:30s} - {str(e)}"
        print(error_msg)
        errors.append(error_msg)

print("=" * 60)
if not errors:
    print("[SUCCESS] All modules compiled and imported successfully!")
    print("[STATUS] Application is ready to run")
    sys.exit(0)
else:
    print(f"[FAILED] {len(errors)} module(s) failed")
    for error in errors:
        print(error)
    sys.exit(1)