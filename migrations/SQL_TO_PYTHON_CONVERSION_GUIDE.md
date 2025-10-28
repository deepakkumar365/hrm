# SQL to Python Migration Conversion Guide

This guide shows how SQL migrations were converted to Python Alembic migrations with practical examples.

---

## 1. Creating Tables with Constraints

### SQL Version
```sql
CREATE TABLE IF NOT EXISTS hrm_tenant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_by VARCHAR(100),
    modified_at TIMESTAMPTZ,
    
    CONSTRAINT chk_tenant_name_not_empty CHECK (LENGTH(TRIM(name)) > 0),
    CONSTRAINT chk_tenant_code_not_empty CHECK (LENGTH(TRIM(code)) > 0)
);

CREATE INDEX IF NOT EXISTS idx_hrm_tenant_code ON hrm_tenant(code);
```

### Python Alembic Version
```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

op.create_table(
    'hrm_tenant',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, 
              server_default=sa.text('gen_random_uuid()')),
    sa.Column('name', sa.String(255), nullable=False, unique=True),
    sa.Column('code', sa.String(50), nullable=False, unique=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False, 
              server_default=sa.text('true')),
    
    sa.Column('created_by', sa.String(100), nullable=False, 
              server_default=sa.text("'system'")),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, 
              server_default=sa.func.now()),
    sa.Column('modified_by', sa.String(100), nullable=True),
    sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
    
    sa.CheckConstraint("LENGTH(TRIM(name)) > 0", name='chk_tenant_name_not_empty'),
    sa.CheckConstraint("LENGTH(TRIM(code)) > 0", name='chk_tenant_code_not_empty'),
    sa.PrimaryKeyConstraint('id')
)

op.create_index('idx_hrm_tenant_code', 'hrm_tenant', ['code'])
```

### Key Conversions
- `UUID PRIMARY KEY DEFAULT gen_random_uuid()` → `postgresql.UUID(as_uuid=True)` with `server_default`
- `VARCHAR(255)` → `sa.String(255)`
- `TEXT` → `sa.Text()`
- `BOOLEAN DEFAULT TRUE` → `sa.Boolean()` with `server_default`
- `NOT NULL DEFAULT 'system'` → `server_default=sa.text("'system'")`
- `CHECK` constraints → `sa.CheckConstraint()`
- Indexes → `op.create_index()`

---

## 2. Foreign Keys with Cascading

### SQL Version
```sql
CREATE TABLE IF NOT EXISTS hrm_company (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    
    CONSTRAINT fk_company_tenant FOREIGN KEY (tenant_id) 
        REFERENCES hrm_tenant(id) ON DELETE CASCADE,
    CONSTRAINT uq_company_tenant_code UNIQUE (tenant_id, code)
);
```

### Python Alembic Version
```python
op.create_table(
    'hrm_company',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, 
              server_default=sa.text('gen_random_uuid()')),
    sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(255), nullable=False),
    
    sa.ForeignKeyConstraint(['tenant_id'], ['hrm_tenant.id'], 
                           ondelete='CASCADE', name='fk_company_tenant'),
    sa.UniqueConstraint('tenant_id', 'code', name='uq_company_tenant_code'),
    sa.PrimaryKeyConstraint('id')
)
```

### Key Conversions
- `FOREIGN KEY ... REFERENCES ... ON DELETE CASCADE` → `sa.ForeignKeyConstraint()` with `ondelete='CASCADE'`
- `UNIQUE (col1, col2)` → `sa.UniqueConstraint('col1', 'col2')`

---

## 3. Conditional Column Additions (Idempotent)

### SQL Version
```sql
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'hrm_employee' AND column_name = 'company_id'
    ) THEN
        ALTER TABLE hrm_employee ADD COLUMN company_id UUID;
        ALTER TABLE hrm_employee 
            ADD CONSTRAINT fk_employee_company 
            FOREIGN KEY (company_id) REFERENCES hrm_company(id) ON DELETE CASCADE;
        CREATE INDEX idx_hrm_employee_company_id ON hrm_employee(company_id);
        RAISE NOTICE 'Added company_id column to hrm_employee table';
    END IF;
END $$;
```

### Python Alembic Version
```python
op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'hrm_employee' AND column_name = 'company_id'
        ) THEN
            ALTER TABLE hrm_employee ADD COLUMN company_id UUID;
            ALTER TABLE hrm_employee 
                ADD CONSTRAINT fk_employee_company 
                FOREIGN KEY (company_id) REFERENCES hrm_company(id) ON DELETE CASCADE;
            CREATE INDEX idx_hrm_employee_company_id ON hrm_employee(company_id);
            RAISE NOTICE 'Added company_id column to hrm_employee table';
        END IF;
    END $$;
""")
```

### Key Conversions
- **Direct PostgreSQL SQL kept as-is** - Wrap in `op.execute()` when complex PL/pgSQL needed
- **Idempotent checks** - Use `IF NOT EXISTS` to make safe for re-runs
- Complex conditionals → Use raw SQL in `op.execute()`

---

## 4. Trigger Function Creation

### SQL Version
```sql
CREATE OR REPLACE FUNCTION update_modified_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_hrm_tenant_modified_at ON hrm_tenant;
CREATE TRIGGER trg_hrm_tenant_modified_at
    BEFORE UPDATE ON hrm_tenant
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_at_column();
```

### Python Alembic Version
```python
op.execute("""
    CREATE OR REPLACE FUNCTION update_modified_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.modified_at = NOW();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
""")

op.execute("""
    DROP TRIGGER IF EXISTS trg_hrm_tenant_modified_at ON hrm_tenant;
    CREATE TRIGGER trg_hrm_tenant_modified_at
        BEFORE UPDATE ON hrm_tenant
        FOR EACH ROW
        EXECUTE FUNCTION update_modified_at_column();
""")
```

### Key Conversions
- PL/pgSQL functions → Keep in raw SQL wrapped in `op.execute()`
- Triggers → Use raw SQL wrapped in `op.execute()`
- `DROP TRIGGER IF EXISTS` → Keep for idempotency

---

## 5. Data Insertion (Upsert Pattern)

### SQL Version
```sql
INSERT INTO hrm_tenant (id, name, code, description, is_active, created_by, created_at)
VALUES 
    ('00000000-0000-0000-0000-000000000001'::UUID, 'Noltrion HRM', 'NOLTRION', 
     'Noltrion Group - Global HRMS Tenant', TRUE, 'admin@noltrion.com', NOW())
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    modified_by = 'admin@noltrion.com',
    modified_at = NOW();
```

### Python Alembic Version
```python
op.execute("""
    INSERT INTO hrm_tenant (id, name, code, description, is_active, created_by, created_at)
    VALUES 
        ('00000000-0000-0000-0000-000000000001'::UUID, 'Noltrion HRM', 'NOLTRION', 
         'Noltrion Group - Global HRMS Tenant', TRUE, 'admin@noltrion.com', NOW())
    ON CONFLICT (code) DO UPDATE SET
        name = EXCLUDED.name,
        description = EXCLUDED.description,
        modified_by = 'admin@noltrion.com',
        modified_at = NOW();
""")
```

### Key Conversions
- INSERT statements → Keep as raw SQL in `op.execute()`
- `ON CONFLICT ... DO UPDATE` → PostgreSQL syntax preserved
- UUIDs → Use `'uuid-string'::UUID` format in SQL

---

## 6. Data Updates with Conditions

### SQL Version
```sql
UPDATE hrm_employee 
SET 
    company_id = '00000000-0000-0000-0000-000000000102'::UUID,
    modified_by = 'admin@noltrion.com',
    modified_at = NOW()
WHERE id IN (
    SELECT id FROM hrm_employee 
    WHERE company_id IS NULL 
    ORDER BY id 
    LIMIT 3
);
```

### Python Alembic Version
```python
op.execute("""
    UPDATE hrm_employee 
    SET 
        company_id = '00000000-0000-0000-0000-000000000102'::UUID,
        modified_by = 'admin@noltrion.com',
        modified_at = NOW()
    WHERE id IN (
        SELECT id FROM hrm_employee 
        WHERE company_id IS NULL 
        ORDER BY id 
        LIMIT 3
    );
""")
```

### Key Conversions
- UPDATE statements → Raw SQL in `op.execute()`
- WHERE conditions → Kept as-is
- Subqueries → PostgreSQL syntax preserved

---

## 7. Comments/Documentation

### SQL Version
```sql
COMMENT ON TABLE hrm_tenant IS 'Top-level tenant entity for multi-tenant HRMS';
COMMENT ON COLUMN hrm_tenant.code IS 'Unique tenant code for identification';
```

### Python Alembic Version
```python
op.execute("COMMENT ON TABLE hrm_tenant IS 'Top-level tenant entity for multi-tenant HRMS'")
op.execute("COMMENT ON COLUMN hrm_tenant.code IS 'Unique tenant code for identification'")
```

### Key Conversions
- COMMENT statements → Simple `op.execute()` calls

---

## 8. Column Renaming

### SQL Version
```sql
IF EXISTS (SELECT 1 FROM information_schema.columns 
           WHERE table_name = 'hrm_employee' AND column_name = 'updated_at') THEN
    ALTER TABLE hrm_employee RENAME COLUMN updated_at TO modified_at;
END IF;
```

### Python Alembic Version
```python
op.execute("""
    DO $$ 
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'hrm_employee' AND column_name = 'updated_at'
        ) THEN
            ALTER TABLE hrm_employee RENAME COLUMN updated_at TO modified_at;
        END IF;
    END $$;
""")

# Or use Alembic API (if column is guaranteed to exist):
op.alter_column('hrm_employee', 'updated_at', new_column_name='modified_at')
```

### Key Conversions
- **Conditional rename** → PL/pgSQL wrapped in `op.execute()`
- **Direct rename** → Can use `op.alter_column()` if safe
- **Always check first** → Use IF EXISTS for idempotency

---

## 9. Downgrade Functions

### SQL Version (No downgrade)
```sql
-- One-way migration, no rollback defined
```

### Python Alembic Version (Proper Rollback)
```python
def downgrade():
    """Downgrade migration - Remove tenant company hierarchy schema"""
    
    # Drop triggers in reverse order
    op.execute("DROP TRIGGER IF EXISTS trg_organization_modified_at ON organization")
    op.execute("DROP TRIGGER IF EXISTS trg_hrm_employee_modified_at ON hrm_employee")
    op.execute("DROP TRIGGER IF EXISTS trg_hrm_company_modified_at ON hrm_company")
    op.execute("DROP TRIGGER IF EXISTS trg_hrm_tenant_modified_at ON hrm_tenant")
    
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_modified_at_column()")
    
    # Remove columns from existing tables
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'hrm_employee' AND column_name = 'company_id'
            ) THEN
                ALTER TABLE hrm_employee DROP CONSTRAINT IF EXISTS fk_employee_company;
                ALTER TABLE hrm_employee DROP COLUMN company_id;
            END IF;
        END $$;
    """)
    
    # Drop tables in reverse order
    op.drop_table('hrm_company')
    op.drop_table('hrm_tenant')
```

### Key Conversions
- **Downgrade defined** - Every upgrade() must have corresponding downgrade()
- **Reverse order** - Drop in reverse of creation order
- **Conditional drops** - Use IF EXISTS for safety
- **Constraints first** - Remove foreign keys before dropping tables

---

## Best Practices for Migration Conversion

### ✅ Do's
1. **Use `op.create_table()` for new tables** - More maintainable than raw SQL
2. **Use `op.add_column()` for simple additions** - Clearer intent
3. **Keep complex SQL in `op.execute()`** - When PL/pgSQL needed
4. **Always include `downgrade()`** - For rollback capability
5. **Make migrations idempotent** - Use `IF NOT EXISTS` / `IF EXISTS`
6. **Use proper type hints** - `sa.String()`, `sa.Integer()`, etc.
7. **Name constraints explicitly** - `name='fk_...'` for clarity
8. **Document the migration** - Add detailed docstring
9. **Test both up and down** - Verify rollback works

### ❌ Don'ts
1. **Don't mix DDL and DML unnecessarily** - Keep schemas separate from data
2. **Don't assume column/table existence** - Use IF EXISTS checks
3. **Don't use raw SQL for simple operations** - Use Alembic API when possible
4. **Don't skip downgrade()** - Always support rollback
5. **Don't reference migrations by name in code** - Use revision IDs
6. **Don't change migration files after they're committed** - Create new ones instead
7. **Don't hardcode server-specific logic** - Use dialect-agnostic approaches where possible

---

## PostgreSQL-Specific Features Used

| Feature | Example | Purpose |
|---------|---------|---------|
| **UUID-OSSP** | `gen_random_uuid()` | Generate UUIDs automatically |
| **TIMESTAMPTZ** | `TIMESTAMPTZ NOT NULL` | Timezone-aware timestamps |
| **Triggers** | `CREATE TRIGGER...` | Auto-update timestamp columns |
| **PL/pgSQL** | `DO $$ ... END $$;` | Conditional DDL execution |
| **ON CONFLICT** | `ON CONFLICT ... DO UPDATE` | Upsert pattern |
| **INFORMATION_SCHEMA** | `information_schema.columns` | Check column existence |

---

## Migration Template for Future Use

```python
"""Short description of what this migration does

Revision ID: NNN_migration_name
Revises: previous_migration_id
Create Date: YYYY-MM-DD

Detailed explanation of changes.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'NNN_migration_name'
down_revision = 'previous_migration_id'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade migration - Add/modify schema"""
    # TODO: Implement upgrade logic
    pass


def downgrade():
    """Downgrade migration - Rollback changes"""
    # TODO: Implement downgrade logic
    pass
```

---

## Reference Links

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Types](https://docs.sqlalchemy.org/en/14/core/types.html)
- [PostgreSQL UUID Type](https://www.postgresql.org/docs/current/uuid-type.html)
- [PostgreSQL Triggers](https://www.postgresql.org/docs/current/sql-createtrigger.html)
- [Alembic Operations](https://alembic.sqlalchemy.org/en/latest/ops.html)
