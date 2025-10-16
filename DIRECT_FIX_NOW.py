#!/usr/bin/env python
"""
DIRECT DATABASE FIX - Bypasses broken migration system
This directly adds the missing designation_id column
"""
import os
import sys
from app import db, create_app

def add_missing_columns():
    """Add all missing columns directly to database"""
    
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("🔧 DIRECT DATABASE FIX - ADDING MISSING COLUMNS")
        print("="*70)
        
        # Columns that need to be added based on Employee model
        missing_columns = {
            'designation_id': 'INTEGER',
            'work_schedule_id': 'UUID',
        }
        
        for col_name, col_type in missing_columns.items():
            try:
                # Check if column already exists
                result = db.session.execute(db.text(f"""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name='hrm_employee' AND column_name='{col_name}'
                """))
                
                if result.fetchone():
                    print(f"\n✅ Column {col_name} already exists - skipping")
                    continue
                
                print(f"\n⏳ Adding column: {col_name} ({col_type})")
                
                # Add the column
                if col_type == 'UUID':
                    db.session.execute(db.text(f"""
                        ALTER TABLE hrm_employee 
                        ADD COLUMN {col_name} UUID NULL
                    """))
                else:
                    db.session.execute(db.text(f"""
                        ALTER TABLE hrm_employee 
                        ADD COLUMN {col_name} {col_type} NULL
                    """))
                
                db.session.commit()
                print(f"   ✅ Column added successfully!")
                
                # Add foreign key for designation_id
                if col_name == 'designation_id':
                    try:
                        db.session.execute(db.text("""
                            ALTER TABLE hrm_employee 
                            ADD CONSTRAINT fk_hrm_employee_designation_id 
                            FOREIGN KEY (designation_id) REFERENCES hrm_designation(id)
                        """))
                        db.session.commit()
                        print(f"   ✅ Foreign key added successfully!")
                    except Exception as e:
                        if 'already exists' in str(e):
                            print(f"   ℹ️  Foreign key already exists")
                        else:
                            print(f"   ⚠️  Foreign key creation failed: {e}")
                            db.session.rollback()
                
            except Exception as e:
                print(f"   ❌ Error adding {col_name}: {e}")
                db.session.rollback()
                return False
        
        print("\n" + "="*70)
        print("✅ DATABASE FIX COMPLETE")
        print("="*70)
        
        # Verify the fix
        print("\n🔍 VERIFICATION:")
        try:
            result = db.session.execute(db.text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name='hrm_employee' AND column_name='designation_id'
            """))
            if result.fetchone():
                print("   ✅ designation_id column now EXISTS in database!")
            else:
                print("   ❌ designation_id column still missing!")
                return False
        except Exception as e:
            print(f"   ❌ Verification failed: {e}")
            return False
        
        # Try a test query
        print("\n🧪 TESTING EMPLOYEE QUERY:")
        try:
            from models import Employee
            emp = Employee.query.first()
            if emp:
                print(f"   ✅ Query successful! Found employee: {emp.first_name}")
            else:
                print("   ✅ Query successful! (No employees in database yet)")
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
            return False
        
        print("\n" + "="*70)
        print("🎉 SUCCESS! Database is fixed and ready to use")
        print("="*70 + "\n")
        return True

if __name__ == '__main__':
    success = add_missing_columns()
    sys.exit(0 if success else 1)