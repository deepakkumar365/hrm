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
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) # needed for url_for to generate with https

# Environment-based configuration
environment = os.environ.get("ENVIRONMENT", "development").lower()

# Set session secret based on environment
if environment == "production":
    session_secret = os.environ.get("PROD_SESSION_SECRET")
    if not session_secret:
        raise RuntimeError("PROD_SESSION_SECRET is not set. Define it in .env for production environment.")
    database_url = os.environ.get("PROD_DATABASE_URL")
    if not database_url:
        raise RuntimeError("PROD_DATABASE_URL is not set. Define it in .env for production environment.")
else:
    session_secret = os.environ.get("DEV_SESSION_SECRET")
    if not session_secret:
        raise RuntimeError("DEV_SESSION_SECRET is not set. Define it in .env for development environment.")
    database_url = os.environ.get("DEV_DATABASE_URL")
    if not database_url:
        raise RuntimeError("DEV_DATABASE_URL is not set. Define it in .env for development environment.")

app.secret_key = session_secret
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
logging.info(f"🌍 Running in {environment.upper()} mode")
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

# Add custom Jinja2 filters
def date_filter(value, format='%d/%m/%Y'):
    """Format a date object to a string."""
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    try:
        return value.strftime(format)
    except (AttributeError, ValueError):
        return value

def currency_filter(amount):
    """Format amount as Singapore currency."""
    if amount is None:
        return "S$ 0.00"
    try:
        return f"S$ {float(amount):,.2f}"
    except (ValueError, TypeError):
        return "S$ 0.00"

app.jinja_env.filters['date'] = date_filter
app.jinja_env.filters['currency'] = currency_filter

# Import seed after models to avoid circular import
from seed import seed
app.cli.add_command(seed)
