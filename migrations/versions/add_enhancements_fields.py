"""Add enhancements for Team, Documents, and other features

Revision ID: add_enhancements_001
Revises: 
Create Date: 2025-01-XX

This migration adds:
1. employee_documents table for document management
2. Work permit fields to Employee
3. Timezone field to Employee
4. Father's name field to Employee
5. Overtime tracking fields to Attendance
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_enhancements_001'
down_revision = 'remove_role_column'  # Previous migration
branch_labels = None
depends_on = None


def upgrade():
    # Create employee_documents table
    op.create_table(
        'hrm_employee_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False),  # Offer Letter, Appraisal Letter, Salary Slip
        sa.Column('file_path', sa.String(length=255), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=True),  # For salary slips
        sa.Column('year', sa.Integer(), nullable=True),   # For salary slips
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['hrm_employee.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['hrm_users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_hrm_employee_documents_employee_id', 'hrm_employee_documents', ['employee_id'])
    op.create_index('ix_hrm_employee_documents_document_type', 'hrm_employee_documents', ['document_type'])
    op.create_index('ix_hrm_employee_documents_year_month', 'hrm_employee_documents', ['year', 'month'])
    
    # Add new fields to hrm_employee table
    with op.batch_alter_table('hrm_employee', schema=None) as batch_op:
        # Father's name for team info cards
        batch_op.add_column(sa.Column('father_name', sa.String(length=100), nullable=True))
        
        # Work permit number and expiry (if nationality != admin country)
        batch_op.add_column(sa.Column('work_permit_number', sa.String(length=50), nullable=True))
        # Note: work_permit_expiry already exists in the model
        
        # Timezone for attendance tracking (store as string like 'Asia/Singapore', 'America/New_York')
        batch_op.add_column(sa.Column('timezone', sa.String(length=50), nullable=True, server_default='UTC'))
        
        # Location field for team display
        batch_op.add_column(sa.Column('location', sa.String(length=100), nullable=True))
    
    # Add overtime tracking to hrm_attendance table
    with op.batch_alter_table('hrm_attendance', schema=None) as batch_op:
        # Add overtime flag
        batch_op.add_column(sa.Column('has_overtime', sa.Boolean(), nullable=False, server_default='false'))
        
        # Add overtime approval fields
        batch_op.add_column(sa.Column('overtime_approved', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('overtime_approved_by', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('overtime_approved_at', sa.DateTime(), nullable=True))
        
        # Add foreign key for overtime approver
        batch_op.create_foreign_key(
            'fk_attendance_overtime_approver',
            'hrm_users',
            ['overtime_approved_by'],
            ['id'],
            ondelete='SET NULL'
        )
    
    # Add index for overtime queries
    op.create_index('ix_hrm_attendance_has_overtime', 'hrm_attendance', ['has_overtime'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_hrm_attendance_has_overtime', table_name='hrm_attendance')
    op.drop_index('ix_hrm_employee_documents_year_month', table_name='hrm_employee_documents')
    op.drop_index('ix_hrm_employee_documents_document_type', table_name='hrm_employee_documents')
    op.drop_index('ix_hrm_employee_documents_employee_id', table_name='hrm_employee_documents')
    
    # Drop attendance overtime fields
    with op.batch_alter_table('hrm_attendance', schema=None) as batch_op:
        batch_op.drop_constraint('fk_attendance_overtime_approver', type_='foreignkey')
        batch_op.drop_column('overtime_approved_at')
        batch_op.drop_column('overtime_approved_by')
        batch_op.drop_column('overtime_approved')
        batch_op.drop_column('has_overtime')
    
    # Drop employee new fields
    with op.batch_alter_table('hrm_employee', schema=None) as batch_op:
        batch_op.drop_column('location')
        batch_op.drop_column('timezone')
        batch_op.drop_column('work_permit_number')
        batch_op.drop_column('father_name')
    
    # Drop employee_documents table
    op.drop_table('hrm_employee_documents')