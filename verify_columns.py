#!/usr/bin/env python
"""Verify that the new columns exist in the database"""
from app import app, db
from sqlalchemy import text, inspect

with app.app_context():
    try:
        inspector = inspect(db.engine)
        
        # Check hrm_attendance table
        attendance_cols = inspector.get_columns('hrm_attendance')
        print("hrm_attendance columns:")
        for col in attendance_cols:
            print(f"  - {col['name']} ({col['type']})")
        
        if any(col['name'] == 'lop' for col in attendance_cols):
            print("  ✓ LOP column exists!")
        else:
            print("  ✗ LOP column MISSING!")
        
        # Check hrm_payroll_configuration table
        print("\nhrm_payroll_configuration columns:")
        payroll_config_cols = inspector.get_columns('hrm_payroll_configuration')
        for col in payroll_config_cols:
            print(f"  - {col['name']} ({col['type']})")
        
        if any(col['name'] == 'levy_allowance_name' for col in payroll_config_cols):
            print("  ✓ levy_allowance_name column exists!")
        else:
            print("  ✗ levy_allowance_name column MISSING!")
            
        if any(col['name'] == 'levy_allowance_amount' for col in payroll_config_cols):
            print("  ✓ levy_allowance_amount column exists!")
        else:
            print("  ✗ levy_allowance_amount column MISSING!")
        
        # Check hrm_payroll table
        print("\nhrm_payroll columns:")
        payroll_cols = inspector.get_columns('hrm_payroll')
        for col in payroll_cols:
            print(f"  - {col['name']} ({col['type']})")
        
        if any(col['name'] == 'absent_days' for col in payroll_cols):
            print("  ✓ absent_days column exists!")
        else:
            print("  ✗ absent_days column MISSING!")
            
        if any(col['name'] == 'lop_days' for col in payroll_cols):
            print("  ✓ lop_days column exists!")
        else:
            print("  ✗ lop_days column MISSING!")
            
        if any(col['name'] == 'lop_deduction' for col in payroll_cols):
            print("  ✓ lop_deduction column exists!")
        else:
            print("  ✗ lop_deduction column MISSING!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()