"""Add performance indexes to payroll tables

Revision ID: add_payroll_indexes
Revises: 2be68655c2bb
Create Date: 2024-01-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_payroll_indexes'
down_revision = 'add_designation_to_employee'
branch_labels = None
depends_on = None


def upgrade():
    """Add performance indexes to payroll tables"""
    # Add individual indexes for common queries
    op.create_index('idx_hrm_payroll_employee_id', 'hrm_payroll', ['employee_id'], if_not_exists=True)
    op.create_index('idx_hrm_payroll_status', 'hrm_payroll', ['status'], if_not_exists=True)
    op.create_index('idx_hrm_payroll_generated_at', 'hrm_payroll', ['generated_at'], if_not_exists=True)
    
    # Add composite index for date range queries
    op.create_index('idx_hrm_payroll_period', 'hrm_payroll', 
                   ['pay_period_start', 'pay_period_end'], if_not_exists=True)
    
    # Add composite index for common queries (employee + period)
    op.create_index('idx_hrm_payroll_employee_period', 'hrm_payroll',
                   ['employee_id', 'pay_period_end'], if_not_exists=True)
    
    # Add partial index for draft payrolls (most common lookup)
    op.create_index('idx_hrm_payroll_draft', 'hrm_payroll',
                   ['status'], 
                   postgresql_where=sa.text("status = 'Draft'"),
                   if_not_exists=True)


def downgrade():
    """Remove added indexes"""
    op.drop_index('idx_hrm_payroll_draft', table_name='hrm_payroll', if_exists=True)
    op.drop_index('idx_hrm_payroll_employee_period', table_name='hrm_payroll', if_exists=True)
    op.drop_index('idx_hrm_payroll_period', table_name='hrm_payroll', if_exists=True)
    op.drop_index('idx_hrm_payroll_generated_at', table_name='hrm_payroll', if_exists=True)
    op.drop_index('idx_hrm_payroll_status', table_name='hrm_payroll', if_exists=True)
    op.drop_index('idx_hrm_payroll_employee_id', table_name='hrm_payroll', if_exists=True)