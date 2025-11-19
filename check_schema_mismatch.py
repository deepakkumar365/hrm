#!/usr/bin/env python
"""Diagnose schema type mismatches"""

from app import app, db
from sqlalchemy import text, inspect

with app.app_context():
    inspector = inspect(db.engine)
    
    print("=" * 70)
    print("  SCHEMA TYPE MISMATCH DIAGNOSIS")
    print("=" * 70)
    print()
    
    # Check hrm_tenant columns
    print("📋 hrm_tenant columns:")
    tenant_cols = inspector.get_columns('hrm_tenant')
    for col in tenant_cols:
        if col['name'] in ['id', 'code', 'is_active']:
            print(f"   {col['name']}: {col['type']}")
    
    print()
    print("📋 hrm_company columns:")
    company_cols = inspector.get_columns('hrm_company')
    for col in company_cols:
        if col['name'] in ['id', 'tenant_id']:
            print(f"   {col['name']}: {col['type']}")
    
    print()
    print("📋 hrm_employee columns:")
    employee_cols = inspector.get_columns('hrm_employee')
    for col in employee_cols:
        if col['name'] in ['id', 'company_id']:
            print(f"   {col['name']}: {col['type']}")
    
    # Check actual data
    print()
    print("📊 Sample tenant data:")
    result = db.session.execute(text('SELECT id FROM hrm_tenant LIMIT 1')).fetchone()
    if result:
        print(f"   First tenant id: {result[0]} (type: {type(result[0]).__name__})")
    
    print()
    print("📊 Sample company data:")
    result = db.session.execute(text('SELECT id, tenant_id FROM hrm_company LIMIT 1')).fetchone()
    if result:
        print(f"   First company id: {result[0]} (type: {type(result[0]).__name__})")
        print(f"   First company tenant_id: {result[1]} (type: {type(result[1]).__name__})")