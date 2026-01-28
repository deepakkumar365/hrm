from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
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
#logging.basicConfig(level=logging.DEBUG)

# Suppress verbose AWS and HTTP logs
#logging.getLogger('boto3').setLevel(logging.WARNING)
#logging.getLogger('botocore').setLevel(logging.WARNING)
#logging.getLogger('s3transfer').setLevel(logging.WARNING)
#logging.getLogger('urllib3').setLevel(logging.WARNING)

class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) # needed for url_for to generate with https

# Swagger Configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "HRM Mobile API",
        "description": "API Documentation for HRM Mobile Application",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\""
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

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
    session_secret = os.environ.get("PROD_SESSION_SECRET")
    if not session_secret:
        raise RuntimeError("PROD_SESSION_SECRET is not set. Define it in .env for development environment.")
    database_url = os.environ.get("DEV_DATABASE_URL")
    if not database_url:
        raise RuntimeError("DEV_DATABASE_URL is not set. Define it in .env for development environment.")

app.secret_key = session_secret
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
logging.info(f"[INFO] Running in {environment.upper()} mode")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

# Session configuration for security
from datetime import timedelta, date
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=2)  # Session expires after 2 hours
app.config["SESSION_COOKIE_SECURE"] = environment == "production"  # HTTPS only in production
app.config["SESSION_COOKIE_HTTPONLY"] = True  # Prevent JavaScript access to session cookie
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # CSRF protection
app.config["SESSION_REFRESH_EACH_REQUEST"] = False  # Don't extend session on each request

# File upload configuration
app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16MB default
app.config["ALLOWED_IMAGE_EXTENSIONS"] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER") or os.path.join(app.root_path, "static", "uploads", "employees")

# Ensure upload folder exists
try:
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
except Exception:
    pass

db = SQLAlchemy(app, model_class=Base)
migrate = Migrate(app, db)

from flask_apscheduler import APScheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Import models so they're registered with SQLAlchemy metadata
from core import models  # noqa: E402,F401

# Add hasattr to Jinja2 global functions
app.jinja_env.globals['hasattr'] = hasattr
app.jinja_env.globals['getattr'] = getattr


# Add date module to Jinja2 globals for template use
app.jinja_env.globals['date'] = date

# Add a helper function to get current year
def get_current_year():
    return date.today().year

app.jinja_env.globals['get_current_year'] = get_current_year

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
from services.seed import seed
app.cli.add_command(seed)

# Final registration of access control helpers to ensure they are available in all templates
from core.utils import check_ui_access, check_module_access
app.jinja_env.globals['check_ui_access'] = check_ui_access
app.jinja_env.globals['check_module_access'] = check_module_access
app.jinja_env.filters['check_ui_access'] = check_ui_access

@app.context_processor
def utility_processor():
    return dict(check_ui_access=check_ui_access, check_module_access=check_module_access)
