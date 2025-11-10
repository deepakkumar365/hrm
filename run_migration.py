#!/usr/bin/env python
"""Run database migration to apply the leave type configuration table"""
import os
import sys
from app import app, db
from flask_migrate import upgrade as alembic_upgrade

def run_migration():
    """Apply all pending migrations"""
    with app.app_context():
        try:
            print("🔄 Running database migrations...")
            alembic_upgrade()
            print("✅ Migration completed successfully!")
            print("✅ The hrm_leave_type table has been created")
            return True
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)