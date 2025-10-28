#!/usr/bin/env python
"""Fix migration history to properly track the LOP migration"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Mark the add_payroll_enhancements migration as applied if not already there
        result = db.session.execute(
            text("SELECT * FROM alembic_version WHERE version_num = 'add_payroll_enhancements'")
        ).fetchone()
        
        if not result:
            db.session.execute(
                text("INSERT INTO alembic_version (version_num) VALUES ('add_payroll_enhancements')")
            )
            db.session.commit()
            print("Marked add_payroll_enhancements as applied")
        else:
            print("add_payroll_enhancements already marked as applied")
            
        # Now check if LOP migration needs to be applied
        result = db.session.execute(
            text("SELECT * FROM alembic_version WHERE version_num = 'add_attendance_lop_payroll_fields'")
        ).fetchone()
        
        if not result:
            print("LOP migration not yet applied - will need to run it")
        else:
            print("LOP migration already applied")
            
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()