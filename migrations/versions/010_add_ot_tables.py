"""Add Overtime management tables

Revision ID: 010_add_ot_tables
Revises: add_leave_type_configuration
Create Date: 2025-01-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '010_add_ot_tables'
down_revision = 'add_leave_type_configuration'
branch_labels = None
depends_on = None


def upgrade():
    # Create OTType table
    op.create_table('hrm_ot_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('code', sa.String(length=20), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('rate_multiplier', sa.Numeric(precision=5, scale=2), nullable=True, server_default='1.5'),
    sa.Column('color_code', sa.String(length=20), nullable=True, server_default='#3498db'),
    sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
    sa.Column('applicable_days', sa.String(length=100), nullable=True),
    sa.Column('display_order', sa.Integer(), nullable=True, server_default='0'),
    sa.Column('created_by', sa.String(length=100), nullable=False, server_default='system'),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    sa.Column('modified_by', sa.String(length=100), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['hrm_company.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('company_id', 'code', name='uq_ot_type_company_code')
    )
    with op.batch_alter_table('hrm_ot_type', schema=None) as batch_op:
        batch_op.create_index('idx_ot_type_company_id', ['company_id'], unique=False)

    # Create OTAttendance table
    op.create_table('hrm_ot_attendance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('ot_date', sa.Date(), nullable=False),
    sa.Column('ot_in_time', sa.DateTime(), nullable=True),
    sa.Column('ot_out_time', sa.DateTime(), nullable=True),
    sa.Column('ot_hours', sa.Numeric(precision=6, scale=2), nullable=True),
    sa.Column('ot_type_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True, server_default='Draft'),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=True),
    sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=True),
    sa.Column('created_by', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['hrm_company.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['employee_id'], ['hrm_employee.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['ot_type_id'], ['hrm_ot_type.id']),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('employee_id', 'ot_date', name='uq_ot_attendance_emp_date')
    )
    with op.batch_alter_table('hrm_ot_attendance', schema=None) as batch_op:
        batch_op.create_index('idx_ot_attendance_employee_date', ['employee_id', 'ot_date'], unique=False)

    # Create OTRequest table
    op.create_table('hrm_ot_request',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('ot_date', sa.Date(), nullable=False),
    sa.Column('ot_type_id', sa.Integer(), nullable=False),
    sa.Column('requested_hours', sa.Numeric(precision=6, scale=2), nullable=False),
    sa.Column('reason', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True, server_default='Pending'),
    sa.Column('approved_hours', sa.Numeric(precision=6, scale=2), nullable=True),
    sa.Column('approver_id', sa.Integer(), nullable=True),
    sa.Column('approval_comments', sa.Text(), nullable=True),
    sa.Column('approved_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['approver_id'], ['hrm_users.id']),
    sa.ForeignKeyConstraint(['company_id'], ['hrm_company.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['employee_id'], ['hrm_employee.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['ot_type_id'], ['hrm_ot_type.id']),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('hrm_ot_request', schema=None) as batch_op:
        batch_op.create_index('idx_ot_request_employee_id', ['employee_id'], unique=False)
        batch_op.create_index('idx_ot_request_status', ['status'], unique=False)

    # Create OTApproval table
    op.create_table('hrm_ot_approval',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ot_request_id', sa.Integer(), nullable=False),
    sa.Column('approver_id', sa.Integer(), nullable=False),
    sa.Column('approval_level', sa.Integer(), nullable=True, server_default='1'),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('comments', sa.Text(), nullable=True),
    sa.Column('approved_hours', sa.Numeric(precision=6, scale=2), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    sa.ForeignKeyConstraint(['approver_id'], ['hrm_users.id']),
    sa.ForeignKeyConstraint(['ot_request_id'], ['hrm_ot_request.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

    # Create PayrollOTSummary table
    op.create_table('hrm_payroll_ot_summary',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('payroll_month', sa.Integer(), nullable=False),
    sa.Column('payroll_year', sa.Integer(), nullable=False),
    sa.Column('total_ot_hours', sa.Numeric(precision=8, scale=2), nullable=True, server_default='0'),
    sa.Column('total_ot_amount', sa.Numeric(precision=12, scale=2), nullable=True, server_default='0'),
    sa.Column('general_ot_hours', sa.Numeric(precision=8, scale=2), nullable=True, server_default='0'),
    sa.Column('general_ot_amount', sa.Numeric(precision=12, scale=2), nullable=True, server_default='0'),
    sa.Column('weekend_ot_hours', sa.Numeric(precision=8, scale=2), nullable=True, server_default='0'),
    sa.Column('weekend_ot_amount', sa.Numeric(precision=12, scale=2), nullable=True, server_default='0'),
    sa.Column('holiday_ot_hours', sa.Numeric(precision=8, scale=2), nullable=True, server_default='0'),
    sa.Column('holiday_ot_amount', sa.Numeric(precision=12, scale=2), nullable=True, server_default='0'),
    sa.Column('sunday_ot_hours', sa.Numeric(precision=8, scale=2), nullable=True, server_default='0'),
    sa.Column('sunday_ot_amount', sa.Numeric(precision=12, scale=2), nullable=True, server_default='0'),
    sa.Column('status', sa.String(length=20), nullable=True, server_default='Draft'),
    sa.Column('daily_logs', sa.JSON(), nullable=True),
    sa.Column('created_by', sa.String(length=100), nullable=False, server_default='system'),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    sa.Column('modified_by', sa.String(length=100), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('finalized_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['hrm_company.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['employee_id'], ['hrm_employee.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('employee_id', 'payroll_month', 'payroll_year', name='uq_payroll_ot_emp_month_year')
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_table('hrm_payroll_ot_summary')
    op.drop_table('hrm_ot_approval')
    op.drop_table('hrm_ot_request')
    op.drop_table('hrm_ot_attendance')
    op.drop_table('hrm_ot_type')