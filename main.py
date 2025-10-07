import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import app
import routes  # noqa: F401
import routes_tenant_company  # noqa: F401 - Tenant/Company hierarchy routes
import routes_team_documents  # noqa: F401 - Team and Documents module routes

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
