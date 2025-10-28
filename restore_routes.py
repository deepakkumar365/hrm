#!/usr/bin/env python3
"""Restore routes.py from git history"""

import subprocess
import sys

try:
    # Restore routes.py from git
    result = subprocess.run(
        ['git', 'checkout', 'HEAD', 'routes.py'],
        cwd='D:/Projects/HRMS/hrm',
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Successfully restored routes.py from git")
        print(result.stdout)
    else:
        print("❌ Error restoring routes.py:")
        print(result.stderr)
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)