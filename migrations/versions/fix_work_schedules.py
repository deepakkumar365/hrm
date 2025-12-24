"""fix_work_schedules_cols

Revision ID: fix_work_schedules_col
Revises: db8b893ca9d8
Create Date: 2025-12-24 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_work_schedules_col'
down_revision = ('db8b893ca9d8', '010_add_ot_tables', 'add_company_timezone')
branch_labels = None
depends_on = None


def upgrade():
    # Add day columns
    with op.batch_alter_table('hrm_work_schedules', schema=None) as batch_op:
        batch_op.add_column(sa.Column('monday', sa.Boolean(), server_default='true', nullable=True))
        batch_op.add_column(sa.Column('tuesday', sa.Boolean(), server_default='true', nullable=True))
        batch_op.add_column(sa.Column('wednesday', sa.Boolean(), server_default='true', nullable=True))
        batch_op.add_column(sa.Column('thursday', sa.Boolean(), server_default='true', nullable=True))
        batch_op.add_column(sa.Column('friday', sa.Boolean(), server_default='true', nullable=True))
        batch_op.add_column(sa.Column('saturday', sa.Boolean(), server_default='false', nullable=True))
        batch_op.add_column(sa.Column('sunday', sa.Boolean(), server_default='false', nullable=True))
        
        # Drop old columns cleanly
        batch_op.drop_column('start_time')
        batch_op.drop_column('end_time')
        batch_op.drop_column('break_duration')


def downgrade():
    with op.batch_alter_table('hrm_work_schedules', schema=None) as batch_op:
        batch_op.add_column(sa.Column('break_duration', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('end_time', sa.TIME(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('start_time', sa.TIME(), autoincrement=False, nullable=True))
        
        batch_op.drop_column('sunday')
        batch_op.drop_column('saturday')
        batch_op.drop_column('friday')
        batch_op.drop_column('thursday')
        batch_op.drop_column('wednesday')
        batch_op.drop_column('tuesday')
        batch_op.drop_column('monday')
