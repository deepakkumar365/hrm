"""Add Leave Type Configuration table for company-specific leave management

Revision ID: add_leave_type_configuration
Revises: add_certification_pass_renewal
Create Date: 2024-12-20 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'add_leave_type_configuration'
down_revision = 'add_certification_pass_renewal'
branch_labels = None
depends_on = None


def upgrade():
    """Create hrm_leave_type table"""
    try:
        op.create_table(
            'hrm_leave_type',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('company_id', sa.String(36), nullable=False),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('code', sa.String(20), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('annual_allocation', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('color', sa.String(20), nullable=False, server_default='#3498db'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('created_by', sa.String(100), nullable=False, server_default='system'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('modified_by', sa.String(100), nullable=True),
            sa.Column('modified_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['company_id'], ['hrm_company.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('company_id', 'name', name='uq_leave_type_company_name')
        )
        
        # Create indexes
        op.create_index('idx_hrm_leave_type_company_id', 'hrm_leave_type', ['company_id'])
        op.create_index('idx_hrm_leave_type_is_active', 'hrm_leave_type', ['is_active'])
        
        print("✓ Created hrm_leave_type table")
    except Exception as e:
        print(f"Note: hrm_leave_type table - {str(e)}")


def downgrade():
    """Drop hrm_leave_type table"""
    try:
        op.drop_table('hrm_leave_type')
        print("✓ Dropped hrm_leave_type table")
    except Exception as e:
        print(f"Note: Drop hrm_leave_type - {str(e)}")