# Company-Specific Employee ID Configuration

## Overview

The HRMS has been updated to support **company-specific employee ID sequences**. Instead of using a global PostgreSQL sequence that increments across all companies, each company now maintains its own independent sequence starting from 1.

## Changes Made

### 1. New Model: `CompanyEmployeeIdConfig`
**Location:** `models.py`

A new table `hrm_company_employee_id_config` tracks the ID sequence for each company:

```
Columns:
- id: Primary key (Integer)
- company_id: FK to hrm_company (UUID)
- last_sequence_number: Current sequence counter (Integer)
- id_prefix: Company code/prefix (String(10))
- created_by: Audit field (String)
- created_at: Audit field (DateTime)
- modified_by: Audit field (String)
- modified_at: Audit field (DateTime)
```

**Key Features:**
- One config per company (unique constraint on company_id)
- Includes audit trail (created_by, modified_by timestamps)
- Automatically incremented on each new employee

### 2. New Utility Function: `get_company_employee_id()`
**Location:** `utils.py`

Generates company-specific employee IDs:

```python
def get_company_employee_id(company_id, company_code, db_session):
    """
    Generate a company-specific employee ID.
    Format: CompanyCode + Sequential Number (e.g., ACME001, ACME002)
    
    - Automatically creates config if it doesn't exist
    - Thread-safe with database transactions
    - Returns next ID and increments counter
    """
```

**Example Usage:**
```python
from utils import get_company_employee_id

employee_id = get_company_employee_id(company_id, "ACME", db.session)
# Returns: "ACME001", then "ACME002", etc.
```

### 3. Updated Employee Creation
**Location:** `routes.py` - `employee_add()` function

The employee creation flow now:
1. Gets the company ID from the form
2. Retrieves the company object
3. Calls `get_company_employee_id()` to generate the next ID
4. Automatically initializes the config if needed
5. Falls back to the old method if something goes wrong

## Migration / Setup

### Step 1: Create the New Table
The new table is automatically created when you run migrations:

```bash
flask db migrate -m "Add company employee ID configuration"
flask db upgrade
```

### Step 2: Initialize Existing Companies
Run the initialization script to populate the config table for all existing companies:

```bash
python init_company_employee_id_config.py
```

This script will:
- Create `CompanyEmployeeIdConfig` entries for each company
- Scan existing employees to determine the current sequence
- Set `last_sequence_number` based on existing employee IDs
- Provide detailed output of what was created

**Example Output:**
```
============================================================
Company Employee ID Configuration Initialization
============================================================
📋 Found 3 companies
⏭️  Skipping ACME: Config already exists (last_seq=5)
✅ Created config for NEXAR (existing employees: 12, last_seq=12)
✅ Created config for TECH (existing employees: 8, last_seq=8)

✨ Configuration Initialization Complete!
   Created: 2 configs
   Skipped: 1 configs (already exist)
   Total:   3 companies

🔍 Verifying Configuration...
   ACME: last_seq=5, employees=5
   NEXAR: last_seq=12, employees=12
   TECH: last_seq=8, employees=8

✅ All configurations verified!
```

## Employee ID Format

### Before (Global Sequence)
```
ACME001, ACME002, ACME003 (global sequence shared across companies)
NEXAR001 (could be NEXAR101 if ACME had 100 employees)
```

### After (Company-Specific Sequence)
```
Company: ACME
- ACME001, ACME002, ACME003, ACME004, ACME005

Company: NEXAR
- NEXAR001, NEXAR002, NEXAR003, ... (independent sequence)

Company: TECH
- TECH001, TECH002, TECH003, ... (independent sequence)
```

## Database Schema

```sql
CREATE TABLE hrm_company_employee_id_config (
    id INTEGER PRIMARY KEY,
    company_id UUID NOT NULL UNIQUE,
    last_sequence_number INTEGER NOT NULL DEFAULT 0,
    id_prefix VARCHAR(10) NOT NULL,
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    modified_by VARCHAR(100),
    modified_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (company_id) REFERENCES hrm_company(id) ON DELETE CASCADE,
    CONSTRAINT uq_company_id_config UNIQUE(company_id)
);

CREATE INDEX idx_company_employee_id_config_company_id 
ON hrm_company_employee_id_config(company_id);
```

## How It Works

### Employee Creation Flow

```
1. User submits "Add Employee" form with Company = "ACME"
                    ↓
2. routes.employee_add() receives the form
                    ↓
3. Validates the company_id
                    ↓
4. Calls get_company_employee_id(company_id, "ACME", db.session)
                    ↓
5. Function checks if CompanyEmployeeIdConfig exists for ACME
   - If NOT → Creates new config with last_seq=0
   - If YES → Uses existing config
                    ↓
6. Increments last_sequence_number: 0 → 1
                    ↓
7. Returns: "ACME001"
                    ↓
8. Employee created with employee_id = "ACME001"
```

### Sequence Increment Example

```
Company ACME Employee Creation Timeline:

1st Employee → Config: last_seq=0 → Increments to 1 → ID: ACME001
2nd Employee → Config: last_seq=1 → Increments to 2 → ID: ACME002
3rd Employee → Config: last_seq=2 → Increments to 3 → ID: ACME003
...
10th Employee → Config: last_seq=9 → Increments to 10 → ID: ACME010
```

## Backward Compatibility

- Old employee IDs remain unchanged
- Global `generate_employee_id()` function still exists for fallback
- If config creation fails, system falls back to old method
- Existing employees are not affected

## Troubleshooting

### Issue: "Company not found" error
**Solution:** Ensure the company_id exists and the company is active

### Issue: Sequence numbers getting out of sync
**Cause:** Database transaction issues or concurrent writes
**Solution:** Run the initialization script again with proper database locking

### Issue: Duplicate employee IDs
**Cause:** Database constraint violation (unique on employee_id)
**Solution:** Check existing employee IDs and reset sequence if needed

### View Current Configuration
```python
from models import CompanyEmployeeIdConfig

# Get config for a specific company
config = CompanyEmployeeIdConfig.query.filter_by(company_id=company_id).first()
print(f"Prefix: {config.id_prefix}")
print(f"Last Sequence: {config.last_sequence_number}")
print(f"Next ID will be: {config.id_prefix}{(config.last_sequence_number + 1):03d}")
```

## Performance Considerations

- **Lookup Time:** O(1) - Direct database query by company_id
- **Insert Time:** O(1) - Simple increment operation
- **Scalability:** Can handle millions of employees across multiple companies
- **Concurrent Access:** Protected by database transactions

## Future Enhancements

Possible improvements:
1. Custom ID format per company (e.g., date-based, random)
2. ID range reservations for bulk imports
3. ID reuse/recycling policies
4. Analytics dashboard for ID usage per company
5. Export/import of ID configurations

## Files Modified

1. `models.py` - Added `CompanyEmployeeIdConfig` model
2. `routes.py` - Updated employee_add() to use new ID generation
3. `utils.py` - Added `get_company_employee_id()` function
4. `init_company_employee_id_config.py` - New initialization script (NEW)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the initialization script output
3. Verify database constraints with: `SELECT * FROM hrm_company_employee_id_config`