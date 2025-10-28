"""Add tenant payment config and documents tables

Revision ID: 007
Revises: 006_add_tenant_country_currency
Create Date: 2024-01-03

This migration creates the missing tables for tenant payment configuration and 
document management. Completes tenant management schema.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_add_tenant_payment_and_documents'
down_revision = '006_add_tenant_country_currency'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade migration - Add tenant payment and documents tables"""
    
    # 1. CREATE hrm_tenant_payment_config TABLE
    op.create_table(
        'hrm_tenant_payment_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Payment Type: 'Fixed' or 'User-Based'
        sa.Column('payment_type', sa.String(20), nullable=False, server_default=sa.text("'Fixed'")),
        
        # Fixed Payment Fields
        sa.Column('implementation_charges', sa.Numeric(precision=10, scale=2), server_default=sa.text('0')),
        sa.Column('monthly_charges', sa.Numeric(precision=10, scale=2), server_default=sa.text('0')),
        sa.Column('other_charges', sa.Numeric(precision=10, scale=2), server_default=sa.text('0')),
        
        # Payment Collection Frequency: 'Monthly', 'Quarterly', 'Half-Yearly', 'Yearly'
        sa.Column('frequency', sa.String(20), nullable=False, server_default=sa.text("'Monthly'")),
        
        # Audit fields
        sa.Column('created_by', sa.String(100), nullable=False, server_default=sa.text("'system'")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('modified_by', sa.String(100), nullable=True),
        sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
        
        # Constraints
        sa.CheckConstraint("payment_type IN ('Fixed', 'User-Based')", name='chk_payment_type'),
        sa.CheckConstraint("frequency IN ('Monthly', 'Quarterly', 'Half-Yearly', 'Yearly')", name='chk_frequency'),
        sa.ForeignKeyConstraint(['tenant_id'], ['hrm_tenant.id'], ondelete='CASCADE', name='fk_payment_config_tenant'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index for hrm_tenant_payment_config
    op.create_index('idx_hrm_tenant_payment_tenant_id', 'hrm_tenant_payment_config', ['tenant_id'])
    
    # Add table comments
    op.execute("COMMENT ON TABLE hrm_tenant_payment_config IS 'Tenant payment configuration for billing management'")
    op.execute("COMMENT ON COLUMN hrm_tenant_payment_config.payment_type IS 'Payment type: Fixed or User-Based'")
    op.execute("COMMENT ON COLUMN hrm_tenant_payment_config.frequency IS 'Payment collection frequency'")
    
    # 2. CREATE hrm_tenant_documents TABLE
    op.create_table(
        'hrm_tenant_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        
        # Audit fields
        sa.Column('uploaded_by', sa.String(100), nullable=False),
        sa.Column('upload_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        
        # Constraints
        sa.ForeignKeyConstraint(['tenant_id'], ['hrm_tenant.id'], ondelete='CASCADE', name='fk_tenant_documents_tenant'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index for hrm_tenant_documents
    op.create_index('idx_hrm_tenant_documents_tenant_id', 'hrm_tenant_documents', ['tenant_id'])
    
    # Add table comments
    op.execute("COMMENT ON TABLE hrm_tenant_documents IS 'Tenant document attachments'")
    op.execute("COMMENT ON COLUMN hrm_tenant_documents.file_path IS 'Relative path under static/uploads/'")
    op.execute("COMMENT ON COLUMN hrm_tenant_documents.file_type IS 'Document type: Contract, Agreement, License, etc.'")
    
    # 3. CREATE TRIGGERS FOR AUTO-UPDATING modified_at
    op.execute("""
        DROP TRIGGER IF EXISTS trg_hrm_tenant_payment_config_modified_at ON hrm_tenant_payment_config;
        CREATE TRIGGER trg_hrm_tenant_payment_config_modified_at
            BEFORE UPDATE ON hrm_tenant_payment_config
            FOR EACH ROW
            EXECUTE FUNCTION update_modified_at_column();
    """)


def downgrade():
    """Downgrade migration - Remove tenant payment and documents tables"""
    
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trg_hrm_tenant_payment_config_modified_at ON hrm_tenant_payment_config")
    
    # Drop tables
    op.drop_table('hrm_tenant_documents')
    op.drop_table('hrm_tenant_payment_config')