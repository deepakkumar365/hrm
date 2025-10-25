#!/usr/bin/env python
"""Manually add missing columns to the database"""
from app import app, db
from sqlalchemy import text, inspect

with app.app_context():
    try:
        inspector = inspect(db.engine)
        
        # Add LOP column to hrm_attendance if it doesn't exist
        attendance_cols = [col['name'] for col in inspector.get_columns('hrm_attendance')]
        if 'lop' not in attendance_cols:
            db.session.execute(
                text("ALTER TABLE hrm_attendance ADD COLUMN lop BOOLEAN DEFAULT false")
            )
            db.session.commit()
            print("✓ Added lop column to hrm_attendance")
        else:
            print("✓ lop column already exists in hrm_attendance")
        
        # Add Levy Allowance fields to hrm_payroll_configuration if they don't exist
        payroll_config_cols = [col['name'] for col in inspector.get_columns('hrm_payroll_configuration')]
        
        if 'levy_allowance_name' not in payroll_config_cols:
            db.session.execute(
                text("ALTER TABLE hrm_payroll_configuration ADD COLUMN levy_allowance_name VARCHAR(100)")
            )
            db.session.commit()
            print("✓ Added levy_allowance_name column to hrm_payroll_configuration")
        else:
            print("✓ levy_allowance_name column already exists")
        
        if 'levy_allowance_amount' not in payroll_config_cols:
            db.session.execute(
                text("ALTER TABLE hrm_payroll_configuration ADD COLUMN levy_allowance_amount NUMERIC(10, 2) DEFAULT 0")
            )
            db.session.commit()
            print("✓ Added levy_allowance_amount column to hrm_payroll_configuration")
        else:
            print("✓ levy_allowance_amount column already exists")
        
        # Add new columns to hrm_payroll if they don't exist
        payroll_cols = [col['name'] for col in inspector.get_columns('hrm_payroll')]
        
        if 'absent_days' not in payroll_cols:
            db.session.execute(
                text("ALTER TABLE hrm_payroll ADD COLUMN absent_days INTEGER DEFAULT 0")
            )
            db.session.commit()
            print("✓ Added absent_days column to hrm_payroll")
        else:
            print("✓ absent_days column already exists")
        
        if 'lop_days' not in payroll_cols:
            db.session.execute(
                text("ALTER TABLE hrm_payroll ADD COLUMN lop_days INTEGER DEFAULT 0")
            )
            db.session.commit()
            print("✓ Added lop_days column to hrm_payroll")
        else:
            print("✓ lop_days column already exists")
        
        if 'lop_deduction' not in payroll_cols:
            db.session.execute(
                text("ALTER TABLE hrm_payroll ADD COLUMN lop_deduction NUMERIC(10, 2) DEFAULT 0")
            )
            db.session.commit()
            print("✓ Added lop_deduction column to hrm_payroll")
        else:
            print("✓ lop_deduction column already exists")
        
        print("\n✓ All missing columns have been added successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()