"""Add Employee Group and Leave Allocation Models

Revision ID: leave_allocation_001
Revises: add_company_employee_id_config
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'leave_allocation_001'
down_revision = 'add_company_employee_id_config'
branch_labels = None
depends_on = None


def upgrade():
    # Add employee_group_id column to hrm_employee table
    op.add_column('hrm_employee',
        sa.Column('employee_group_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_employee_employee_group',
        'hrm_employee', 'hrm_employee_group',
        ['employee_group_id'], ['id'],
        ondelete='SET NULL'
    )

    # Create hrm_employee_group table
    op.create_table(
        'hrm_employee_group',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', sa.String(100), nullable=False, server_default='system'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('modified_by', sa.String(100), nullable=True),
        sa.Column('modified_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['hrm_company.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'name', name='uq_employee_group_company_name'),
        sa.Index('idx_hrm_employee_group_company_id', 'company_id'),
        sa.Index('idx_hrm_employee_group_is_active', 'is_active'),
    )

    # Create hrm_designation_leave_allocation table
    op.create_table(
        'hrm_designation_leave_allocation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('designation_id', sa.Integer(), nullable=False),
        sa.Column('leave_type_id', sa.Integer(), nullable=False),
        sa.Column('total_days', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=False, server_default='system'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('modified_by', sa.String(100), nullable=True),
        sa.Column('modified_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['hrm_company.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['designation_id'], ['hrm_designation.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['leave_type_id'], ['hrm_leave_type.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'designation_id', 'leave_type_id', 
                          name='uq_designation_leave_type'),
        sa.Index('idx_designation_leave_alloc_company', 'company_id'),
        sa.Index('idx_designation_leave_alloc_designation', 'designation_id'),
        sa.Index('idx_designation_leave_alloc_leave_type', 'leave_type_id'),
    )

    # Create hrm_employee_group_leave_allocation table
    op.create_table(
        'hrm_employee_group_leave_allocation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_group_id', sa.Integer(), nullable=False),
        sa.Column('leave_type_id', sa.Integer(), nullable=False),
        sa.Column('total_days', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=False, server_default='system'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('modified_by', sa.String(100), nullable=True),
        sa.Column('modified_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['hrm_company.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_group_id'], ['hrm_employee_group.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['leave_type_id'], ['hrm_leave_type.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'employee_group_id', 'leave_type_id', 
                          name='uq_employee_group_leave_type'),
        sa.Index('idx_emp_group_leave_alloc_company', 'company_id'),
        sa.Index('idx_emp_group_leave_alloc_group', 'employee_group_id'),
        sa.Index('idx_emp_group_leave_alloc_leave_type', 'leave_type_id'),
    )

    # Create hrm_employee_leave_allocation table
    op.create_table(
        'hrm_employee_leave_allocation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('leave_type_id', sa.Integer(), nullable=False),
        sa.Column('total_days', sa.Integer(), nullable=False),
        sa.Column('override_reason', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(100), nullable=False, server_default='system'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('modified_by', sa.String(100), nullable=True),
        sa.Column('modified_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['hrm_employee.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['leave_type_id'], ['hrm_leave_type.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'leave_type_id', 
                          name='uq_employee_leave_type'),
        sa.Index('idx_emp_leave_alloc_employee', 'employee_id'),
        sa.Index('idx_emp_leave_alloc_leave_type', 'leave_type_id'),
    )


def downgrade():
    # Drop tables in reverse order of creation
    op.drop_table('hrm_employee_leave_allocation')
    op.drop_table('hrm_employee_group_leave_allocation')
    op.drop_table('hrm_designation_leave_allocation')
    
    # Drop foreign key and column from hrm_employee
    op.drop_constraint('fk_employee_employee_group', 'hrm_employee', type_='foreignkey')
    op.drop_column('hrm_employee', 'employee_group_id')
    
    # Drop hrm_employee_group table
    op.drop_table('hrm_employee_group')