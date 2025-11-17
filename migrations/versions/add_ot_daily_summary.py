"""Add OTDailySummary table for OT Payroll Summary management

Revision ID: add_ot_daily_summary_001
Revises: add_overtime_group_001
Create Date: 2025-01-01

This migration adds:
1. hrm_ot_daily_summary table for storing daily OT records with allowances
   - Tracks OT hours, rates, and amounts per employee per day
   - Stores manually editable allowance columns (KD & CLAIM, TRIPS, etc.)
   - Used by HR Manager for Payroll Summary grid
   - Integrates with Payroll module for OT amount consolidation
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_ot_daily_summary_001'
down_revision = 'add_overtime_group_001'
branch_labels = None
depends_on = None


def upgrade():
    """Create hrm_ot_daily_summary table"""
    op.create_table(
        'hrm_ot_daily_summary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ot_request_id', sa.Integer(), nullable=True),
        sa.Column('ot_date', sa.Date(), nullable=False),
        sa.Column('ot_hours', sa.Numeric(precision=6, scale=2), server_default='0', nullable=False),
        sa.Column('ot_rate_per_hour', sa.Numeric(precision=8, scale=2), server_default='0', nullable=False),
        sa.Column('ot_amount', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('kd_and_claim', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('trips', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('sinpost', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('sandstone', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('spx', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('psle', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('manpower', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('stacking', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('dispose', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('night', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('ph', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('sun', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('total_allowances', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('status', sa.String(length=20), server_default='Draft', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('modified_by', sa.String(length=100), nullable=True),
        sa.Column('modified_at', sa.DateTime(), nullable=True),
        sa.Column('finalized_at', sa.DateTime(), nullable=True),
        sa.Column('finalized_by', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['hrm_company.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['hrm_employee.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ot_request_id'], ['hrm_ot_request.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'ot_date', name='uq_ot_daily_emp_date')
    )
    
    # Create indexes
    op.create_index('idx_ot_daily_employee_date', 'hrm_ot_daily_summary', ['employee_id', 'ot_date'])
    op.create_index('idx_ot_daily_status', 'hrm_ot_daily_summary', ['status'])
    op.create_index('idx_ot_daily_company', 'hrm_ot_daily_summary', ['company_id'])


def downgrade():
    """Drop hrm_ot_daily_summary table"""
    # Drop indexes
    op.drop_index('idx_ot_daily_company', table_name='hrm_ot_daily_summary')
    op.drop_index('idx_ot_daily_status', table_name='hrm_ot_daily_summary')
    op.drop_index('idx_ot_daily_employee_date', table_name='hrm_ot_daily_summary')
    
    # Drop table
    op.drop_table('hrm_ot_daily_summary')