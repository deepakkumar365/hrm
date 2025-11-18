"""Add UserCompanyAccess junction table for multi-company support

Revision ID: add_user_company_access
Revises: add_certification_pass_renewal
Create Date: 2024-12-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'add_user_company_access'
down_revision = 'add_certification_pass_renewal'
branch_labels = None
depends_on = None


def upgrade():
    """Create hrm_user_company_access junction table"""
    try:
        op.create_table(
            'hrm_user_company_access',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('company_id', UUID(as_uuid=True), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('modified_at', sa.DateTime(), nullable=True),
            
            sa.ForeignKeyConstraint(['user_id'], ['hrm_users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['company_id'], ['hrm_company.id'], ondelete='CASCADE'),
            sa.UniqueConstraint('user_id', 'company_id', name='uq_user_company_access'),
        )
        print("✓ Created hrm_user_company_access junction table")
        
        # Add index on company_id for faster lookups
        op.create_index('ix_user_company_access_company_id', 'hrm_user_company_access', ['company_id'])
        print("✓ Created index on hrm_user_company_access.company_id")
        
        # Add index on user_id for faster lookups
        op.create_index('ix_user_company_access_user_id', 'hrm_user_company_access', ['user_id'])
        print("✓ Created index on hrm_user_company_access.user_id")
        
    except Exception as e:
        print(f"Note: hrm_user_company_access - {str(e)}")


def downgrade():
    """Drop hrm_user_company_access junction table"""
    try:
        op.drop_index('ix_user_company_access_user_id', 'hrm_user_company_access')
        op.drop_index('ix_user_company_access_company_id', 'hrm_user_company_access')
        op.drop_table('hrm_user_company_access')
        print("✓ Dropped hrm_user_company_access junction table")
    except Exception as e:
        print(f"Note: Failed to drop table - {str(e)}")