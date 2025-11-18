#!/usr/bin/env python
"""
File-based verification script for Multi-Company Support.
Checks implementation without requiring app to be running.

Usage: python verify_multi_company_files.py
"""

import os

print("\n" + "="*70)
print("🔍 Multi-Company Support - File Verification")
print("="*70 + "\n")

checks_passed = 0
checks_failed = 0

def check_mark(status):
    return "✅" if status else "❌"

def log_check(name, status, details=""):
    global checks_passed, checks_failed
    mark = check_mark(status)
    print(f"{mark} {name}")
    if details:
        print(f"   {details}")
    if status:
        checks_passed += 1
    else:
        checks_failed += 1
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
            has_correct = correct_text in content
            has_wrong = wrong_text in content
            
            if has_correct and not has_wrong:
                log_check(f"{template_file}", True, f"✓ Uses {correct_text}")
            else:
                log_check(f"{template_file}", False, f"Still has {wrong_text}!")
    except FileNotFoundError:
        log_check(f"{template_file}", False, "File not found")
    except Exception as e:
        log_check(f"{template_file}", False, str(e))

# ===== CHECK 2: Model File =====
print("\n📦 2. MODEL FILE (models.py)")
print("-" * 70)

try:
    with open('models.py', 'r') as f:
        content = f.read()
        
        checks = [
            ('class UserCompanyAccess', "UserCompanyAccess model"),
            ('company_access = db.relationship', "User.company_access relationship"),
            ('def get_accessible_companies', "User.get_accessible_companies() method"),
            ('__tablename__ = \'hrm_user_company_access\'', "Junction table definition"),
        ]
        
        for check_text, check_name in checks:
            if check_text in content:
                log_check(f"{check_name}", True, f"Found in models.py")
            else:
                log_check(f"{check_name}", False, f"Not found in models.py")
                
except FileNotFoundError:
    log_check("models.py", False, "File not found")

# ===== CHECK 3: Routes File =====
print("\n🛣️  3. ROUTES FILE (routes_hr_manager.py)")
print("-" * 70)

try:
    with open('routes_hr_manager.py', 'r') as f:
        content = f.read()
        
        checks = [
            ('def get_user_companies', "get_user_companies function"),
            ('get_accessible_companies()', "Uses get_accessible_companies method"),
        ]
        
        for check_text, check_name in checks:
            if check_text in content:
                log_check(f"{check_name}", True, "Found in routes_hr_manager.py")
            else:
                log_check(f"{check_name}", False, "Not found in routes_hr_manager.py")
                
except FileNotFoundError:
    log_check("routes_hr_manager.py", False, "File not found")

# ===== CHECK 4: Migration Files =====
print("\n🗄️  4. MIGRATION FILES")
print("-" * 70)

migration_files = [
    ("migrations/versions/add_user_company_access.py", "Database migration"),
    ("migrate_user_company_access.py", "Data migration script"),
]

for migration_file, description in migration_files:
    if os.path.exists(migration_file):
        log_check(f"{description}", True, f"{migration_file}")
    else:
        log_check(f"{description}", False, f"{migration_file} not found")

# ===== CHECK 5: Migration File Content =====
print("\n📝 5. MIGRATION FILE CONTENT")
print("-" * 70)

try:
    with open('migrations/versions/add_user_company_access.py', 'r') as f:
        content = f.read()
        
        checks = [
            ('hrm_user_company_access', "Junction table name"),
            ('user_id', "user_id column"),
            ('company_id', "company_id column"),
            ('UniqueConstraint', "Unique constraint"),
        ]
        
        for check_text, check_name in checks:
            if check_text in content:
                log_check(f"{check_name}", True, "Found in migration")
            else:
                log_check(f"{check_name}", False, "Not found in migration")
                
except FileNotFoundError:
    log_check("Migration file", False, "Not found")

# ===== CHECK 6: Data Migration Script =====
print("\n📊 6. DATA MIGRATION SCRIPT")
print("-" * 70)

try:
    with open('migrate_user_company_access.py', 'r') as f:
        content = f.read()
        
        checks = [
            ('migrate_existing_user_companies', "Main migration function"),
            ('SuperAdmin', "Super Admin handling"),
            ('HR Manager', "HR Manager handling"),
            ('UserCompanyAccess', "UserCompanyAccess usage"),
        ]
        
        for check_text, check_name in checks:
            if check_text in content:
                log_check(f"{check_name}", True, "Found in data migration script")
            else:
                log_check(f"{check_name}", False, "Not found in data migration script")
                
except FileNotFoundError:
    log_check("Data migration script", False, "Not found")

# ===== CHECK 7: Documentation =====
print("\n📚 7. DOCUMENTATION")
print("-" * 70)

doc_files = [
    ("MULTI_COMPANY_DEPLOYMENT.md", "Deployment guide"),
    ("MULTI_COMPANY_SUMMARY.md", "Summary document"),
]

for doc_file, description in doc_files:
    if os.path.exists(doc_file):
        log_check(f"{description}", True, f"{doc_file}")
    else:
        log_check(f"{description}", False, f"{doc_file} not found")

# ===== SUMMARY =====
print("\n" + "="*70)
print("📊 VERIFICATION SUMMARY")
print("="*70)
print(f"✅ Passed:  {checks_passed}")
print(f"❌ Failed:  {checks_failed}")
print()

if checks_failed == 0:
    print("🎉 All file checks passed!")
    print("\n✅ Implementation is complete. All files are in place.")
    print("\n📋 Next steps:")
    print("  1. Review MULTI_COMPANY_SUMMARY.md for overview")
    print("  2. Review MULTI_COMPANY_DEPLOYMENT.md for detailed deployment steps")
    print("  3. Run: flask db upgrade")
    print("  4. Run: python migrate_user_company_access.py")
    print("  5. Restart your application")
    print("  6. Test HR Manager Dashboard company selector")
else:
    print(f"❌ {checks_failed} checks failed.")
    print("\n📋 Please review the failures above.")

print("\n" + "="*70 + "\n")
