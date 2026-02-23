"""add scope column to report schedule

Revision ID: add_report_scope
Revises: 
Create Date: 2026-02-23
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'add_report_scope'
down_revision = '7c5d97703251'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('hrm_report_schedule',
        sa.Column('scope', sa.String(20), nullable=False, server_default='single')
    )


def downgrade():
    op.drop_column('hrm_report_schedule', 'scope')
