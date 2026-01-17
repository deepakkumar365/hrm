"""Add hrm_payslip_templates table

Revision ID: add_payslip_templates_001
Revises: add_ot_daily_summary_001
Create Date: 2025-01-10 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_payslip_templates_001'
down_revision = '0b228db6f823'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'hrm_payslip_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logo_path', sa.String(length=255), nullable=True),
        sa.Column('watermark_path', sa.String(length=255), nullable=True),
        sa.Column('footer_image_path', sa.String(length=255), nullable=True),
        sa.Column('layout_config', sa.JSON(), nullable=True),
        sa.Column('field_config', sa.JSON(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['hrm_company.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['hrm_users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['hrm_tenant.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['updated_by'], ['hrm_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_payslip_tmpl_company', 'hrm_payslip_templates', ['company_id'], unique=False)
    op.create_index('ix_payslip_tmpl_tenant', 'hrm_payslip_templates', ['tenant_id'], unique=False)


def downgrade():
    op.drop_index('ix_payslip_tmpl_tenant', table_name='hrm_payslip_templates')
    op.drop_index('ix_payslip_tmpl_company', table_name='hrm_payslip_templates')
    op.drop_table('hrm_payslip_templates')
