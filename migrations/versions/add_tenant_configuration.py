"""Add TenantConfiguration model for advanced tenant settings

Revision ID: add_tenant_configuration
Revises: add_attendance_lop_payroll_fields
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = 'add_tenant_configuration'
down_revision = 'add_attendance_lop_payroll_fields'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    # Check if the table already exists
    if 'hrm_tenant_configuration' not in inspector.get_table_names():
        op.create_table(
            'hrm_tenant_configuration',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('payslip_logo_path', sa.String(255), nullable=True),
            sa.Column('payslip_logo_filename', sa.String(255), nullable=True),
            sa.Column('payslip_logo_uploaded_by', sa.String(100), nullable=True),
            sa.Column('payslip_logo_uploaded_at', sa.DateTime(), nullable=True),
            sa.Column('employee_id_prefix', sa.String(50), server_default='EMP', nullable=False),
            sa.Column('employee_id_company_code', sa.String(20), nullable=True),
            sa.Column('employee_id_format', sa.String(100), server_default='prefix-company-number', nullable=False),
            sa.Column('employee_id_separator', sa.String(5), server_default='-', nullable=False),
            sa.Column('employee_id_next_number', sa.Integer(), server_default='1', nullable=False),
            sa.Column('employee_id_pad_length', sa.Integer(), server_default='4', nullable=False),
            sa.Column('employee_id_suffix', sa.String(50), nullable=True),
            sa.Column('overtime_enabled', sa.Boolean(), server_default=sa.true(), nullable=False),
            sa.Column('overtime_calculation_method', sa.String(20), server_default='By User', nullable=False),
            sa.Column('overtime_group_type', sa.String(50), nullable=True),
            sa.Column('general_overtime_rate', sa.Numeric(5, 2), server_default='1.5', nullable=False),
            sa.Column('holiday_overtime_rate', sa.Numeric(5, 2), server_default='2.0', nullable=False),
            sa.Column('weekend_overtime_rate', sa.Numeric(5, 2), server_default='1.5', nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.Column('updated_by', sa.String(100), nullable=True),
            sa.ForeignKeyConstraint(['tenant_id'], ['hrm_tenant.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('tenant_id', name='uq_tenant_config_tenant'),
        )
        
        # Create index
        op.create_index('idx_tenant_config_tenant_id', 'hrm_tenant_configuration', ['tenant_id'])


def downgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    # Drop the table if it exists
    if 'hrm_tenant_configuration' in inspector.get_table_names():
        op.drop_table('hrm_tenant_configuration')