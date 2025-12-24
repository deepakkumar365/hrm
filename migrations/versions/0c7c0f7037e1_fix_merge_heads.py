"""fix_merge_heads

Revision ID: 0c7c0f7037e1
Revises: add_ot_daily_summary_001, add_user_company_access, TEMPLATE_DROP_USER_NAMES, merge_migration_heads
Create Date: 2025-12-24 11:03:13.391146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c7c0f7037e1'
down_revision = ('add_ot_daily_summary_001', 'add_user_company_access', 'TEMPLATE_DROP_USER_NAMES', 'merge_migration_heads')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
