---
description: Repository Information Overview
alwaysApply: true
---

# HRM System Information

## Summary
**NolTrion HRM** is a comprehensive Human Resource Management system built with Flask and PostgreSQL. It provides multi-tenant support, role-based access control, and features modules for employee management, payroll, attendance, leave management, appraisals, compliance, and team collaboration. The system is designed for enterprise deployment with Docker and Render support.

## Structure
The project is organized as a single-tier Flask application with clear separation of concerns:
- **Backend**: Python Flask with SQLAlchemy ORM and Alembic migrations
- **Frontend**: Jinja2 templates with HTML/CSS/JavaScript in static assets
- **Database**: PostgreSQL with multi-schema support for tenants
- **Modules**: Organized by feature (attendance, payroll, leave, etc.)
- **Deployment**: Docker containerization with Gunicorn WSGI server

### Main Components
- **Application Core**: `app.py` (Flask initialization), `main.py` (entry point)
- **Database Layer**: `models.py` (39.6 KB - comprehensive data models), `migrations/` (Alembic versioning)
- **Routing**: `routes.py` (121 KB - main routes), plus modular route files (`routes_*.py`)
- **Templates**: 15+ module-specific directories under `templates/`
- **Static Assets**: CSS, JavaScript, logos, and upload directories under `static/`
- **Utilities**: Helper scripts for database operations, migrations, and deployment

## Language & Runtime
**Language**: Python
**Version**: 3.11+
**Build System**: Flask-Migrate (Alembic for schema versioning)
**Package Manager**: pip
**Runtime Platform**: Gunicorn WSGI server (production) / Flask development server
**Database**: PostgreSQL 16+ with SQLAlchemy 2.0+

## Dependencies
**Core Dependencies**:
- Flask 3.1.2 - Web framework
- Flask-SQLAlchemy 3.1.1 - ORM integration
- Flask-Migrate 4.1.0 - Database migrations
- SQLAlchemy 2.0.43 - SQL toolkit
- Flask-Login 0.6.3+ - User session management
- Flask-WTF 1.2.2+ - Form handling
- Werkzeug 3.1.3 - WSGI utilities
- Gunicorn 23.0.0+ - Production WSGI server
- psycopg2-binary 2.9.10+ - PostgreSQL adapter
- pandas 2.3.2+ - Data processing for exports
- openpyxl 3.1.2 - Excel file handling
- python-dateutil 2.9.0+ - Date utilities
- python-dotenv 1.0.0+ - Environment configuration
- PyJWT 2.10.1 - JWT token handling
- oauthlib 3.3.1 - OAuth support
- Flask-Dance 7.1.0 - Social authentication
- email-validator 2.3.0 - Email validation

**Development Dependencies**:
- pytest 7.0.0+ - Testing framework

## Build & Installation
**Development Setup**:
```bash
pip install -r requirements.txt
flask db upgrade
python main.py
```

**Production Build** (Render deployment):
```bash
./build.sh
```

**Build Steps** (via build.sh):
1. Install dependencies from `requirements-render.txt`
2. Set environment variables (DATABASE_URL, SESSION_SECRET)
3. Run database migrations: `flask db upgrade`
4. Verify database schema: `python verify_db.py`
5. Start with Gunicorn using configuration in `gunicorn.conf.py`

## Docker
**Dockerfile**: Present in repository root (840 B)
**Base Image**: Python 3.11-slim
**Entry Point**: `gunicorn -c gunicorn.conf.py main:app`
**Port**: 5000 (mapped via Render config)
**Health Check**: HTTP GET to `/health` endpoint (30s interval)
**Process User**: Non-root user `app` for security

**Docker Configuration**:
- Minimal runtime dependencies (curl for health checks)
- Multi-layer caching strategy with requirements copy before source
- Volume ready for uploads at `/app/static/uploads`

## Deployment Configuration
**Render Deployment** (`render.yaml`):
- Service: Python web service
- Build Command: `./build.sh`
- Start Command: `gunicorn -c gunicorn.conf.py main:app`
- Database: PostgreSQL 16 on Render
- Health Check Path: `/health`
- Auto-migration on startup: `true`

**Gunicorn Configuration** (`gunicorn.conf.py`):
- Workers: 2 (configurable via WEB_CONCURRENCY)
- Worker Class: Sync
- Timeout: 30 seconds
- Max Requests: 1000 (memory leak prevention)
- Preload App: Enabled

**Replit Configuration** (`replit.nix`):
- Modules: Python 3.11, PostgreSQL 16
- Deployment: Autoscale
- Runtime: Gunicorn binding to 0.0.0.0:5000

## Database & Migrations
**Migration Tool**: Alembic (via Flask-Migrate)
**Location**: `migrations/versions/` directory
**Configuration**: `migrations/alembic.ini` and `migrations/env.py`
**Auto-Migration**: Enabled on startup (can be disabled with AUTO_MIGRATE_ON_STARTUP=false)
**Schema**: Multi-tenant support with tenant-specific tables and prefixes

## Configuration
**Environment Variables**:
- `ENVIRONMENT`: development or production
- `DEV_DATABASE_URL`: PostgreSQL connection string for development
- `PROD_DATABASE_URL`: PostgreSQL connection string for production
- `DEV_SESSION_SECRET`: Session encryption key for development
- `PROD_SESSION_SECRET`: Session encryption key for production
- `AUTO_MIGRATE_ON_STARTUP`: Auto-run migrations on app startup (true/false)
- `MAX_CONTENT_LENGTH`: Maximum upload file size (default 1MB)
- `UPLOAD_FOLDER`: Path for file uploads
- `PORT`: Server port (default 5000)
- `WEB_CONCURRENCY`: Gunicorn worker count (default 2)

## Testing
**Framework**: pytest 7.0.0+
**Test Discovery**: No test files found in repository root
**Test Command**: Would use `pytest` (framework configured but tests may be in development)
**Note**: Production-focused codebase with utility scripts for validation rather than formal test suite

## Main Entry Points
- **Application**: `main.py` - Loads environment, imports app and routes, starts Gunicorn or Flask dev server
- **Core App**: `app.py` - Flask app initialization with database, session, and Jinja2 configuration
- **Routes**: Multiple route modules loaded in main.py:
  - `routes.py` (121 KB) - Primary application routes
  - `routes_tenant_company.py` - Tenant/company hierarchy
  - `routes_team_documents.py` - Team and documents module
  - `routes_enhancements.py` - Employee editing and reporting
  - `routes_masters.py` - Master data management
  - `routes_bulk_upload.py` - Bulk employee import
  - `routes_access_control.py` - Access control management
  - `routes_tenant_config.py` - Tenant configuration
  - `routes_leave.py` - Leave management

## Key Features & Modules
- **Attendance Management**: Daily tracking, bulk attendance import
- **Payroll System**: Salary calculation, payslip generation, tax computation
- **Leave Management**: Leave types, requests, approvals
- **Employee Management**: Profile, designation, hierarchy, certifications
- **Access Control**: Role-based permissions, user access levels
- **Reports**: Various HR analytics and exports
- **Multi-Tenancy**: Support for multiple organizations/tenants
- **Compliance**: Document management, certification tracking
- **Team Collaboration**: Team documents, communication
- **Master Data**: Roles, departments, working hours, schedules

## Database Models
**Key Tables** (from models.py ~39.6 KB):
- User (authentication and authorization)
- Employee (core employee data)
- Attendance (daily records)
- Leave (leave applications)
- Payroll (salary and payment data)
- Designation (job titles and levels)
- Department (organizational units)
- Company/Tenant (multi-tenant support)
- Roles/Access Control (permission management)
- Documents, Certifications, Appraisals, Claims

## CLI Commands
**Available Commands** (via `cli_commands.py`):
- Database setup and initialization
- User management
- Data seeding and validation
- Payroll operations
- Migration utilities

