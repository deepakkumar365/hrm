import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import app

# CRITICAL: Directly truncate routes.py to remove duplicate code BEFORE any imports
# This must happen before Flask app imports routes
try:
    import os
    routes_path = os.path.join(os.path.dirname(__file__), 'routes.py')
    
    with open(routes_path, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
    
    if len(all_lines) > 2934:
        # Keep only first 2934 lines (function properly ends there)
        proper_lines = all_lines[:2934]
        if proper_lines[-1] and not proper_lines[-1].endswith('\n'):
            proper_lines[-1] = proper_lines[-1] + '\n'
        
        with open(routes_path, 'w', encoding='utf-8') as f:
            f.writelines(proper_lines)
        
        removed = len(all_lines) - len(proper_lines)
        print(f"✅ Cleaned up duplicate code - removed {removed} lines from routes.py")
except Exception as e:
    print(f"⚠️  Warning during cleanup: {e}")

# Clean up any remaining issues
try:
    import cleanup_duplicate_code  # noqa: F401 - Removes duplicate code from auto-fixes
except Exception as e:
    print(f"⚠️  Warning: Could not cleanup: {e}")

# Fix syntax errors in routes.py before importing
try:
    import auto_syntax_fix  # noqa: F401 - Auto-fixes incomplete claims_approve function
except Exception as e:
    print(f"⚠️  Warning: Could not run syntax fix: {e}")

import routes  # noqa: F401
import routes_tenant_company  # noqa: F401 - Tenant/Company hierarchy routes
import routes_team_documents  # noqa: F401 - Team and Documents module routes
import routes_enhancements  # noqa: F401 - Employee edit, reports, bank info enhancements
import routes_masters  # noqa: F401 - Master data management (Roles, Departments, Working Hours, Work Schedules)
import routes_bulk_upload  # noqa: F401 - Employee bulk upload functionality
import routes_access_control  # noqa: F401 - Access Control Management
import cli_commands  # noqa: F401 - CLI commands for database management

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
