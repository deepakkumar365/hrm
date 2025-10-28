import subprocess
import sys

result = subprocess.run([sys.executable, 'fix_designation_now.py'], cwd='D:/Projects/HRMS/hrm')
sys.exit(result.returncode)