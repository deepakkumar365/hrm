import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import app

# NOTE: Route truncation disabled - routes.py is now complete with all functions
# The file previously had duplicate code that was being auto-truncated, 
# but this is no longer needed as the file structure is finalized.

# Auto-fix modules disabled - they cause continuous file rewrites and server restarts
# These are not needed if routes.py is already correct
# Uncomment only if needed for emergency fixes
# try:
#     import cleanup_duplicate_code  # noqa: F401 - Removes duplicate code from auto-fixes
# except Exception as e:
#     print(f"⚠️  Warning: Could not cleanup: {e}")
#
# try:
#     import auto_syntax_fix  # noqa: F401 - Auto-fixes incomplete claims_approve function
# except Exception as e:
#     print(f"⚠️  Warning: Could not run syntax fix: {e}")

import routes  # noqa: F401
import routes_tenant_company  # noqa: F401 - Tenant/Company hierarchy routes
import routes_team_documents  # noqa: F401 - Team and Documents module routes
import routes_enhancements  # noqa: F401 - Employee edit, reports, bank info enhancements
import routes_masters  # noqa: F401 - Master data management (Roles, Departments, Working Hours, Work Schedules)
import routes_bulk_upload  # noqa: F401 - Employee bulk upload functionality
import routes_access_control  # noqa: F401 - Access Control Management
import routes_tenant_config  # noqa: F401 - Tenant configuration and advanced features
import routes_leave  # noqa: F401 - Leave management routes
import routes_employee_group  # noqa: F401 - Employee Group master management
import routes_leave_allocation  # noqa: F401 - Leave allocation configuration
import routes_ot  # noqa: F401 - OT (Overtime) Management routes
import routes_hr_manager  # noqa: F401 - HR Manager Dashboard
import cli_commands  # noqa: F401 - CLI commands for database management

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
