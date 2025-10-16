#!/usr/bin/env python3
"""
Complete database schema fix for hrm_employee table
This script adds any missing columns to align the database with the ORM models
"""
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

from app import db, create_app
from models import Employee
import sqlalchemy as sa

def fix_database_schema():
    """Add missing columns to hrm_employee table"""
    
    app = create_app()
    
    with app.app_context():
        # Get database connection
        connection = db.engine.raw_connection()
        cursor = connection.cursor()
        
        try:
            print("=" * 60)
            print("🔧 DATABASE SCHEMA FIX FOR hrm_employee")
            print("=" * 60)
            
            # Get all columns that should exist (from the model)
            expected_columns = {
                col.name: col for col in Employee.__table__.columns
            }
            
            # Get actual columns in database
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'hrm_employee'
                ORDER BY ordinal_position
            """)
            
            existing_columns = {row[0]: row[1] for row in cursor.fetchall()}
            
            print(f"\n📊 Current database columns: {len(existing_columns)}")
            print(f"📊 Expected model columns: {len(expected_columns)}")
            
            # Find missing columns
            missing_columns = set(expected_columns.keys()) - set(existing_columns.keys())
            
            if not missing_columns:
                print("\n✅ All columns exist! Database is up to date.")
                cursor.close()
                connection.close()
                return True
            
            print(f"\n⚠️  Missing columns ({len(missing_columns)}):")
            for col_name in sorted(missing_columns):
                print(f"   - {col_name}")
            
            # Add missing columns
            print(f"\n⏳ Adding {len(missing_columns)} missing columns...")
            
            for col_name in sorted(missing_columns):
                col = expected_columns[col_name]
                
                # Generate SQL for adding column
                col_type = str(col.type.compile(dialect=db.engine.dialect))
                nullable = "NULL" if col.nullable else "NOT NULL"
                
                # Special handling for columns with defaults or special requirements
                default_sql = ""
                if col.default is not None:
                    if callable(col.default.arg):
                        # Skip dynamic defaults like datetime.now
                        default_sql = ""
                    else:
                        default_sql = f"DEFAULT {col.default.arg}"
                
                # Build ADD COLUMN statement
                add_col_sql = f"""
                    ALTER TABLE hrm_employee 
                    ADD COLUMN {col_name} {col_type} {nullable} {default_sql}
                """.strip()
                
                try:
                    cursor.execute(add_col_sql)
                    connection.commit()
                    print(f"   ✅ Added column: {col_name} ({col_type})")
                except Exception as e:
                    connection.rollback()
                    print(f"   ⚠️  Skipped {col_name}: {str(e)}")
                    continue
                
                # Add foreign key constraints if needed
                if col.foreign_keys:
                    for fk in col.foreign_keys:
                        constraint_name = f"fk_hrm_employee_{col_name}"
                        ref_table = fk.column.table.name
                        ref_col = fk.column.name
                        
                        try:
                            fk_sql = f"""
                                ALTER TABLE hrm_employee 
                                ADD CONSTRAINT {constraint_name}
                                FOREIGN KEY ({col_name}) 
                                REFERENCES {ref_table}({ref_col})
                            """.strip()
                            cursor.execute(fk_sql)
                            connection.commit()
                            print(f"      ↳ Foreign key added: {constraint_name}")
                        except Exception as e:
                            connection.rollback()
                            print(f"      ⚠️  FK constraint skipped: {str(e)}")
            
            print("\n" + "=" * 60)
            print("✅ DATABASE SCHEMA FIX COMPLETE")
            print("=" * 60)
            print("\n💡 Tip: Run 'flask db upgrade' to apply all pending migrations")
            print("💡 Tip: Restart your application to apply changes\n")
            
            cursor.close()
            connection.close()
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            cursor.close()
            connection.close()
            return False

if __name__ == '__main__':
    success = fix_database_schema()
    sys.exit(0 if success else 1)