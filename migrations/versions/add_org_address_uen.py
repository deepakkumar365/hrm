"""Add address and uen to Organization model

Revision ID: add_org_address_uen
Revises: add_organization_logo
Create Date: 2025-01-30 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_org_address_uen'
down_revision = 'add_organization_logo'
branch_labels = None
depends_on = None


def upgrade():
    # Add address and uen columns to organization table
    with op.batch_alter_table('organization', schema=None) as batch_op:
        batch_op.add_column(sa.Column('address', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('uen', sa.String(length=50), nullable=True))


def downgrade():
    # Remove address and uen columns from organization table
    with op.batch_alter_table('organization', schema=None) as batch_op:
        batch_op.drop_column('uen')
        batch_op.drop_column('address')