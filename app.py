from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from sqlalchemy.orm import DeclarativeBase

# Load .env if available to populate env vars early
try:
    from pathlib import Path
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).with_name(".env"))
except Exception:
    # If python-dotenv is not installed, ignore; env must be set by shell
    pass

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) # needed for url_for to generate with https

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
if not app.config["SQLALCHEMY_DATABASE_URI"]:
    raise RuntimeError("DATABASE_URL is not set. Define it in .env or your environment before starting the app.")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

# File upload configuration
app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_CONTENT_LENGTH", 1 * 1024 * 1024))  # 1MB default
app.config["ALLOWED_IMAGE_EXTENSIONS"] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER") or os.path.join(app.root_path, "static", "uploads", "employees")

# Ensure upload folder exists
try:
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
except Exception:
    pass

db = SQLAlchemy(app, model_class=Base)
migrate = Migrate(app, db)

# Import models so they're registered with SQLAlchemy metadata
import models  # noqa: E402,F401

# Add hasattr to Jinja2 global functions
app.jinja_env.globals['hasattr'] = hasattr

# Import seed after models to avoid circular import
from seed import seed
app.cli.add_command(seed)
