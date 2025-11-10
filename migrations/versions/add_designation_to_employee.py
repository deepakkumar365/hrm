"""Add designation_id column to hrm_employee table

Revision ID: add_designation_to_employee
Revises: add_is_manager
Create Date: 2024-01-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_designation_to_employee'
down_revision = 'add_is_manager'
branch_labels = None
depends_on = None


def upgrade():
    """Add designation_id column to hrm_employee table"""
    # Add designation_id column if it doesn't exist
    try:
        op.add_column('hrm_employee', sa.Column('designation_id', sa.Integer(), nullable=True))
        # Add foreign key constraint
        op.create_foreign_key(
            'fk_hrm_employee_designation_id',
            'hrm_employee', 'hrm_designation',
            ['designation_id'], ['id']
        )
        print("✓ Added designation_id column to hrm_employee")
    except Exception as e:
        print(f"Note: {str(e)}")


def downgrade():
    """Remove designation_id column from hrm_employee table"""
    try:
        # Drop foreign key first
        op.drop_constraint('fk_hrm_employee_designation_id', 'hrm_employee', type_='foreignkey')
        # Drop column
        op.drop_column('hrm_employee', 'designation_id')
        print("✓ Removed designation_id column from hrm_employee")
    except Exception as e:
        print(f"Note: {str(e)}")