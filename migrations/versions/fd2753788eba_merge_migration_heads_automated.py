"""merge_migration_heads_automated

Revision ID: fd2753788eba
Revises: add_ot_quantity_cols, e4fb7d4c736f
Create Date: 2025-12-27 16:01:51.117717

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd2753788eba'
down_revision = ('add_ot_quantity_cols', 'e4fb7d4c736f')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
