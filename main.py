import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import app
import routes  # noqa: F401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
