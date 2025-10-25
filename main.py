import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import app

# NOTE: Route truncation disabled - routes.py is now complete with all functions
# The file previously had duplicate code that was being auto-truncated, 
# but this is no longer needed as the file structure is finalized.

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
import routes_tenant_config  # noqa: F401 - Tenant configuration and advanced features
import routes_leave  # noqa: F401 - Leave management routes
import cli_commands  # noqa: F401 - CLI commands for database management

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
