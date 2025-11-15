#!/usr/bin/env python
"""Check if employee_group tables exist and create them if needed"""

from app import db, app
from models import EmployeeGroup, DesignationLeaveAllocation, EmployeeGroupLeaveAllocation, EmployeeLeaveAllocation

with app.app_context():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    print('=' * 70)
    print('CHECKING EMPLOYEE GROUP TABLES')
    print('=' * 70)
    print()
    
    required_tables = {
        'hrm_employee_group': EmployeeGroup,
        'hrm_designation_leave_allocation': DesignationLeaveAllocation,
        'hrm_employee_group_leave_allocation': EmployeeGroupLeaveAllocation,
        'hrm_employee_leave_allocation': EmployeeLeaveAllocation,
    }
    
    missing = []
    for table_name, model_class in required_tables.items():
        exists = table_name in tables
        status = 'OK' if exists else 'MISSING'
        print(f'[{status}] {table_name}')
        if not exists:
            missing.append((table_name, model_class))
    
    print()
    if missing:
        print(f'Creating {len(missing)} missing table(s)...')
        print('=' * 70)
        try:
            # Create all tables from models
            db.create_all()
            print('All tables created successfully!')
            print()
            
            # Verify they were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            for table_name in required_tables:
                exists = table_name in tables
                status = 'OK' if exists else 'MISSING'
                print(f'[{status}] {table_name}')
        except Exception as e:
            print(f'Error creating tables: {e}')
    else:
        print('ALL REQUIRED TABLES EXIST!')
    
    print()
    print('=' * 70)
    print('COMPLETE DATABASE TABLE LIST:')
    print('=' * 70)
    all_tables = sorted(inspector.get_table_names())
    for table in all_tables:
        print(f'  {table}')