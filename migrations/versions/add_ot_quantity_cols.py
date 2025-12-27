"""Add quantity, rate, amount to OTAttendance

Revision ID: add_ot_quantity_cols
Revises: remove_role_column
Create Date: 2025-12-27 15:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'add_ot_quantity_cols'
down_revision = 'remove_role_column'
branch_labels = None
depends_on = None


def upgrade():
    # Helper to check if column exists
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns('hrm_ot_attendance')]

    with op.batch_alter_table('hrm_ot_attendance', schema=None) as batch_op:
        if 'quantity' not in columns:
            batch_op.add_column(sa.Column('quantity', sa.Numeric(precision=6, scale=2), server_default='0', nullable=True))
        if 'rate' not in columns:
            batch_op.add_column(sa.Column('rate', sa.Numeric(precision=8, scale=2), server_default='0', nullable=True))
        if 'amount' not in columns:
            batch_op.add_column(sa.Column('amount', sa.Numeric(precision=10, scale=2), server_default='0', nullable=True))


def downgrade():
    with op.batch_alter_table('hrm_ot_attendance', schema=None) as batch_op:
        batch_op.drop_column('amount')
        batch_op.drop_column('rate')
        batch_op.drop_column('quantity')
