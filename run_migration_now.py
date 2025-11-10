#!/usr/bin/env python
"""
Run the leave allocation migration
Execute: python run_migration_now.py
"""

import os
import sys
import subprocess

# Change to project directory
os.chdir('D:/Projects/HRMS/hrm')

print("=" * 60)
print("Running Leave Allocation Migration")
print("=" * 60)

try:
    # Run the migration
    result = subprocess.run(
        [sys.executable, '-m', 'flask', 'db', 'upgrade'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("\n✅ Migration completed successfully!")
        print("\nThe following changes were applied:")
        print("  ✓ Added 'employee_group_id' column to hrm_employee table")
        print("  ✓ Created hrm_employee_group table")
        print("  ✓ Created hrm_designation_leave_allocation table")
        print("  ✓ Created hrm_employee_group_leave_allocation table")
        print("  ✓ Created hrm_employee_leave_allocation table")
    else:
        print(f"\n❌ Migration failed with return code: {result.returncode}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)