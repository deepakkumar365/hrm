"""Add is_manager column to hrm_employee table

Revision ID: add_is_manager
Revises: 
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_is_manager'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add is_manager column with default value False
    op.add_column('hrm_employee', sa.Column('is_manager', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    # Remove is_manager column
    op.drop_column('hrm_employee', 'is_manager')