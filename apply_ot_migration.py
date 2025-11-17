#!/usr/bin/env python
"""Direct migration execution for OT Daily Summary table"""
import os
import sys
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    try:
        print("🔄 Applying OT Daily Summary migration...\n")
        
        # Import app and db
        from app import app, db
        from flask_migrate import upgrade, stamp
        
        with app.app_context():
            # Try to upgrade the database
            print("📋 Running Alembic upgrade...")
            upgrade()
            
            print("\n✅ Migration completed successfully!")
            print("✅ Table 'hrm_ot_daily_summary' has been created")
            print("\n📌 You can now access the OT Payroll Summary Grid at:")
            print("   OT Management > Payroll Summary (Grid)")
            
            return 0
            
    except Exception as e:
        print(f"\n❌ Error during migration: {str(e)}\n")
        import traceback
        traceback.print_exc()
        print("\n💡 Try these solutions:")
        print("   1. Restart your Flask application (it should auto-migrate)")
        print("   2. Run: python -m flask db upgrade")
        print("   3. Or restart the development server\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())