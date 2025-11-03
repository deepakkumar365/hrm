"""Add certification and pass renewal fields to hrm_employee table

Revision ID: add_certification_pass_renewal
Revises: 008_insert_tenant_company_test_data
Create Date: 2024-12-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_certification_pass_renewal'
down_revision = '008_insert_tenant_company_test_data'
branch_labels = None
depends_on = None


def upgrade():
    """Add certification and pass renewal fields to hrm_employee table"""
    # Add new columns for certifications and pass renewals
    try:
        op.add_column('hrm_employee', sa.Column('hazmat_expiry', sa.Date(), nullable=True))
        print("✓ Added hazmat_expiry column to hrm_employee")
    except Exception as e:
        print(f"Note: hazmat_expiry - {str(e)}")

    try:
        op.add_column('hrm_employee', sa.Column('airport_pass_expiry', sa.Date(), nullable=True))
        print("✓ Added airport_pass_expiry column to hrm_employee")
    except Exception as e:
        print(f"Note: airport_pass_expiry - {str(e)}")

    try:
        op.add_column('hrm_employee', sa.Column('psa_pass_number', sa.String(50), nullable=True))
        print("✓ Added psa_pass_number column to hrm_employee")
    except Exception as e:
        print(f"Note: psa_pass_number - {str(e)}")

    try:
        op.add_column('hrm_employee', sa.Column('psa_pass_expiry', sa.Date(), nullable=True))
        print("✓ Added psa_pass_expiry column to hrm_employee")
    except Exception as e:
        print(f"Note: psa_pass_expiry - {str(e)}")


def downgrade():
    """Remove certification and pass renewal fields from hrm_employee table"""
    try:
        op.drop_column('hrm_employee', 'psa_pass_expiry')
        print("✓ Removed psa_pass_expiry column from hrm_employee")
    except Exception as e:
        print(f"Note: {str(e)}")

    try:
        op.drop_column('hrm_employee', 'psa_pass_number')
        print("✓ Removed psa_pass_number column from hrm_employee")
    except Exception as e:
        print(f"Note: {str(e)}")

    try:
        op.drop_column('hrm_employee', 'airport_pass_expiry')
        print("✓ Removed airport_pass_expiry column from hrm_employee")
    except Exception as e:
        print(f"Note: {str(e)}")

    try:
        op.drop_column('hrm_employee', 'hazmat_expiry')
        print("✓ Removed hazmat_expiry column from hrm_employee")
    except Exception as e:
        print(f"Note: {str(e)}")