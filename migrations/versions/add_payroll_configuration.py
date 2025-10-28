"""Add payroll configuration table

Revision ID: add_payroll_config
Revises: add_enhancements_fields
Create Date: 2025-01-22 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_payroll_config'
down_revision = 'add_enhancements_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Create payroll_configuration table
    op.create_table('hrm_payroll_configuration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('allowance_1_name', sa.String(length=100), nullable=True),
        sa.Column('allowance_1_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('allowance_2_name', sa.String(length=100), nullable=True),
        sa.Column('allowance_2_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('allowance_3_name', sa.String(length=100), nullable=True),
        sa.Column('allowance_3_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('allowance_4_name', sa.String(length=100), nullable=True),
        sa.Column('allowance_4_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('ot_rate_per_hour', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['hrm_employee.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['hrm_users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id')
    )
    op.create_index('ix_hrm_payroll_config_employee_id', 'hrm_payroll_configuration', ['employee_id'], unique=False)


def downgrade():
    op.drop_index('ix_hrm_payroll_config_employee_id', table_name='hrm_payroll_configuration')
    op.drop_table('hrm_payroll_configuration')