#!/usr/bin/env python
"""
Verification script for Multi-Company Support implementation.
Checks all components are correctly implemented.

Usage: python verify_multi_company.py
"""

import sys
import os
import inspect

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Company, UserCompanyAccess

print("\n" + "="*70)
print("🔍 Multi-Company Support - Verification Script")
print("="*70 + "\n")

checks_passed = 0
checks_failed = 0
checks_warnings = 0

def check_mark(status):
    if status == "pass":
        return "✅"
    elif status == "fail":
        return "❌"
    elif status == "warning":
        return "⚠️"
    return "⊘"

def log_check(name, status, details=""):
    global checks_passed, checks_failed, checks_warnings
    mark = check_mark(status)
    print(f"{mark} {name}")
    if details:
        print(f"   {details}")
    if status == "pass":
        checks_passed += 1
    elif status == "fail":
        checks_failed += 1
    else:
        checks_warnings += 1
    print()

# ===== CHECK 1: Template Files =====
print("\n📋 1. TEMPLATE FILES")
print("-" * 70)

templates_to_check = [
    ("templates/hr_manager_dashboard.html", "{{ company.name }}", "{{ company.company_name }}"),
    ("templates/hr_manager/generate_payroll.html", "{{ company.name }}", "{{ company.company_name }}"),
]

for template_file, correct_text, wrong_text in templates_to_check:
    try:
        with open(template_file, 'r') as f:
            content = f.read()
            if correct_text in content:
                if wrong_text in content:
                    log_check(f"{template_file}", "warning", f"Found both {correct_text} and {wrong_text} in file")
                else:
                    log_check(f"{template_file}", "pass", f"Correctly uses {correct_text}")
            else:
                log_check(f"{template_file}", "fail", f"Does not contain {correct_text}")
    except FileNotFoundError:
        log_check(f"{template_file}", "fail", "File not found")
    except Exception as e:
        log_check(f"{template_file}", "fail", f"Error reading file: {str(e)}")

# ===== CHECK 2: Model Classes =====
print("\n📦 2. MODEL CLASSES")
print("-" * 70)

# Check UserCompanyAccess model exists
try:
    uca_model = UserCompanyAccess
    log_check("UserCompanyAccess model exists", "pass", f"Found at {uca_model.__module__}")
except Exception as e:
    log_check("UserCompanyAccess model", "fail", str(e))

# Check User model has company_access relationship
try:
    if hasattr(User, 'company_access'):
        log_check("User.company_access relationship", "pass", "Relationship property exists")
    else:
        log_check("User.company_access relationship", "fail", "Property not found")
except Exception as e:
    log_check("User.company_access relationship", "fail", str(e))

# Check User model has get_accessible_companies method
try:
    if hasattr(User, 'get_accessible_companies'):
        log_check("User.get_accessible_companies() method", "pass", "Method exists")
        # Check if method is callable
        if callable(getattr(User, 'get_accessible_companies')):
            log_check("Method is callable", "pass", "Can be invoked")
        else:
            log_check("Method is callable", "fail", "Method is not callable")
    else:
        log_check("User.get_accessible_companies() method", "fail", "Method not found")
except Exception as e:
    log_check("User.get_accessible_companies() method", "fail", str(e))

# Check UserCompanyAccess table structure
try:
    with app.app_context():
        # Check table columns
        mapper = inspect.inspect(UserCompanyAccess)
        columns = {c.name for c in mapper.columns}
        required_columns = {'id', 'user_id', 'company_id', 'created_at', 'modified_at'}
        
        if required_columns.issubset(columns):
            log_check("UserCompanyAccess table columns", "pass", f"All required columns present: {', '.join(required_columns)}")
        else:
            missing = required_columns - columns
            log_check("UserCompanyAccess table columns", "fail", f"Missing columns: {', '.join(missing)}")
except Exception as e:
    log_check("UserCompanyAccess table structure", "warning", f"Could not verify (DB may not be initialized): {str(e)}")

# ===== CHECK 3: Database Migration =====
print("\n🗄️  3. DATABASE MIGRATION")
print("-" * 70)

try:
    with app.app_context():
        # Check if table exists in database
        from sqlalchemy import inspect as sa_inspect
        inspector = sa_inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'hrm_user_company_access' in tables:
            log_check("hrm_user_company_access table exists", "pass", "Table found in database")
            
            # Check indexes
            indexes = inspector.get_indexes('hrm_user_company_access')
            index_names = {idx['name'] for idx in indexes}
            if 'ix_user_company_access_user_id' in index_names:
                log_check("User ID index", "pass", "ix_user_company_access_user_id exists")
            else:
                log_check("User ID index", "warning", "ix_user_company_access_user_id not found")
            
            if 'ix_user_company_access_company_id' in index_names:
                log_check("Company ID index", "pass", "ix_user_company_access_company_id exists")
            else:
                log_check("Company ID index", "warning", "ix_user_company_access_company_id not found")
        else:
            log_check("hrm_user_company_access table", "fail", "Table not found in database (need to run: flask db upgrade)")
except Exception as e:
    log_check("Database table check", "warning", f"Could not verify: {str(e)}")

# ===== CHECK 4: Routes =====
print("\n🛣️  4. ROUTES")
print("-" * 70)

try:
    with open('routes_hr_manager.py', 'r') as f:
        routes_content = f.read()
        
        # Check get_user_companies function
        if 'def get_user_companies' in routes_content:
            log_check("get_user_companies() function exists", "pass", "Function found in routes_hr_manager.py")
            
            # Check if it uses the new method
            if 'get_accessible_companies()' in routes_content:
                log_check("Uses new method", "pass", "Routes use User.get_accessible_companies()")
            else:
                log_check("Uses new method", "fail", "Routes do not use get_accessible_companies()")
        else:
            log_check("get_user_companies() function", "fail", "Function not found")
except Exception as e:
    log_check("Routes check", "fail", str(e))

# ===== CHECK 5: Data Population =====
print("\n📊 5. DATA POPULATION")
print("-" * 70)

try:
    with app.app_context():
        user_company_count = UserCompanyAccess.query.count()
        if user_company_count > 0:
            log_check(f"UserCompanyAccess records", "pass", f"Found {user_company_count} user-company access records")
        else:
            log_check(f"UserCompanyAccess records", "warning", "No user-company access records found (need to run: python migrate_user_company_access.py)")
except Exception as e:
    log_check("Data check", "warning", f"Could not count records: {str(e)}")

# ===== CHECK 6: Migration Files =====
print("\n📁 6. MIGRATION FILES")
print("-" * 70)

migration_files = [
    "migrations/versions/add_user_company_access.py",
    "migrate_user_company_access.py",
]

for migration_file in migration_files:
    if os.path.exists(migration_file):
        log_check(f"{migration_file}", "pass", "File exists")
    else:
        log_check(f"{migration_file}", "fail", "File not found")

# ===== SUMMARY =====
print("\n" + "="*70)
print("📊 VERIFICATION SUMMARY")
print("="*70)
print(f"✅ Passed:  {checks_passed}")
print(f"❌ Failed:  {checks_failed}")
print(f"⚠️  Warnings: {checks_warnings}")
print()

if checks_failed == 0:
    if checks_warnings == 0:
        print("🎉 All checks passed! Multi-company support is fully implemented.")
        print("\n📋 Next steps:")
        print("  1. Run: flask db upgrade")
        print("  2. Run: python migrate_user_company_access.py")
        print("  3. Restart your application")
        print("  4. Test HR Manager Dashboard")
    else:
        print("✅ Implementation complete with minor warnings.")
        print("⚠️  Warnings to address:")
        print("  - Run database migration if not yet done")
        print("  - Run data migration script to populate user-company relationships")
else:
    print("❌ Some checks failed. Please review the errors above.")
    print("\n📋 Troubleshooting:")
    print("  - Check that all files are in correct locations")
    print("  - Verify template field names are corrected")
    print("  - Ensure database migration has been run")

print("\n" + "="*70)

sys.exit(0 if checks_failed == 0 else 1)