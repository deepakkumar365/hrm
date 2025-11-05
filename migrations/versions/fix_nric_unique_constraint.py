"""Fix NRIC unique constraint to allow multiple NULL values

Revision ID: fix_nric_null_unique
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_nric_null_unique'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Drop the existing unique constraint on nric if it exists
    with op.batch_operations.batch_alter_table('hrm_employee', schema=None) as batch_op:
        # Try to drop the constraint if it exists
        try:
            batch_op.drop_constraint('hrm_employee_nric_key', type_='unique')
        except:
            pass
    
    # Create a partial unique index that allows NULL values
    # This allows multiple NULL values but prevents duplicate non-NULL values
    op.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_nric_unique_partial 
        ON hrm_employee(nric) 
        WHERE nric IS NOT NULL
    ''')


def downgrade():
    # Drop the partial unique index
    op.execute('DROP INDEX IF EXISTS idx_nric_unique_partial')
    
    # Recreate the unique constraint (optional, for rollback)
    # op.create_unique_constraint('hrm_employee_nric_key', 'hrm_employee', ['nric'])