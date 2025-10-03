"""Remove role column from hrm_users table

Revision ID: remove_role_column
Revises: add_org_address_uen
Create Date: 2025-01-31 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'remove_role_column'
down_revision = 'add_org_address_uen'
branch_labels = None
depends_on = None


def upgrade():
    # Check if the 'role' column exists before trying to drop it
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns('hrm_users')]
    
    if 'role' in columns:
        # Drop the old 'role' column if it exists
        with op.batch_alter_table('hrm_users', schema=None) as batch_op:
            batch_op.drop_column('role')


def downgrade():
    # Add back the role column if needed (though this shouldn't be used)
    with op.batch_alter_table('hrm_users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.String(length=50), nullable=True))