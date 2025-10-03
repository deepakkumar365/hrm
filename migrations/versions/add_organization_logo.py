"""Add logo_path to organization table

Revision ID: add_organization_logo
Revises: 28f425a665b2
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_organization_logo'
down_revision = '28f425a665b2'
branch_labels = None
depends_on = None


def upgrade():
    # Add logo_path column to organization table
    op.add_column('organization', sa.Column('logo_path', sa.String(length=255), nullable=True))


def downgrade():
    # Remove logo_path column from organization table
    op.drop_column('organization', 'logo_path')