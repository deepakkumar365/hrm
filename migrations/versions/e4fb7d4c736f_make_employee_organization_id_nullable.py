"""Make employee.organization_id nullable

Revision ID: e4fb7d4c736f
Revises: fix_work_schedules_col
Create Date: 2025-12-27 14:03:31.088002

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e4fb7d4c736f'
down_revision = 'fix_work_schedules_col'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('hrm_employee', schema=None) as batch_op:
        batch_op.alter_column('organization_id',
               existing_type=sa.INTEGER(),
               nullable=True)


def downgrade():
    with op.batch_alter_table('hrm_employee', schema=None) as batch_op:
        batch_op.alter_column('organization_id',
               existing_type=sa.INTEGER(),
               nullable=False)
