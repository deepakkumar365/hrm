#!/usr/bin/env python3
"""
Verify that database migration auto-run is properly configured.
This script checks:
1. Environment variables are set correctly
2. Required migration files exist
3. Database connectivity
4. Migration status
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(message):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {message}")
    print('='*60)

def print_status(status, message):
    """Print status message with icon"""
    icons = {
        'ok': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    }
    print(f"{icons.get(status, '  ')} {message}")

def check_environment_variables():
    """Check if required environment variables are set"""
    print_header("Checking Environment Variables")
    
    env_vars = {
        'ENVIRONMENT': os.environ.get('ENVIRONMENT', 'not set'),
        'AUTO_MIGRATE_ON_STARTUP': os.environ.get('AUTO_MIGRATE_ON_STARTUP', 'not set'),
        'DEV_DATABASE_URL': os.environ.get('DEV_DATABASE_URL', 'not set')[:30] + '...',
        'PROD_DATABASE_URL': os.environ.get('PROD_DATABASE_URL', 'not set')[:30] + '...',
    }
    
    for key, value in env_vars.items():
        if value == 'not set':
            print_status('warning', f"{key}: {value}")
        else:
            print_status('ok', f"{key}: {value}")
    
    auto_migrate = os.environ.get('AUTO_MIGRATE_ON_STARTUP', '').lower()
    if auto_migrate in ['true', '1', 'yes']:
        print_status('ok', "Auto-migration is ENABLED")
        return True
    else:
        print_status('warning', "Auto-migration is DISABLED")
        return False

def check_migration_files():
    """Check if migration files exist"""
    print_header("Checking Migration Files")
    
    migrations_dir = Path('migrations')
    
    if not migrations_dir.exists():
        print_status('error', "migrations/ directory not found")
        return False
    
    print_status('ok', "migrations/ directory exists")
    
    # Check for alembic config
    alembic_ini = migrations_dir / 'alembic.ini'
    if alembic_ini.exists():
        print_status('ok', "alembic.ini found")
    else:
        print_status('warning', "alembic.ini not found")
    
    # Check for env.py
    env_py = migrations_dir / 'env.py'
    if env_py.exists():
        print_status('ok', "env.py found")
    else:
        print_status('error', "env.py not found")
        return False
    
    # Check for versions directory
    versions_dir = migrations_dir / 'versions'
    if versions_dir.exists():
        py_migrations = list(versions_dir.glob('*.py'))
        sql_migrations = list(versions_dir.glob('*.sql'))
        total = len(py_migrations) + len(sql_migrations)
        print_status('ok', f"versions/ found with {total} migrations")
        print(f"     - Python migrations: {len(py_migrations)}")
        print(f"     - SQL migrations: {len(sql_migrations)}")
    else:
        print_status('warning', "versions/ directory not found")
    
    return True

def check_routes_py():
    """Check if routes.py has migration checking code"""
    print_header("Checking routes.py Implementation")
    
    routes_file = Path('routes.py')
    if not routes_file.exists():
        print_status('error', "routes.py not found")
        return False
    
    content = routes_file.read_text()
    
    checks = {
        'check_and_run_migrations': "Migration checker function",
        '_migrations_applied': "One-time execution flag",
        'AUTO_MIGRATE_ON_STARTUP': "Environment variable usage",
        'flask_migrate': "Migration framework import",
    }
    
    for code_check, description in checks.items():
        if code_check in content:
            print_status('ok', f"Found: {description}")
        else:
            print_status('warning', f"Missing: {description}")
    
    if len(checks) == sum(1 for check in checks if check in content):
        return True
    return False

def check_database_connection():
    """Check if database is accessible"""
    print_header("Checking Database Connection")
    
    try:
        from app import app, db
        with app.app_context():
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1'))
            print_status('ok', "Database connection successful")
            
            # Check for required tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['hrm_users', 'hrm_employees', 'hrm_roles']
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                print_status('warning', f"Missing tables: {', '.join(missing_tables)}")
                print_status('info', "Run: flask db upgrade")
                return False
            else:
                print_status('ok', "All required tables exist")
                return True
    except Exception as e:
        print_status('error', f"Database connection failed: {e}")
        return False

def check_migration_status():
    """Check current migration status"""
    print_header("Checking Migration Status")
    
    try:
        result = subprocess.run(
            ['flask', 'db', 'current'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print_status('ok', f"Current migration: {result.stdout.strip()}")
        else:
            print_status('warning', "Could not determine migration status")
            if result.stderr:
                print(f"     Error: {result.stderr}")
        
        # Show migration history
        history_result = subprocess.run(
            ['flask', 'db', 'history', '--verbose'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if history_result.returncode == 0 and history_result.stdout:
            lines = history_result.stdout.strip().split('\n')
            print_status('ok', f"Migration history ({len(lines)} entries):")
            for line in lines[-5:]:  # Show last 5
                print(f"     {line}")
    except Exception as e:
        print_status('warning', f"Could not check migration status: {e}")

def print_summary(results):
    """Print summary of checks"""
    print_header("Summary")
    
    critical = results.get('env_vars', False)
    important = results.get('migration_files', False)
    code = results.get('routes', False)
    db_connected = results.get('database', False)
    
    print(f"Environment: {'✅' if critical else '❌'}")
    print(f"Migration files: {'✅' if important else '❌'}")
    print(f"Code implementation: {'✅' if code else '❌'}")
    print(f"Database: {'✅' if db_connected else '❌'}")
    
    print()
    if critical and important and code:
        print_status('ok', "All checks passed! Auto-migration is ready.")
        print()
        print("Next steps:")
        print("1. Ensure AUTO_MIGRATE_ON_STARTUP is set in your environment")
        print("2. Run: flask db upgrade (if tables don't exist)")
        print("3. Start the app: python main.py")
        return True
    else:
        print_status('error', "Some checks failed. See above for details.")
        return False

def main():
    """Main verification function"""
    print("\n" + "="*60)
    print("  DATABASE MIGRATION AUTO-RUN VERIFICATION")
    print("="*60)
    
    results = {
        'env_vars': check_environment_variables(),
        'migration_files': check_migration_files(),
        'routes': check_routes_py(),
        'database': check_database_connection(),
    }
    
    check_migration_status()
    
    success = print_summary(results)
    
    print("\n" + "="*60)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())