#!/usr/bin/env python3
"""
Verify that all required database columns exist
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from app import db, create_app
from models import Employee

def verify_employee_schema():
    """Verify all columns in Employee model exist in database"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Get database connection
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            print("=" * 70)
            print("✓ DATABASE SCHEMA VERIFICATION")
            print("=" * 70)
            
            # Get expected columns from model
            expected_columns = {col.name for col in Employee.__table__.columns}
            
            # Get actual columns from database
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'hrm_employee'
                ORDER BY ordinal_position
            """)
            
            actual_columns = {row[0] for row in cursor.fetchall()}
            
            print(f"\n📊 Schema Status:")
            print(f"   Expected columns (from model): {len(expected_columns)}")
            print(f"   Actual columns (in database):  {len(actual_columns)}")
            
            # Check for missing columns
            missing = expected_columns - actual_columns
            extra = actual_columns - expected_columns
            
            if not missing and not extra:
                print(f"\n✅ SCHEMA IS UP TO DATE!")
                print(f"   All {len(expected_columns)} columns are present and correct")
                cursor.close()
                connection.close()
                return True
            
            if missing:
                print(f"\n⚠️  MISSING COLUMNS ({len(missing)}):")
                for col in sorted(missing):
                    print(f"   - {col}")
            
            if extra:
                print(f"\n⚠️  EXTRA COLUMNS ({len(extra)}):")
                for col in sorted(extra):
                    print(f"   - {col}")
            
            if missing:
                print(f"\n💡 FIX: Run 'flask db upgrade' or 'python fix_database_schema.py'")
            
            print("\n" + "=" * 70)
            
            cursor.close()
            connection.close()
            
            return len(missing) == 0
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            print(f"   Make sure DATABASE_URL is set in .env and database is running")
            return False

def test_employee_query():
    """Try to query an employee to verify the schema works"""
    
    print("\n" + "=" * 70)
    print("✓ TESTING EMPLOYEE QUERY")
    print("=" * 70)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Try to query employees
            count = Employee.query.count()
            print(f"\n✅ QUERY SUCCESSFUL!")
            print(f"   Found {count} employees in database")
            
            # Try to access the new column
            emp = Employee.query.first()
            if emp:
                print(f"\n   Employee: {emp.first_name} {emp.last_name}")
                print(f"   Has designation_id column: {hasattr(emp, 'designation_id')}")
                if hasattr(emp, 'designation_id'):
                    print(f"   Designation ID value: {emp.designation_id}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ QUERY FAILED: {str(e)}")
            return False

if __name__ == '__main__':
    print("\n")
    schema_ok = verify_employee_schema()
    query_ok = test_employee_query()
    
    print("\n" + "=" * 70)
    if schema_ok and query_ok:
        print("✅ ALL CHECKS PASSED - DATABASE IS READY!")
    else:
        print("❌ SOME CHECKS FAILED - SEE ABOVE FOR DETAILS")
    print("=" * 70 + "\n")
    
    sys.exit(0 if (schema_ok and query_ok) else 1)