"""Add overtime_group_id field to Employee for group-based overtime configuration

Revision ID: add_overtime_group_001
Revises: 
Create Date: 2025-01-01

This migration adds:
1. overtime_group_id field to hrm_employee table for overtime group mapping
   - Stores group identifier (e.g., "Group 1", "Group 2", etc.)
   - Used for group-based overtime calculations
   - References tenant configuration overtime group settings
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_overtime_group_001'
down_revision = None  # Set to previous migration ID when integrating
branch_labels = None
depends_on = None


def upgrade():
    """Add overtime_group_id field to hrm_employee table"""
    with op.batch_alter_table('hrm_employee', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('overtime_group_id', sa.String(length=50), nullable=True)
        )
    
    # Create index for overtime group queries
    op.create_index('ix_hrm_employee_overtime_group_id', 'hrm_employee', ['overtime_group_id'])


def downgrade():
    """Remove overtime_group_id field from hrm_employee table"""
    # Drop index
    op.drop_index('ix_hrm_employee_overtime_group_id', table_name='hrm_employee')
    
    # Drop column
    with op.batch_alter_table('hrm_employee', schema=None) as batch_op:
        batch_op.drop_column('overtime_group_id')