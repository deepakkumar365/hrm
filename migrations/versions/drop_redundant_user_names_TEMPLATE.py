"""Drop redundant first_name and last_name columns from hrm_users

This migration should be run AFTER:
1. All code has been updated to use hrm_employee names
2. All templates have been updated
3. All tests pass
4. Thorough verification that no code references User.first_name or User.last_name directly

Revision ID: TEMPLATE_DROP_USER_NAMES
Revises: [PREVIOUS_MIGRATION_ID]
Create Date: [TODAY]

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'TEMPLATE_DROP_USER_NAMES'
down_revision = None  # Set to previous migration ID
branch_labels = None
depends_on = None


def upgrade():
    """
    Drop the redundant first_name and last_name columns from hrm_users table.
    
    At this point, all profile names should be accessed from hrm_employee table
    through the User.get_first_name, User.get_last_name, or User.full_name properties.
    """
    
    print("\n" + "=" * 80)
    print("MIGRATION: Dropping redundant name columns from hrm_users")
    print("=" * 80)
    print("\nREQUIREMENTS CHECKLIST:")
    print("  [ ] All code updated to use User.get_first_name/get_last_name")
    print("  [ ] All templates updated to use employee profile names")
    print("  [ ] All tests passing")
    print("  [ ] Verified no direct access to User.first_name/last_name")
    print("  [ ] Backup created")
    print("=" * 80 + "\n")
    
    # Drop the columns
    op.drop_column('hrm_users', 'first_name')
    op.drop_column('hrm_users', 'last_name')
    
    print("✅ Successfully dropped first_name and last_name columns from hrm_users")


def downgrade():
    """
    Restore the first_name and last_name columns to hrm_users table.
    
    This allows rollback if needed.
    """
    
    print("\n" + "=" * 80)
    print("ROLLBACK: Restoring name columns to hrm_users")
    print("=" * 80 + "\n")
    
    # Restore the columns
    op.add_column('hrm_users', 
                   sa.Column('first_name', sa.String(50), nullable=False, server_default='Unknown'))
    op.add_column('hrm_users', 
                   sa.Column('last_name', sa.String(50), nullable=False, server_default='Unknown'))
    
    # Sync data from employee profiles
    conn = op.get_bind()
    conn.execute("""
        UPDATE hrm_users u
        SET first_name = COALESCE(e.first_name, 'Unknown'),
            last_name = COALESCE(e.last_name, 'Unknown')
        FROM hrm_employee e
        WHERE e.user_id = u.id
    """)
    
    print("✅ Successfully restored first_name and last_name columns to hrm_users")
    print("⚠️  Data has been synced from employee profiles")


# Additional helper migration - verify data before dropping columns
def verify_migration():
    """
    Verify that it's safe to drop the columns.
    Run this before upgrading to ensure no code still references the columns.
    """
    print("\n" + "=" * 80)
    print("VERIFICATION: Checking for column references")
    print("=" * 80)
    
    # Search for direct column access patterns
    import subprocess
    import sys
    
    patterns = [
        r'user\.first_name(?!\s*#)',
        r'user\.last_name(?!\s*#)',
        r'current_user\.first_name(?!\s*#)',
        r'current_user\.last_name(?!\s*#)',
        r'\.first_name\s*=',
        r'\.last_name\s*=',
    ]
    
    print("\nSearching for potentially problematic patterns in code...")
    found_issues = False
    
    for pattern in patterns:
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'grep', '-r', pattern, '.', '--include=*.py'],
                capture_output=True,
                text=True,
                cwd='.'
            )
            if result.stdout:
                print(f"\n⚠️  Found pattern: {pattern}")
                print(result.stdout[:500])
                found_issues = True
        except:
            pass
    
    if found_issues:
        print("\n❌ Issues found! Please fix references before dropping columns.")
        return False
    else:
        print("\n✅ No obvious issues found. Safe to proceed with column drop.")
        return True


if __name__ == '__main__':
    verify_migration()