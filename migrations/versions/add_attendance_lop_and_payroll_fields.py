"""Add LOP column to Attendance and Levy Allowance to PayrollConfiguration

Revision ID: add_attendance_lop_payroll_fields
Revises: add_payroll_enhancements
Create Date: 2024-01-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = 'add_attendance_lop_payroll_fields'
down_revision = 'add_payroll_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # Get connection to check if columns exist
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    # Add LOP column to hrm_attendance if it doesn't exist
    attendance_columns = [col['name'] for col in inspector.get_columns('hrm_attendance')]
    if 'lop' not in attendance_columns:
        op.add_column('hrm_attendance', sa.Column('lop', sa.Boolean(), nullable=True, server_default='false'))
    
    # Add Levy Allowance fields to hrm_payroll_configuration if they don't exist
    payroll_config_columns = [col['name'] for col in inspector.get_columns('hrm_payroll_configuration')]
    if 'levy_allowance_name' not in payroll_config_columns:
        op.add_column('hrm_payroll_configuration', 
                      sa.Column('levy_allowance_name', sa.String(100), nullable=True))
    if 'levy_allowance_amount' not in payroll_config_columns:
        op.add_column('hrm_payroll_configuration', 
                      sa.Column('levy_allowance_amount', sa.Numeric(10, 2), nullable=True, server_default='0'))
    
    # Add new columns to hrm_payroll if they don't exist
    payroll_columns = [col['name'] for col in inspector.get_columns('hrm_payroll')]
    if 'absent_days' not in payroll_columns:
        op.add_column('hrm_payroll', sa.Column('absent_days', sa.Integer(), nullable=True, server_default='0'))
    if 'lop_days' not in payroll_columns:
        op.add_column('hrm_payroll', sa.Column('lop_days', sa.Integer(), nullable=True, server_default='0'))
    if 'lop_deduction' not in payroll_columns:
        op.add_column('hrm_payroll', sa.Column('lop_deduction', sa.Numeric(10, 2), nullable=True, server_default='0'))


def downgrade():
    # Remove columns from hrm_payroll
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    payroll_columns = [col['name'] for col in inspector.get_columns('hrm_payroll')]
    if 'lop_deduction' in payroll_columns:
        op.drop_column('hrm_payroll', 'lop_deduction')
    if 'lop_days' in payroll_columns:
        op.drop_column('hrm_payroll', 'lop_days')
    if 'absent_days' in payroll_columns:
        op.drop_column('hrm_payroll', 'absent_days')
    
    # Remove Levy Allowance fields from hrm_payroll_configuration
    payroll_config_columns = [col['name'] for col in inspector.get_columns('hrm_payroll_configuration')]
    if 'levy_allowance_amount' in payroll_config_columns:
        op.drop_column('hrm_payroll_configuration', 'levy_allowance_amount')
    if 'levy_allowance_name' in payroll_config_columns:
        op.drop_column('hrm_payroll_configuration', 'levy_allowance_name')
    
    # Remove LOP column from hrm_attendance
    attendance_columns = [col['name'] for col in inspector.get_columns('hrm_attendance')]
    if 'lop' in attendance_columns:
        op.drop_column('hrm_attendance', 'lop')