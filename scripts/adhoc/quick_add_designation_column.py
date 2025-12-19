#!/usr/bin/env python3
"""Quick fix to add designation_id column"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        print("Adding designation_id column to hrm_employee...")
        
        # Check if column exists
        inspector_result = db.session.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='hrm_employee' AND column_name='designation_id'
        """)).fetchone()
        
        if inspector_result:
            print("✓ Column already exists")
        else:
            # Add column
            db.session.execute(text("""
                ALTER TABLE hrm_employee 
                ADD COLUMN designation_id INTEGER
            """))
            
            # Add foreign key
            try:
                db.session.execute(text("""
                    ALTER TABLE hrm_employee 
                    ADD CONSTRAINT fk_hrm_employee_designation_id 
                    FOREIGN KEY (designation_id) REFERENCES hrm_designation(id)
                """))
            except:
                pass
            
            db.session.commit()
            print("✓ Column added successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
