import subprocess
import sys

# Run the initialization
result = subprocess.run([sys.executable, 'D:/Projects/HRMS/hrm/init_company_id_config_now.py'])
sys.exit(result.returncode)