#!/usr/bin/env python3
"""
Direct script to create the hrm_ot_daily_summary table
Run this from terminal while in the project directory
"""
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models import OTDailySummary

def create_table():
    """Create the OTDailySummary table in the database"""
    with app.app_context():
        try:
            print("🔍 Checking if hrm_ot_daily_summary table exists...")
            
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'hrm_ot_daily_summary' in existing_tables:
                print("✅ Table hrm_ot_daily_summary already EXISTS in database!")
                return True
            
            print("❌ Table hrm_ot_daily_summary does NOT exist. Creating it now...")
            print()
            
            # Create the table
            OTDailySummary.__table__.create(db.engine, checkfirst=True)
            db.session.commit()
            
            print("✅ Table creation command executed!")
            print()
            
            # Verify it was created
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'hrm_ot_daily_summary' in existing_tables:
                print("✅✅✅ SUCCESS! Table hrm_ot_daily_summary has been created!")
                print()
                print("📋 Table details:")
                columns = inspector.get_columns('hrm_ot_daily_summary')
                print(f"   - Total columns: {len(columns)}")
                for col in columns:
                    print(f"     • {col['name']}: {col['type']}")
                print()
                print("✅ You can now use OT Management > Payroll Summary (Grid) feature")
                return True
            else:
                print("❌ Table creation FAILED - table still does not exist")
                print("   Please check database permissions and try again")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            print()
            print("📌 Troubleshooting:")
            print("   1. Make sure PostgreSQL database is running")
            print("   2. Check your DATABASE_URL environment variable")
            print("   3. Ensure your database credentials are correct")
            print()
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("Creating OT Daily Summary Table")
    print("=" * 60)
    print()
    
    success = create_table()
    
    print()
    print("=" * 60)
    if success:
        print("✅ DONE! Table is ready to use.")
    else:
        print("❌ FAILED! See errors above.")
    print("=" * 60)
    
    sys.exit(0 if success else 1)