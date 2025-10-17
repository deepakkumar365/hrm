import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import app
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
