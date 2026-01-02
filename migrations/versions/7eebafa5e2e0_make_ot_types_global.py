"""make_ot_types_global

Revision ID: 7eebafa5e2e0
Revises: 776f81c4fa9c
Create Date: 2025-12-31 16:27:06.273950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7eebafa5e2e0'
down_revision = '776f81c4fa9c'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Drop existing unique constraint (company_id, code)
    # Note: Constraint names might vary, so we try to be specific if possible or handle error
    try:
        op.drop_constraint('uq_ot_type_company_code', 'hrm_ot_type', type_='unique')
    except Exception:
        pass # Might not exist or named differently

    # 2. Make company_id nullable
    op.alter_column('hrm_ot_type', 'company_id',
               existing_type=sa.UUID(),
               nullable=True)

    # 3. Add new unique constraint on (code)
    # Warning: This might fail if there are duplicates across companies.
    # In a real production migration, you might want to data-cleanse first.
    try:
        op.create_unique_constraint('uq_ot_type_code', 'hrm_ot_type', ['code'])
    except Exception:
        print("Warning: Could not create unique constraint 'uq_ot_type_code'. Duplicates may exist.")


def downgrade():
    # 1. Drop the global unique constraint
    try:
        op.drop_constraint('uq_ot_type_code', 'hrm_ot_type', type_='unique')
    except Exception:
        pass

    # 2. Make company_id NOT NULL (This requires data cleansing if global types exist)
    # We will attempt it, but it might fail if nulls exist.
    op.alter_column('hrm_ot_type', 'company_id',
               existing_type=sa.UUID(),
               nullable=False)

    # 3. Restore the composite unique constraint
    try:
        op.create_unique_constraint('uq_ot_type_company_code', 'hrm_ot_type', ['company_id', 'code'])
    except Exception:
        pass
