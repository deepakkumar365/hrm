#!/usr/bin/env python3
"""Check manager user's company assignment"""
import os
import sys
from app import app, db
from models import User, Employee

with app.app_context():
    # Get manager user
    manager_user = User.query.filter_by(username='manager').first()
    
    if not manager_user:
        print("❌ Manager user not found!")
        sys.exit(1)
    
    print(f"✅ Manager User Found:")
    print(f"   ID: {manager_user.id}")
    print(f"   Username: {manager_user.username}")
    print(f"   Email: {manager_user.email}")
    print(f"   Organization ID: {manager_user.organization_id}")
    print(f"   Role: {manager_user.role.name if manager_user.role else 'None'}")
    
    # Check employee profile
    employee = manager_user.employee_profile
    
    if not employee:
        print(f"\n❌ Manager user HAS NO employee profile!")
        print(f"   A new employee record needs to be created for this user.")
    else:
        print(f"\n✅ Manager Employee Profile Found:")
        print(f"   ID: {employee.id}")
        print(f"   Employee ID: {employee.employee_id}")
        print(f"   Name: {employee.first_name} {employee.last_name}")
        print(f"   Organization ID: {employee.organization_id}")
        print(f"   Company ID: {employee.company_id}")
        
        if not employee.company_id:
            print(f"\n❌ Employee HAS NO company assigned!")
            print(f"   Company ID is NULL - this is why the OT Type creation fails")
        else:
            print(f"\n✅ Employee has company assigned!")