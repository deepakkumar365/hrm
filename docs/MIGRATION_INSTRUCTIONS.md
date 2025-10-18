# Database Migration Instructions

## Adding Organization Logo Support

### Quick Start

Run this command from the project root directory:

```powershell
# Navigate to project directory
Set-Location "E:/Gobi/Pro/HRMS/hrm"

# Apply the migration
python -m flask db upgrade
```

---

## What This Migration Does

Adds a new column `logo_path` to the `organization` table:
- **Column Name:** `logo_path`
- **Type:** VARCHAR(255)
- **Nullable:** Yes (optional field)
- **Purpose:** Store relative path to company logo (e.g., `logos/company_logo.png`)

---

## After Migration

### 1. Create Logos Directory

```powershell
# Create directory for logos
New-Item -ItemType Directory -Path "E:/Gobi/Pro/HRMS/hrm/static/logos" -Force
```

### 2. Upload Company Logo

Place your company logo in the `static/logos/` directory:
- Supported formats: PNG, JPG, SVG
- Recommended size: 120px × 80px (or similar aspect ratio)
- Example: `static/logos/noltrion_logo.png`

### 3. Update Organization Record

**Option A: Using Python Shell**
```python
from app import app, db
from models import Organization

with app.app_context():
    org = Organization.query.first()
    org.logo_path = 'logos/noltrion_logo.png'  # Relative to static/
    db.session.commit()
    print(f"Logo path updated for {org.name}")
```

**Option B: Using SQL**
```sql
UPDATE organization 
SET logo_path = 'logos/noltrion_logo.png' 
WHERE id = 1;
```

**Option C: Via Admin Interface**
(If you have an organization management page, add a logo upload field)

---

## Verification

### Check Migration Status
```powershell
python -m flask db current
```

Should show: `add_organization_logo (head)`

### Check Database
```powershell
# Using Python shell
python

>>> from app import app, db
>>> from models import Organization
>>> with app.app_context():
...     org = Organization.query.first()
...     print(f"Name: {org.name}")
...     print(f"Logo: {org.logo_path}")
```

### Test Payslip
1. Navigate to any payslip
2. Logo should appear at the top (if logo_path is set)
3. If logo_path is NULL, building icon will show (fallback)

---

## Rollback (If Needed)

To undo this migration:

```powershell
python -m flask db downgrade
```

This will remove the `logo_path` column from the `organization` table.

---

## Troubleshooting

### Error: "Can't locate revision identified by 'add_organization_logo'"

**Solution:** The migration file might not be detected. Check:
```powershell
# List all migrations
python -m flask db history

# If not listed, ensure file is in migrations/versions/
Get-ChildItem "E:/Gobi/Pro/HRMS/hrm/migrations/versions/"
```

### Error: "Column 'logo_path' already exists"

**Solution:** Migration already applied. Check current version:
```powershell
python -m flask db current
```

### Error: "No such table: organization"

**Solution:** Run initial migration first:
```powershell
python -m flask db upgrade
```

---

## File Locations

- **Migration File:** `migrations/versions/add_organization_logo.py`
- **Model File:** `models.py` (Organization class)
- **Logo Directory:** `static/logos/`
- **Template File:** `templates/payroll/payslip.html`

---

## Notes

- Logo path is stored relative to the `static/` directory
- If no logo is set, the payslip will show a building icon (fallback)
- Logo dimensions are automatically constrained to 120px × 80px in the template
- Logo will appear in both screen view and printed PDF

---

**Status:** Ready to Apply ✅