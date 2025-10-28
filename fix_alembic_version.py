#!/usr/bin/env python
"""Fix alembic_version table to allow longer revision names"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # First, let's check the current structure
        result = db.session.execute(
            text("SELECT * FROM alembic_version LIMIT 5")
        ).fetchall()
        
        print("Current alembic_version entries:")
        for row in result:
            print(f"  {row}")
        
        # Try to update the table structure if needed (PostgreSQL specific)
        try:
            db.session.execute(
                text("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE varchar(100)")
            )
            db.session.commit()
            print("Successfully extended alembic_version.version_num to 100 characters")
        except Exception as e:
            print(f"Note: Could not alter column (may already be wide enough): {e}")
            db.session.rollback()
        
        # Now mark the migration as applied
        result = db.session.execute(
            text("SELECT * FROM alembic_version WHERE version_num = 'add_attendance_lop_payroll_fields'")
        ).fetchone()
        
        if not result:
            # Delete old entry if it exists
            db.session.execute(
                text("DELETE FROM alembic_version WHERE version_num = 'add_payroll_enhancements'")
            )
            # Insert new entry
            db.session.execute(
                text("INSERT INTO alembic_version (version_num) VALUES ('add_attendance_lop_payroll_fields')")
            )
            db.session.commit()
            print("Marked add_attendance_lop_payroll_fields as applied")
        else:
            print("add_attendance_lop_payroll_fields already marked as applied")
            
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()