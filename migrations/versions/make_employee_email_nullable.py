"""Make employee email nullable

Revision ID: make_email_nullable
Revises: fix_nric_null_unique
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'make_email_nullable'
down_revision = 'fix_nric_null_unique'
branch_labels = None
depends_on = None


def upgrade():
    # First, set existing empty strings to NULL
    op.execute("UPDATE hrm_employee SET email = NULL WHERE email = '' OR email IS NOT NULL;")
    
    # Drop the unique constraint if it exists
    try:
        op.drop_constraint('hrm_employee_email_key', 'hrm_employee', type_='unique')
    except Exception:
        pass
    
    # Alter the column to allow NULL
    op.alter_column('hrm_employee', 'email',
               existing_type=sa.String(length=120),
               nullable=True)
    
    # Recreate the unique constraint to allow multiple NULLs
    op.create_unique_constraint('hrm_employee_email_key', 'hrm_employee', ['email'])


def downgrade():
    # Drop the unique constraint
    try:
        op.drop_constraint('hrm_employee_email_key', 'hrm_employee', type_='unique')
    except Exception:
        pass
    
    # Revert to NOT NULL (set empty string for NULL values)
    op.execute("UPDATE hrm_employee SET email = '' WHERE email IS NULL;")
    
    op.alter_column('hrm_employee', 'email',
               existing_type=sa.String(length=120),
               nullable=False)
    
    # Recreate the original unique constraint
    op.create_unique_constraint('hrm_employee_email_key', 'hrm_employee', ['email'])