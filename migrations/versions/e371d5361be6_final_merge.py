"""final_merge

Revision ID: e371d5361be6
Revises: eb48e83c4e93
Create Date: 2025-12-24 12:11:35.338367

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e371d5361be6'
down_revision = ('eb48e83c4e93', 'leave_allocation_001', 'add_payroll_config', 'add_enhancements_fields')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
