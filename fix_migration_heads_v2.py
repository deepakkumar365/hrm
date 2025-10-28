#!/usr/bin/env python3
"""Fix multiple migration heads v2 - using correct revision IDs"""
import re
from pathlib import Path

print("=" * 80)
print("🔗 FIXING MIGRATION HEADS - VERSION 2")
print("=" * 80)

versions_dir = Path("migrations/versions")

# Fixes using the CORRECT revision IDs that exist
fixes = {
    "add_enhancements_fields.py": {
        "revision": "add_enhancements_fields",
        "down_revision": "'remove_role_column'",  # Correct ID
        "reason": "Fixed down_revision to use correct revision ID"
    },
    "add_payroll_enhancements.py": {
        "revision": "add_payroll_enhancements",
        "down_revision": "'add_payroll_config'",  # Correct ID (not add_payroll_configuration)
        "reason": "Set parent to add_payroll_config (correct revision ID)"
    },
    "add_designation_to_employee.py": {
        "revision": "add_designation_to_employee",
        "down_revision": "'add_payroll_enhancements'",  # Was pointing to deleted merge migration
        "reason": "Updated parent from deleted merge migration to add_payroll_enhancements"
    },
    "add_payroll_indexes.py": {
        "revision": "add_payroll_indexes",
        "down_revision": "'add_designation_to_employee'",  # Was pointing to deleted merge migration
        "reason": "Updated parent from deleted merge migration to add_designation_to_employee"
    },
    "add_attendance_lop_and_payroll_fields.py": {
        "down_revision": "'add_payroll_indexes'",
        "reason": "Set parent to add_payroll_indexes"
    },
    "add_tenant_configuration.py": {
        "down_revision": "'add_attendance_lop_and_payroll_fields'",
        "reason": "Set parent to add_attendance_lop_and_payroll_fields"
    },
    "add_overtime_group_id.py": {
        "revision": "add_overtime_group_id",
        "down_revision": "'add_tenant_configuration'",
        "reason": "Set parent to add_tenant_configuration"
    },
    "005_add_tenant_company_hierarchy.py": {
        "down_revision": "'add_overtime_group_id'",
        "reason": "Integrated into main chain after add_overtime_group_id"
    },
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
    
    # Fix down_revision
    if "down_revision" in fix_info:
        old_down_pattern = r"^down_revision = (.+?)$"
        new_down = f"down_revision = {fix_info['down_revision']}"
        if re.search(old_down_pattern, content, re.MULTILINE):
            content = re.sub(old_down_pattern, new_down, content, flags=re.MULTILINE)
            updated = True
    
    if updated:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ {filename}")
        print(f"   {fix_info['reason']}\n")
    else:
        print(f"⚠️  {filename} - No changes made\n")

print("=" * 80)
print("✅ MIGRATION CONSOLIDATION COMPLETE!")
print("=" * 80)
print("""
The migrations should now be in a proper linear chain.
Next: Run the application with: python main.py
""")