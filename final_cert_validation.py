#!/usr/bin/env python
"""Final validation of certification fields integration"""
from app import app, db
from models import Employee
from datetime import date

app.app_context().push()

print("\n" + "=" * 70)
print("FINAL VALIDATION: Certification & Pass Renewal Fields")
print("=" * 70)

results = []

# 1. Check database schema
print("\n1️⃣  DATABASE SCHEMA")
print("-" * 70)
try:
    cols = {c.name: c.type for c in Employee.__table__.columns}
    required = ['hazmat_expiry', 'airport_pass_expiry', 'psa_pass_number', 'psa_pass_expiry']
    
    for col in required:
        if col in cols:
            print(f"   ✓ {col:<25} ({cols[col]})")
            results.append(True)
        else:
            print(f"   ✗ {col:<25} MISSING")
            results.append(False)
except Exception as e:
    print(f"   ✗ Error: {e}")
    results.append(False)

# 2. Check HTML form
print("\n2️⃣  HTML FORM (templates/employees/form.html)")
print("-" * 70)
try:
    with open('templates/employees/form.html', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        form_checks = {
            'Certifications & Pass Renewals': 'Section header',
            'hazmat_expiry': 'HAZMAT field',
            'airport_pass_expiry': 'Airport Pass field',
            'psa_pass_number': 'PSA Pass Number field',
            'psa_pass_expiry': 'PSA Pass Expiry field',
            'name="hazmat_expiry"': 'HAZMAT form input',
            'name="airport_pass_expiry"': 'Airport Pass form input',
            'name="psa_pass_number"': 'PSA Number form input',
            'name="psa_pass_expiry"': 'PSA Expiry form input',
        }
        
        for check, desc in form_checks.items():
            if check in content:
                print(f"   ✓ {desc}")
                results.append(True)
            else:
                print(f"   ✗ {desc} - '{check}' not found")
                results.append(False)
except Exception as e:
    print(f"   ✗ Error: {e}")
    results.append(False)

# 3. Check migration status
print("\n3️⃣  MIGRATION STATUS")
print("-" * 70)
try:
    from flask_migrate import Migrate
    # Just verify the migration file exists
    import os
    mig_file = 'migrations/versions/add_certification_pass_renewal_fields.py'
    if os.path.exists(mig_file):
        print(f"   ✓ Migration file exists: {mig_file}")
        results.append(True)
    else:
        print(f"   ✗ Migration file missing: {mig_file}")
        results.append(False)
except Exception as e:
    print(f"   ✗ Error: {e}")
    results.append(False)

# 4. Model attribute test
print("\n4️⃣  MODEL ATTRIBUTES")
print("-" * 70)
try:
    emp = Employee()
    attrs = ['hazmat_expiry', 'airport_pass_expiry', 'psa_pass_number', 'psa_pass_expiry']
    
    for attr in attrs:
        if hasattr(emp, attr):
            print(f"   ✓ Employee.{attr} exists")
            results.append(True)
        else:
            print(f"   ✗ Employee.{attr} missing")
            results.append(False)
except Exception as e:
    print(f"   ✗ Error: {e}")
    results.append(False)

# Summary
print("\n" + "=" * 70)
total = len(results)
passed = sum(results)
print(f"SUMMARY: {passed}/{total} checks passed")
print("=" * 70)

if passed == total:
    print("\n✅ ALL VALIDATIONS PASSED - System is ready!\n")
    exit(0)
else:
    print(f"\n⚠️  {total - passed} validation(s) failed\n")
    exit(1)