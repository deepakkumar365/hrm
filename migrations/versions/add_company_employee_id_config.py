"""Add company employee ID configuration table with automatic initialization

This migration:
1. Creates the hrm_company_employee_id_config table
2. Automatically initializes configs for all existing companies
3. Preserves existing employee ID sequences

Revision ID: add_company_employee_id_config
Revises: add_certification_pass_renewal
Create Date: 2025-01-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_company_employee_id_config'
down_revision = 'add_certification_pass_renewal'
branch_labels = None
depends_on = None


def upgrade():
    """Create table and initialize data"""
    
    # Step 1: Create the company_employee_id_config table
    op.create_table('hrm_company_employee_id_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('last_sequence_number', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('id_prefix', sa.String(length=10), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('modified_by', sa.String(length=100), nullable=True),
        sa.Column('modified_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['hrm_company.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', name='uq_company_employee_id_config_company_id')
    )
    
    # Create index for faster lookups
    op.create_index(
        'idx_company_employee_id_config_company_id',
        'hrm_company_employee_id_config',
        ['company_id'],
        unique=False
    )
    
    # Step 2: Initialize configurations for all existing companies
    connection = op.get_bind()
    
    # Get all companies with their employees
    companies_query = """
        SELECT DISTINCT c.id, c.code 
        FROM hrm_company c
        ORDER BY c.id
    """
    
    companies = connection.execute(sa.text(companies_query)).fetchall()
    
    for company_id, company_code in companies:
        # Check if config already exists (safety check)
        existing_check = """
            SELECT id FROM hrm_company_employee_id_config 
            WHERE company_id = :company_id
        """
        existing = connection.execute(sa.text(existing_check), {'company_id': company_id}).fetchone()
        
        if existing:
            print(f"⏭️  Skipping {company_code}: Config already exists")
            continue
        
        # Find the maximum employee sequence number for this company
        max_seq_query = """
            SELECT COALESCE(MAX(CAST(SUBSTRING(employee_id, LENGTH(:prefix) + 1) AS INTEGER)), 0) as max_seq
            FROM hrm_employee
            WHERE company_id = :company_id 
            AND employee_id LIKE :prefix_pattern
            AND employee_id ~ '^[A-Z0-9]+[0-9]{3}$'
        """
        
        result = connection.execute(
            sa.text(max_seq_query),
            {
                'company_id': company_id,
                'prefix': company_code,
                'prefix_pattern': f"{company_code}%"
            }
        ).fetchone()
        
        max_sequence = result[0] if result and result[0] else 0
        
        # Insert the configuration
        insert_query = """
            INSERT INTO hrm_company_employee_id_config 
            (company_id, last_sequence_number, id_prefix, created_by, created_at, modified_at)
            VALUES (:company_id, :last_seq, :prefix, 'system', NOW(), NOW())
        """
        
        connection.execute(
            sa.text(insert_query),
            {
                'company_id': company_id,
                'last_seq': max_sequence,
                'prefix': company_code
            }
        )
        
        print(f"✅ Initialized {company_code} with last_sequence={max_sequence}")
    
    connection.commit()
    print("✨ Company Employee ID Configuration initialized successfully!")


def downgrade():
    """Remove the table"""
    op.drop_index('idx_company_employee_id_config_company_id', table_name='hrm_company_employee_id_config')
    op.drop_table('hrm_company_employee_id_config')