#!/usr/bin/env python
"""Direct migration runner to bypass PowerShell execution policy issues"""

import subprocess
import sys
import os

os.chdir(r'D:\Projects\HRMS\hrm')

# Run migration
result = subprocess.run(
    [sys.executable, '-m', 'flask', 'db', 'upgrade'],
    capture_output=False
)

sys.exit(result.returncode)