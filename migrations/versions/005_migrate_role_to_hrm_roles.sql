-- Migration: Migrate from role table to hrm_roles table
-- Description: This migration creates the new hrm_roles table, migrates all data from the old role table,
--              updates foreign key references, and drops the old role table.
-- Date: 2024

-- Step 1: Create the new hrm_roles table
CREATE TABLE IF NOT EXISTS hrm_roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 2: Migrate data from role to hrm_roles
INSERT INTO hrm_roles (id, name, description, is_active, created_at, updated_at)
SELECT id, name, description, is_active, created_at, updated_at
FROM role
ON CONFLICT (id) DO NOTHING;

-- Step 3: Update the sequence to match the max ID
SELECT setval('hrm_roles_id_seq', (SELECT COALESCE(MAX(id), 1) FROM hrm_roles), true);

-- Step 4: Drop the foreign key constraint on hrm_users.role_id (if it exists)
DO $$ 
BEGIN
    -- Drop the old foreign key constraint
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'hrm_users_role_id_fkey' 
        AND table_name = 'hrm_users'
    ) THEN
        ALTER TABLE hrm_users DROP CONSTRAINT hrm_users_role_id_fkey;
    END IF;
END $$;

-- Step 5: Add new foreign key constraint pointing to hrm_roles
ALTER TABLE hrm_users 
ADD CONSTRAINT hrm_users_role_id_fkey 
FOREIGN KEY (role_id) REFERENCES hrm_roles(id);

-- Step 6: Drop the old role table
DROP TABLE IF EXISTS role CASCADE;

-- Step 7: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_hrm_roles_name ON hrm_roles(name);
CREATE INDEX IF NOT EXISTS idx_hrm_roles_is_active ON hrm_roles(is_active);

-- Verification queries (commented out - uncomment to verify)
-- SELECT 'hrm_roles count:' as info, COUNT(*) as count FROM hrm_roles;
-- SELECT 'Users with roles:' as info, COUNT(*) as count FROM hrm_users WHERE role_id IS NOT NULL;
-- SELECT * FROM hrm_roles ORDER BY id;