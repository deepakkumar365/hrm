#!/usr/bin/env python
"""
Verify migration chain and run database upgrade
Handles common PostgreSQL connection issues and provides clear feedback
"""

import sys
import os
import subprocess

def print_header(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}\n")

def print_step(msg, status="→"):
    print(f"{status} {msg}")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_warning(msg):
    print(f"⚠️  {msg}")

def main():
    os.chdir(r'D:\Projects\HRMS\hrm')
    
    print_header("HRMS Database Migration Verification & Upgrade")
    
    print_step("Step 1: Checking Python environment")
    print(f"  Python: {sys.version}")
    print(f"  Location: {sys.executable}")
    
    print_step("Step 2: Verifying project structure")
    if os.path.exists('migrations/versions'):
        migration_files = [f for f in os.listdir('migrations/versions') if f.endswith('.py')]
        print_success(f"Found {len(migration_files)} migration files")
    else:
        print_error("migrations/versions directory not found")
        return False
    
    print_step("Step 3: Checking Flask and required packages")
    try:
        import flask
        import flask_migrate
        import sqlalchemy
        print_success(f"Flask {flask.__version__} is installed")
        print_success(f"Flask-Migrate is installed")
        print_success(f"SQLAlchemy {sqlalchemy.__version__} is installed")
    except ImportError as e:
        print_error(f"Missing dependency: {e}")
        print("  Run: pip install -r requirements.txt")
        return False
    
    print_header("Running Database Migration")
    print_step("Executing: flask db upgrade")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'flask', 'db', 'upgrade'],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print()
            print_header("Migration Completed Successfully")
            print_success("Database has been upgraded")
            print()
            print("Next steps:")
            print("  1. Start Flask: python main.py")
            print("  2. Navigate to Masters → Employee Groups")
            print("  3. Test Leave Allocation configuration")
            print("  4. Verify access control (HR Manager, Tenant Admin roles)")
            return True
        else:
            print()
            print_error("Migration failed")
            print("  Check error messages above for details")
            return False
            
    except Exception as e:
        print()
        print_error(f"Error running migration: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)