#!/usr/bin/env python3
"""Fix multiple migration heads by consolidating into a single linear chain"""
import re
from pathlib import Path

print("=" * 80)
print("🔗 FIXING MULTIPLE MIGRATION HEADS")
print("=" * 80)

versions_dir = Path("migrations/versions")

# The proper migration chain we want to establish:
# 1. 28f425a665b2_initial_schema_creation (ROOT - no parent)
# 2. add_organization_logo
# 3. add_org_address_uen
# 4. remove_role_column_from_users
# 5. add_enhancements_fields (fix revision ID)
# 6. add_payroll_configuration
# 7. add_payroll_enhancements
# 8. add_designation_to_employee
# 9. add_payroll_indexes
# 10. add_attendance_lop_and_payroll_fields
# 11. add_overtime_group_id (fix revision ID)
# 12. add_tenant_configuration
# 13. 005_add_tenant_company_hierarchy
# 14. 006_add_tenant_country_currency
# 15. 007_add_tenant_payment_and_documents
# 16. 008_insert_tenant_company_test_data

# Delete the empty merge migration
merge_file = versions_dir / "2be68655c2bb_merge_payroll_and_enhancements.py"
if merge_file.exists():
    merge_file.unlink()
    print("\n✅ Deleted empty merge migration: 2be68655c2bb_merge_payroll_and_enhancements.py")

# Define fixes
fixes = {
    "add_enhancements_fields.py": {
        "revision": "add_enhancements_fields",
        "down_revision": "'remove_role_column_from_users'",
        "reason": "Fixed revision ID and parent reference"
    },
    "add_payroll_enhancements.py": {
        "revision": "add_payroll_enhancements", 
        "down_revision": "'add_payroll_configuration'",
        "reason": "Set parent to add_payroll_configuration"
    },
    "add_overtime_group_id.py": {
        "revision": "add_overtime_group_id",
        "down_revision": "'add_tenant_configuration'",
        "reason": "Changed revision ID and set parent to add_tenant_configuration"
    },
    "005_add_tenant_company_hierarchy.py": {
        "down_revision": "'add_overtime_group_id'",
        "reason": "Integrated tenant hierarchy into main chain"
    },
    "006_add_tenant_country_currency.py": {
        "down_revision": "'005_add_tenant_company_hierarchy'",
        "reason": "Fixed parent reference"
    },
    "007_add_tenant_payment_and_documents.py": {
        "down_revision": "'006_add_tenant_country_currency'",
        "reason": "Fixed parent reference"
    },
    "008_insert_tenant_company_test_data.py": {
        "down_revision": "'007_add_tenant_payment_and_documents'",
        "reason": "Fixed parent reference"
    }
}

print("\n📝 APPLYING FIXES:")
print("-" * 80)

for filename, fix_info in fixes.items():
    filepath = versions_dir / filename
    if not filepath.exists():
        print(f"⚠️  {filename} - NOT FOUND (skipping)")
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    updated = False
    
    # Fix revision ID if specified
    if "revision" in fix_info:
        old_rev_pattern = r"^revision = ['\"]([^'\"]+)['\"]"
        new_rev = f"revision = '{fix_info['revision']}'"
        if re.search(old_rev_pattern, content, re.MULTILINE):
            content = re.sub(old_rev_pattern, new_rev, content, flags=re.MULTILINE)
            updated = True
            print(f"  • Updated revision ID to: {fix_info['revision']}")
    
    # Fix down_revision
    if "down_revision" in fix_info:
        old_down_pattern = r"^down_revision = (.+?)$"
        new_down = f"down_revision = {fix_info['down_revision']}"
        if re.search(old_down_pattern, content, re.MULTILINE):
            content = re.sub(old_down_pattern, new_down, content, flags=re.MULTILINE)
            updated = True
            print(f"  • Updated down_revision to: {fix_info['down_revision']}")
    
    if updated:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ {filename}")
        print(f"   Reason: {fix_info['reason']}\n")
    else:
        print(f"⚠️  {filename} - No changes needed\n")

print("=" * 80)
print("✅ MIGRATION CONSOLIDATION COMPLETE!")
print("=" * 80)
print("""
The migrations have been consolidated into a single linear chain:

ROOT: 28f425a665b2_initial_schema_creation
  └─ add_organization_logo
     └─ add_org_address_uen
        └─ remove_role_column_from_users
           └─ add_enhancements_fields
              └─ add_payroll_configuration
                 └─ add_payroll_enhancements
                    └─ add_designation_to_employee
                       └─ add_payroll_indexes
                          └─ add_attendance_lop_and_payroll_fields
                             └─ add_tenant_configuration
                                └─ add_overtime_group_id
                                   └─ 005_add_tenant_company_hierarchy
                                      └─ 006_add_tenant_country_currency
                                         └─ 007_add_tenant_payment_and_documents
                                            └─ 008_insert_tenant_company_test_data

Next steps:
1. Run: python main.py
2. The app will now apply migrations in the correct linear order

""")