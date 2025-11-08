#!/usr/bin/env python3
"""
Check if the hrm_company_employee_id_config table exists in the database.
"""

from app import app, db
from sqlalchemy import text, inspect

def check_table():
    with app.app_context():
        print("\n" + "="*80)
        print("CHECKING DATABASE TABLES")
        print("="*80)
        
        try:
            # Get all table names
            inspector = inspect(db.engine)
            all_tables = inspector.get_table_names()
            
            print(f"\n📊 Total tables in database: {len(all_tables)}")
            print("\n📋 All tables:")
            print("-" * 80)
            for table in sorted(all_tables):
                print(f"  • {table}")
            print("-" * 80)
            
            # Check for our specific table
            target_table = 'hrm_company_employee_id_config'
            print(f"\n🔍 Looking for table: '{target_table}'...")
            
            if target_table in all_tables:
                print(f"✅ TABLE FOUND!")
                
                # Get table columns
                columns = inspector.get_columns(target_table)
                print(f"\n📝 Columns in {target_table}:")
                for col in columns:
                    print(f"   - {col['name']:25} {str(col['type']):20}")
                
                # Check row count
                try:
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {target_table}"))
                    count = result.scalar()
                    print(f"\n📊 Records in table: {count}")
                except Exception as e:
                    print(f"⚠️  Could not count records: {str(e)}")
                
            else:
                print(f"❌ TABLE NOT FOUND!")
                print(f"\n💡 Table '{target_table}' does NOT exist in your database.")
                print("\nYou need to run: python init_company_id_config_now.py")
            
            # Also check if model exists
            print("\n" + "-" * 80)
            print("Checking if model class exists...")
            try:
                from models import CompanyEmployeeIdConfig
                print("✅ CompanyEmployeeIdConfig model class EXISTS")
            except ImportError as e:
                print(f"❌ CompanyEmployeeIdConfig model class NOT FOUND: {e}")
            
            print("\n" + "="*80)
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            print("="*80)

if __name__ == '__main__':
    check_table()