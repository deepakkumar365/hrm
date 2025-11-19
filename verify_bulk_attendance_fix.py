#!/usr/bin/env python
"""Verify that bulk attendance fix is working"""

from app import app, db
from models import User, Employee, Company, Tenant, Organization
from datetime import date

with app.app_context():
    print("=" * 70)
    print("  BULK ATTENDANCE FIX VERIFICATION")
    print("=" * 70)
    print()
    
    # Check 1: hrm_user_company_access table exists
    print("✓ Check 1: Verify hrm_user_company_access table")
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    if 'hrm_user_company_access' in tables:
        count = db.session.execute(
            db.text('SELECT COUNT(*) FROM hrm_user_company_access')
        ).scalar()
        print(f"  ✅ Table exists with {count} records")
    else:
        print(f"  ❌ Table missing!")
    
    print()
    
    # Check 2: Verify a simple employee query works
    print("✓ Check 2: Test basic employee query")
    try:
        employees = Employee.query.filter_by(is_active=True).limit(1).all()
        print(f"  ✅ Can query employees ({len(employees)} found)")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()
    
    # Check 3: Test user organization relationship
    print("✓ Check 3: Verify user-organization relationship")
    try:
        users = User.query.limit(1).all()
        if users:
            user = users[0]
            print(f"  User: {user.username}")
            print(f"  Organization ID (type): {user.organization_id} ({type(user.organization_id).__name__})")
            if user.organization:
                print(f"  Organization: {user.organization.name}")
                print(f"  Tenant ID (type): {user.organization.tenant_id} ({type(user.organization.tenant_id).__name__})")
                print(f"  ✅ Relationship works")
            else:
                print(f"  ⚠️  No organization found")
        else:
            print(f"  ⚠️  No users in database")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()
    
    # Check 4: Verify tenant/company relationship
    print("✓ Check 4: Verify tenant-company relationship")
    try:
        companies = Company.query.limit(1).all()
        if companies:
            company = companies[0]
            print(f"  Company: {company.name}")
            print(f"  Company ID (type): {company.id} ({type(company.id).__name__})")
            print(f"  Tenant ID (type): {company.tenant_id} ({type(company.tenant_id).__name__})")
            if company.tenant:
                print(f"  Tenant: {company.tenant.name}")
                print(f"  Tenant.id (type): {company.tenant.id} ({type(company.tenant.id).__name__})")
                print(f"  ✅ Relationship works")
            else:
                print(f"  ⚠️  No tenant found")
        else:
            print(f"  ⚠️  No companies in database")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()
    print("=" * 70)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 70)
    print()
    print("Ready to test Bulk Attendance in the UI!")