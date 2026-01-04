"""Fix missing columns in working hours and attendance

Revision ID: 0b228db6f823
Revises: c2d2f9ba8d12
Create Date: 2026-01-04 15:19:07.569588

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b228db6f823'
down_revision = 'c2d2f9ba8d12'
branch_labels = None
depends_on = None


def upgrade():
    # Use inspector to check for column existence (idempotent fix for production sync)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # 1. Check hrm_working_hours for grace_period
    wh_columns = [col['name'] for col in inspector.get_columns('hrm_working_hours')]
    if 'grace_period' not in wh_columns:
        with op.batch_alter_table('hrm_working_hours', schema=None) as batch_op:
            batch_op.add_column(sa.Column('grace_period', sa.Integer(), nullable=True, server_default='15'))
    
    # 2. Check hrm_attendance for late/early flags
    attn_columns = [col['name'] for col in inspector.get_columns('hrm_attendance')]
    missing_attn = []
    if 'is_late' not in attn_columns:
        missing_attn.append(sa.Column('is_late', sa.Boolean(), nullable=True, server_default='false'))
    if 'is_early_departure' not in attn_columns:
        missing_attn.append(sa.Column('is_early_departure', sa.Boolean(), nullable=True, server_default='false'))
    if 'late_minutes' not in attn_columns:
        missing_attn.append(sa.Column('late_minutes', sa.Integer(), nullable=True, server_default='0'))
    if 'early_departure_minutes' not in attn_columns:
        missing_attn.append(sa.Column('early_departure_minutes', sa.Integer(), nullable=True, server_default='0'))
    
    if missing_attn:
        with op.batch_alter_table('hrm_attendance', schema=None) as batch_op:
            for col in missing_attn:
                batch_op.add_column(col)

    # 3. Check hrm_attendance_segments table
    tables = inspector.get_table_names()
    if 'hrm_attendance_segments' not in tables:
        op.create_table('hrm_attendance_segments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('attendance_id', sa.Integer(), nullable=False),
            sa.Column('segment_type', sa.String(length=20), nullable=True),
            sa.Column('clock_in', sa.DateTime(), nullable=False),
            sa.Column('clock_out', sa.DateTime(), nullable=True),
            sa.Column('duration_minutes', sa.Integer(), nullable=True),
            sa.Column('location_lat', sa.String(length=20), nullable=True),
            sa.Column('location_lng', sa.String(length=20), nullable=True),
            sa.Column('remarks', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['attendance_id'], ['hrm_attendance.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade():
    # Downgrade is optional/not recommended for fix-up scripts, but here for completeness
    with op.batch_alter_table('hrm_working_hours', schema=None) as batch_op:
        batch_op.drop_column('grace_period')
    
    with op.batch_alter_table('hrm_attendance', schema=None) as batch_op:
        batch_op.drop_column('early_departure_minutes')
        batch_op.drop_column('late_minutes')
        batch_op.drop_column('is_early_departure')
        batch_op.drop_column('is_late')
    
    op.drop_table('hrm_attendance_segments')
