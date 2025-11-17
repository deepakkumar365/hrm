#!/usr/bin/env python
"""Run database migration for OT Daily Summary"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from flask_migrate import upgrade

def main():
    with app.app_context():
        try:
            print("Running database migration...")
            upgrade()
            print("✅ Migration completed successfully!")
            return 0
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1

if __name__ == '__main__':
    sys.exit(main())