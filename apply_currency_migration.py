#!/usr/bin/env python
"""
Direct migration application script
Run: python apply_currency_migration.py
"""

import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def apply_migration():
    try:
        print("🔄 Initializing Flask app...")
        from main import app
        
        with app.app_context():
            print("📊 Setting up database context...")
            from flask_sqlalchemy import SQLAlchemy
            from flask_migrate import Migrate, upgrade
            
            print("🚀 Applying migrations...")
            upgrade()
            
            print("\n✅ SUCCESS! Migration applied successfully!")
            print("   ✓ Added currency_code column to hrm_company")
            print("   ✓ Default value: SGD")
            
            # Verify
            from sqlalchemy import text
            from main import db
            result = db.session.execute(text("SELECT COUNT(*) as count FROM hrm_company"))
            count = result.fetchone()[0]
            print(f"   ✓ Verified: {count} companies in database")
            
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print(f"\n📋 Troubleshooting:")
        print("   1. Make sure your .env file has DATABASE_URL configured")
        print("   2. Ensure PostgreSQL is running")
        print("   3. Check your database connection")
        return False

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)