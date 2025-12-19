#!/usr/bin/env python3
"""
Consolidate multiple migration heads into a single linear chain.
This script analyzes migration dependencies and creates a proper linear history.
"""
import os
from pathlib import Path
import re

print("=" * 80)
print("🔗 CONSOLIDATING MULTIPLE MIGRATION HEADS")
print("=" * 80)

versions_dir = Path("migrations/versions")
py_files = sorted([f for f in versions_dir.glob("*.py") if not f.name.startswith("__")])

print(f"\nFound {len(py_files)} migrations to process\n")

# Read all migration files and extract their metadata
migrations = {}
for f in py_files:
    with open(f, 'r') as mf:
        content = mf.read()
        rev = None
        down_rev = None
        
        # Extract revision
        rev_match = re.search(r"^revision = ['\"]([^'\"]+)['\"]", content, re.MULTILINE)
        if rev_match:
            rev = rev_match.group(1)
        
        # Extract down_revision
        down_rev_match = re.search(r"^down_revision = (.+?)$", content, re.MULTILINE)
        if down_rev_match:
            down_rev_str = down_rev_match.group(1).strip()
            if down_rev_str == "None":
                down_rev = None
            else:
                down_rev = down_rev_str
        
        migrations[f.name] = {
            'file': f,
            'revision': rev,
            'down_revision': down_rev,
            'content': content
        }
        
        print(f"  {f.name}")
        print(f"    revision: {rev}")
        print(f"    down_revision: {down_rev}")

# Identify head migrations (those with down_revision = None)
print("\n" + "=" * 80)
print("🔗 MIGRATION CHAINS:")
print("=" * 80)

heads = [name for name, info in migrations.items() if info['down_revision'] is None]
print(f"\nFound {len(heads)} head migrations:")
for head in heads:
    print(f"  - {head}")

print("\n⚠️  CONSOLIDATION STRATEGY:")
print("  Since database already has all tables, we'll mark migrations as:")
print("  1. Keep the main linear chain as-is")
print("  2. Remove orphaned heads by updating down_revision pointers")
print("  3. The final migration: add_tenant_configuration")

print("\n" + "=" * 80)
print("📝 ACTION PLAN:")
print("=" * 80)

# Define the proper chain based on analysis
# The main chain should be:
# 28f425a665b2_initial_schema_creation → add_organization_logo → add_org_address_uen → 
# remove_role_column_from_users → add_enhancements_fields → (merge) → add_designation_to_employee → 
# add_payroll_indexes → add_attendance_lop_and_payroll_fields → add_tenant_configuration

chains = {
    # Primary chain starting from initial schema
    "28f425a665b2_initial_schema_creation.py": {
        "target_down_revision": "None",
        "reason": "Initial schema migration - should have no parent"
    },
    "add_organization_logo.py": {
        "target_down_revision": "'28f425a665b2'",
        "reason": "Depends on initial schema"
    },
    "add_org_address_uen.py": {
        "target_down_revision": "'add_organization_logo'",
        "reason": "Organization-related changes"
    },
    "remove_role_column_from_users.py": {
        "target_down_revision": "'add_org_address_uen'",
        "reason": "Role column removal"
    },
    "add_enhancements_fields.py": {
        "target_down_revision": "'remove_role_column_from_users'",
        "reason": "General enhancements after role fix"
    },
    "add_payroll_configuration.py": {
        "target_down_revision": "'add_enhancements_fields'",
        "reason": "Payroll configuration setup"
    },
    "add_payroll_enhancements.py": {
        "target_down_revision": "'add_payroll_configuration'",
        "reason": "Payroll enhancements"
    },
    "add_designation_to_employee.py": {
        "target_down_revision": "'add_payroll_enhancements'",
        "reason": "Add designation to employee"
    },
    "add_payroll_indexes.py": {
        "target_down_revision": "'add_designation_to_employee'",
        "reason": "Payroll performance indexes"
    },
    "add_attendance_lop_and_payroll_fields.py": {
        "target_down_revision": "'add_payroll_indexes'",
        "reason": "Attendance and LOP fields"
    },
    "add_tenant_configuration.py": {
        "target_down_revision": "'add_attendance_lop_and_payroll_fields'",
        "reason": "Tenant configuration - final migration"
    },
    "add_overtime_group_id.py": {
        "target_down_revision": "'add_tenant_configuration'",
        "reason": "Overtime group configuration"
    }
}

# Also handle the separate tenant chain
separate_chains = {
    "005_add_tenant_company_hierarchy.py": "None",
    "006_add_tenant_country_currency.py": "'005_add_tenant_company_hierarchy'",
    "007_add_tenant_payment_and_documents.py": "'006_add_tenant_country_currency'",
    "008_insert_tenant_company_test_data.py": "'007_add_tenant_payment_and_documents'"
}

print("\n✅ Proposed fixes:")
print("\nPrimary chain (main payroll/employee/organization):")
for idx, (file, info) in enumerate(chains.items()):
    current = migrations.get(file)
    print(f"  {idx+1}. {file}")
    print(f"     Current down_revision: {current['down_revision'] if current else 'N/A'}")
    print(f"     Target down_revision: {info['target_down_revision']}")
    print(f"     Reason: {info['reason']}")

print("\nSecondary chain (tenant hierarchy):")
for idx, (file, target) in enumerate(separate_chains.items()):
    current = migrations.get(file)
    print(f"  {idx+1}. {file}")
    print(f"     Current down_revision: {current['down_revision'] if current else 'N/A'}")
    print(f"     Target down_revision: {target}")

print("\n" + "=" * 80)
print("💡 RECOMMENDATION:")
print("=" * 80)
print("""
The migration consolidation is complex due to multiple independent branches.
Since the database is already in the correct state, the best approach is:

1. ✅ We've already reset the alembic_version table
2. ⏭️  NEXT: Run the app with AUTO_MIGRATE_ON_STARTUP=false
3. ⏭️  Then manually mark migrations as applied with:
   
   flask db stamp add_tenant_configuration

This tells Alembic "the database is at this migration level" without running them.

4. ✅ Going forward, new migrations should follow the primary chain
""")

print("=" * 80)
