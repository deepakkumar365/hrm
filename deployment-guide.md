# Noltrion Render Deployment Guide

## Required Files for Render Deployment

The following files are required to deploy Noltrion HRM system on Render:

### 1. `render.yaml` - Main deployment configuration
Configures the web service and PostgreSQL database with automatic environment variables.

### 2. `requirements-render.txt` - Python dependencies
Contains all required Python packages for the Flask application.

### 3. `Dockerfile` - Container configuration
Defines the Docker container for the application with health checks.

### 4. `.env.example` - Environment variables template
Shows the required environment variables (don't deploy this file).

## Deployment Steps

### Option 1: Using render.yaml (Recommended)

1. **Connect your GitHub repository to Render**
2. **Create a new "Blueprint" on Render**
3. **Upload the render.yaml file** - Render will automatically:
   - Create the web service
   - Set up PostgreSQL database
   - Configure environment variables
   - Set up health checks

### Option 2: Manual Setup

1. **Create PostgreSQL Database:**
   - Go to Render Dashboard
   - Create new PostgreSQL database
   - Name: `noltrion-db`
   - Save the connection string

2. **Create Web Service:**
   - Create new Web Service
   - Connect your repository
   - Build Command: `pip install -r requirements-render.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 1 main:app`

3. **Set Environment Variables:**
   - `DATABASE_URL`: (Copy from PostgreSQL database)
   - `SESSION_SECRET`: Generate a random secret key
   - `PYTHON_VERSION`: 3.11.4

## Environment Variables

### Required Variables:
- **DATABASE_URL**: PostgreSQL connection string from Render database
- **SESSION_SECRET**: Random secret key for Flask sessions (auto-generated in render.yaml)
- **PYTHON_VERSION**: Python version (set to 3.11.4)

### Database Setup:
The application will automatically:
- Create all database tables on first run
- Set up default master data (roles, departments, etc.)
- Create default user accounts (superadmin, admin, manager, user)

## Default Login Credentials (Change immediately):
- **Super Admin**: username `superadmin`, password `superadmin123`
- **Admin**: username `admin`, password `admin123`
- **Manager**: username `manager`, password `manager123`
- **User**: username `user`, password `user123`

## Health Check:
The application includes a `/health` endpoint that:
- Checks database connectivity
- Returns status for Render monitoring
- Automatically restarts if unhealthy

## Security Notes:
1. Change all default passwords immediately after deployment
2. Use a strong SESSION_SECRET in production
3. The render.yaml generates SESSION_SECRET automatically for security
4. Database credentials are managed securely by Render

## Post-Deployment:
1. Access your application at the Render-provided URL
2. Log in with Super Admin credentials
3. Change default passwords
4. Set up your master data (roles, departments, working hours, schedules)
5. Start adding employees - they'll get automatic user accounts!