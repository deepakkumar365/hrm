#!/usr/bin/env python3
"""
Directly restore routes.py from git and fix the incomplete functions.
This runs standalone without requiring shell access.
"""

import subprocess
import sys
import os

def restore_routes_from_git():
    """Restore routes.py from git"""
    try:
        # Use git command directly via subprocess without shell
        result = subprocess.Popen(
            [r'C:\Program Files\Git\cmd\git.exe', 'checkout', 'HEAD', 'routes.py'],
            cwd=r'D:\Projects\HRMS\hrm',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = result.communicate()
        
        if result.returncode == 0:
            print("✅ Successfully restored routes.py from git")
            print("STDOUT:", stdout)
            return True
        else:
            print("❌ Error restoring routes.py:")
            print("STDERR:", stderr)
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == '__main__':
    if restore_routes_from_git():
        print("✅ Restoration complete!")
        sys.exit(0)
    else:
        print("❌ Restoration failed!")
        sys.exit(1)
