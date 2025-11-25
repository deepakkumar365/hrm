"""Merge multiple migration heads into a single linear path

This migration merges the following heads:
1. add_company_timezone (timezone feature)
2. leave_allocation_001 (leave allocation feature)
3. add_payroll_config (payroll configuration)
4. add_enhancements_fields (HR enhancements)
5. 010_add_ot_tables (overtime tables)

Revision ID: merge_migration_heads
Revises: None (merge multiple heads)
Create Date: 2025-01-24 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_migration_heads'
down_revision = None  # This is a merge point
branch_labels = None
depends_on = [
    'add_company_timezone',
    'leave_allocation_001', 
    'add_payroll_config',
    'add_enhancements_fields',
    '010_add_ot_tables'
]


def upgrade():
    """Merge multiple migration heads"""
    print("✅ Merging multiple migration heads into single linear path")
    print("   - add_company_timezone")
    print("   - leave_allocation_001")
    print("   - add_payroll_config")
    print("   - add_enhancements_fields")
    print("   - 010_add_ot_tables")
    pass


def downgrade():
    """Cannot downgrade a merge migration"""
    print("⚠️  Cannot downgrade a merge migration")
    pass