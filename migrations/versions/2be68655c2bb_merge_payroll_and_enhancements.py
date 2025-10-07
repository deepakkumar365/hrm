"""merge_payroll_and_enhancements

Revision ID: 2be68655c2bb
Revises: add_enhancements_001, add_payroll_config
Create Date: 2025-10-07 19:29:16.158543

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2be68655c2bb'
down_revision = ('add_enhancements_001', 'add_payroll_config')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
