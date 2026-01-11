"""add_payslip_logos

Revision ID: add_payslip_logos
Revises: add_payslip_templates_table
Create Date: 2026-01-10 21:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_payslip_logos'
down_revision = 'add_payslip_templates_001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('hrm_payslip_templates', sa.Column('left_logo_path', sa.String(length=255), nullable=True))
    op.add_column('hrm_payslip_templates', sa.Column('right_logo_path', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('hrm_payslip_templates', 'right_logo_path')
    op.drop_column('hrm_payslip_templates', 'left_logo_path')
