"""Migrate role table to hrm_roles

Revision ID: 005_migrate_role_to_hrm_roles
Revises: 
Create Date: 2024-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_migrate_role_to_hrm_roles'
down_revision = None  # Update this to the previous migration ID if needed
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database: Migrate from role to hrm_roles table"""
    
    # Step 1: Create the new hrm_roles table
    op.create_table(
        'hrm_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Step 2: Create indexes
    op.create_index('idx_hrm_roles_name', 'hrm_roles', ['name'], unique=False)
    op.create_index('idx_hrm_roles_is_active', 'hrm_roles', ['is_active'], unique=False)
    
    # Step 3: Migrate data from role to hrm_roles
    connection = op.get_bind()
    
    # Check if role table exists
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'role' in tables:
        # Copy all data from role to hrm_roles
        connection.execute(sa.text("""
            INSERT INTO hrm_roles (id, name, description, is_active, created_at, updated_at)
            SELECT id, name, description, is_active, created_at, updated_at
            FROM role
            ON CONFLICT (id) DO NOTHING
        """))
        
        # Update the sequence
        connection.execute(sa.text("""
            SELECT setval('hrm_roles_id_seq', (SELECT COALESCE(MAX(id), 1) FROM hrm_roles), true)
        """))
        
        # Step 4: Drop the old foreign key constraint on hrm_users.role_id
        try:
            op.drop_constraint('hrm_users_role_id_fkey', 'hrm_users', type_='foreignkey')
        except Exception as e:
            print(f"Note: Could not drop old constraint (may not exist): {e}")
        
        # Step 5: Add new foreign key constraint pointing to hrm_roles
        op.create_foreign_key(
            'hrm_users_role_id_fkey',
            'hrm_users', 'hrm_roles',
            ['role_id'], ['id']
        )
        
        # Step 6: Drop the old role table
        op.drop_table('role')
        
        print("✅ Successfully migrated role table to hrm_roles")
        print(f"   Migrated {connection.execute(sa.text('SELECT COUNT(*) FROM hrm_roles')).scalar()} roles")
    else:
        print("⚠️  role table does not exist, skipping data migration")


def downgrade():
    """Downgrade database: Revert hrm_roles back to role table"""
    
    # Step 1: Create the old role table
    op.create_table(
        'role',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Step 2: Migrate data back from hrm_roles to role
    connection = op.get_bind()
    connection.execute(sa.text("""
        INSERT INTO role (id, name, description, is_active, created_at, updated_at)
        SELECT id, name, description, is_active, created_at, updated_at
        FROM hrm_roles
        ON CONFLICT (id) DO NOTHING
    """))
    
    # Update the sequence
    connection.execute(sa.text("""
        SELECT setval('role_id_seq', (SELECT COALESCE(MAX(id), 1) FROM role), true)
    """))
    
    # Step 3: Drop the foreign key constraint on hrm_users.role_id
    op.drop_constraint('hrm_users_role_id_fkey', 'hrm_users', type_='foreignkey')
    
    # Step 4: Add back the old foreign key constraint
    op.create_foreign_key(
        'hrm_users_role_id_fkey',
        'hrm_users', 'role',
        ['role_id'], ['id']
    )
    
    # Step 5: Drop indexes from hrm_roles
    op.drop_index('idx_hrm_roles_is_active', table_name='hrm_roles')
    op.drop_index('idx_hrm_roles_name', table_name='hrm_roles')
    
    # Step 6: Drop the hrm_roles table
    op.drop_table('hrm_roles')
    
    print("✅ Successfully reverted hrm_roles back to role table")