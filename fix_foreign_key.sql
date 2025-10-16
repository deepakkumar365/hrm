-- ============================================================
-- Fix Foreign Key and Complete Migration
-- This SQL script will:
-- 1. Create hrm_roles table
-- 2. Copy data from role to hrm_roles
-- 3. Drop OLD foreign key constraint
-- 4. Create NEW foreign key pointing to hrm_roles
-- 5. Drop old role table
-- ============================================================

-- Step 1: Create hrm_roles table if it doesn't exist
CREATE TABLE IF NOT EXISTS hrm_roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) UNIQUE NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 2: Copy data from role to hrm_roles (if hrm_roles is empty)
INSERT INTO hrm_roles (id, name, description, is_active, created_at, updated_at)
SELECT id, name, description, is_active, created_at, updated_at
FROM role
WHERE NOT EXISTS (SELECT 1 FROM hrm_roles)
ORDER BY id;

-- Step 3: Update sequence to continue from max ID
SELECT setval('hrm_roles_id_seq', (SELECT MAX(id) FROM hrm_roles));

-- Step 4: Drop OLD foreign key constraint on hrm_users
-- This is what's preventing you from dropping the 'role' table!
ALTER TABLE hrm_users 
DROP CONSTRAINT IF EXISTS hrm_users_role_id_fkey;

-- Also drop any other constraints that might exist
DO $$ 
DECLARE
    constraint_name TEXT;
BEGIN
    FOR constraint_name IN 
        SELECT tc.constraint_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = 'hrm_users' 
            AND tc.constraint_type = 'FOREIGN KEY'
            AND kcu.column_name = 'role_id'
    LOOP
        EXECUTE 'ALTER TABLE hrm_users DROP CONSTRAINT IF EXISTS ' || constraint_name;
    END LOOP;
END $$;

-- Step 5: Create NEW foreign key pointing to hrm_roles
ALTER TABLE hrm_users
ADD CONSTRAINT hrm_users_role_id_fkey
FOREIGN KEY (role_id) REFERENCES hrm_roles(id);

-- Step 6: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_hrm_roles_name ON hrm_roles(name);
CREATE INDEX IF NOT EXISTS idx_hrm_roles_is_active ON hrm_roles(is_active);

-- Step 7: NOW drop the old 'role' table (this should work now!)
DROP TABLE IF EXISTS role CASCADE;

-- Verification queries
SELECT 'Migration Complete!' AS status;
SELECT 'hrm_roles record count:' AS info, COUNT(*) AS count FROM hrm_roles;
SELECT 'Sample roles:' AS info, id, name FROM hrm_roles ORDER BY id LIMIT 5;

-- Check foreign key
SELECT 
    'Foreign key status:' AS info,
    tc.constraint_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.table_name = 'hrm_users' 
    AND tc.constraint_type = 'FOREIGN KEY'
    AND kcu.column_name = 'role_id';