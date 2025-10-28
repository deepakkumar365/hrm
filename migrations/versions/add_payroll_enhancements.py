"""Add payroll configuration enhancements and employee bank info

Revision ID: add_payroll_enhancements
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_payroll_enhancements'
down_revision = 'add_payroll_config'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to hrm_payroll_configuration
    op.add_column('hrm_payroll_configuration', sa.Column('employer_cpf', sa.Numeric(10, 2), nullable=True, server_default='0'))
    op.add_column('hrm_payroll_configuration', sa.Column('employee_cpf', sa.Numeric(10, 2), nullable=True, server_default='0'))
    op.add_column('hrm_payroll_configuration', sa.Column('net_salary', sa.Numeric(10, 2), nullable=True, server_default='0'))
    op.add_column('hrm_payroll_configuration', sa.Column('remarks', sa.Text, nullable=True))
    
    # Create employee_bank_info table
    op.create_table(
        'hrm_employee_bank_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('bank_account_name', sa.String(length=100), nullable=True),
        sa.Column('bank_account_number', sa.String(length=30), nullable=True),
        sa.Column('bank_code', sa.String(length=20), nullable=True),
        sa.Column('paynow_no', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['hrm_employee.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', name='uq_employee_bank_info_employee_id')
    )
    op.create_index('ix_hrm_employee_bank_info_employee_id', 'hrm_employee_bank_info', ['employee_id'])


def downgrade():
    # Drop employee_bank_info table
    op.drop_index('ix_hrm_employee_bank_info_employee_id', table_name='hrm_employee_bank_info')
    op.drop_table('hrm_employee_bank_info')
    
    # Remove columns from hrm_payroll_configuration
    op.drop_column('hrm_payroll_configuration', 'remarks')
    op.drop_column('hrm_payroll_configuration', 'net_salary')
    op.drop_column('hrm_payroll_configuration', 'employee_cpf')
    op.drop_column('hrm_payroll_configuration', 'employer_cpf')