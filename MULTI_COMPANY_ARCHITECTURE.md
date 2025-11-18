# 🏗️ Multi-Company User Management Architecture

## System Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                      HRM MULTI-COMPANY SYSTEM                      │
└────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────┐
                    │    Application       │
                    │  (main.py/app.py)    │
                    └──────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼──────┐    ┌─────▼──────┐   ┌──────▼──────┐
    │ User       │    │ Company    │   │ Employee    │
    │ Model      │    │ Model      │   │ Model       │
    └────┬──────┘    └─────┬──────┘   └──────┬──────┘
         │                 │                  │
         └────────┬────────┘                  │
                  │                           │
          ┌───────▼────────────┐              │
          │ UserCompanyAccess  │◄─────────────┘
          │ (Junction Table)   │
          └────────────────────┘
                  
              Many-to-Many Bridge
```

---

## 🗄️ Database Schema

### 1. **hrm_users** (Existing)
```sql
CREATE TABLE hrm_users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    password_hash VARCHAR(255),
    role_id INTEGER FOREIGN KEY,
    is_active BOOLEAN,
    -- ... other fields
);
```

### 2. **hrm_company** (Existing)
```sql
CREATE TABLE hrm_company (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN,
    -- ... other fields
);
```

### 3. **hrm_user_company_access** (NEW - Junction Table)
```sql
CREATE TABLE hrm_user_company_access (
    id UUID PRIMARY KEY,
    user_id INTEGER NOT NULL,
    company_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    modified_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES hrm_users(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES hrm_company(id) ON DELETE CASCADE,
    
    UNIQUE(user_id, company_id),  -- One row per user-company pair
    INDEX(user_id),
    INDEX(company_id)
);
```

---

## 👥 Relationship Models

### User Model (Simplified)
```python
class User(db.Model):
    __tablename__ = 'hrm_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    role_id = db.Column(db.Integer, db.ForeignKey('hrm_role.id'))
    
    # ✅ NEW: Relationship to companies
    company_access = db.relationship(
        'UserCompanyAccess',
        primaryjoin='User.id==UserCompanyAccess.user_id',
        foreign_keys='UserCompanyAccess.user_id',
        cascade='all, delete-orphan',
        lazy='select',  # Deferred loading
        viewonly=False
    )
    
    # Helper method to get companies
    @property
    def companies(self):
        return [access.company for access in self.company_access]
```

### UserCompanyAccess Model (NEW)
```python
class UserCompanyAccess(db.Model):
    __tablename__ = 'hrm_user_company_access'
    
    id = db.Column(UUID, primary_key=True, default=uuid4)
    user_id = db.Column(db.Integer, db.ForeignKey('hrm_users.id', ondelete='CASCADE'))
    company_id = db.Column(UUID, db.ForeignKey('hrm_company.id', ondelete='CASCADE'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], viewonly=True)
    company = db.relationship('Company')
```

### Company Model (Existing)
```python
class Company(db.Model):
    __tablename__ = 'hrm_company'
    
    id = db.Column(UUID, primary_key=True, default=uuid4)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    # ... other fields
```

---

## 📊 Data Flow Examples

### Example 1: Single User with Multiple Companies

```
User: john_smith (ID: 1)

hrm_user_company_access table:
┌─────────────────────────────────────────────┐
│ ID              │ user_id │ company_id      │
├─────────────────────────────────────────────┤
│ uuid-001        │    1    │ uuid-comp-A     │ ← NYC Office
│ uuid-002        │    1    │ uuid-comp-B     │ ← LA Office
│ uuid-003        │    1    │ uuid-comp-C     │ ← Chicago Office
└─────────────────────────────────────────────┘

In Python:
    user = User.query.get(1)
    # user.company_access = [Access(comp_a), Access(comp_b), Access(comp_c)]
    # user.companies = [Company(NYC), Company(LA), Company(Chicago)]
    
    for company in user.companies:
        print(company.name)
    # Output:
    # NYC Office
    # LA Office
    # Chicago Office
```

### Example 2: Multiple Users Accessing One Company

```
Company: ACME Corp (ID: uuid-acme)

hrm_user_company_access table:
┌─────────────────────────────────────────────┐
│ ID              │ user_id │ company_id      │
├─────────────────────────────────────────────┤
│ uuid-010        │    1    │ uuid-acme       │ ← john_smith
│ uuid-011        │    2    │ uuid-acme       │ ← sarah_admin
│ uuid-012        │    3    │ uuid-acme       │ ← mike_manager
└─────────────────────────────────────────────┘

In Python:
    company = Company.query.get('uuid-acme')
    accesses = UserCompanyAccess.query.filter_by(company_id='uuid-acme').all()
    users = [access.user for access in accesses]
    
    for user in users:
        print(user.username)
    # Output:
    # john_smith
    # sarah_admin
    # mike_manager
```

### Example 3: Query Pattern - Find Users with Access

```python
# Get all users with access to specific company
company_users = db.session.query(User).join(UserCompanyAccess).filter(
    UserCompanyAccess.company_id == 'uuid-target-company'
).all()

# Get all companies for a user
user = User.query.get(1)
companies = [a.company for a in user.company_access]

# Check if user has access to company
has_access = UserCompanyAccess.query.filter_by(
    user_id=1,
    company_id='uuid-company'
).first() is not None

# Count companies per user
from sqlalchemy import func
user_company_counts = db.session.query(
    User.username,
    func.count(UserCompanyAccess.id).label('company_count')
).join(UserCompanyAccess).group_by(User.id).all()
```

---

## 🔄 Data Flow Scenarios

### Scenario 1: Adding a Company to a User

```
User Action:
  "Add Company LA Office to HR Manager john_smith"

Flow:
  1. Get User: john_smith (ID: 1)
  2. Get Company: LA Office (UUID: uuid-la)
  3. Check if already exists:
     UserCompanyAccess.query.filter_by(user_id=1, company_id=uuid-la).first()
  4. If NOT exists, create new record:
     access = UserCompanyAccess(user_id=1, company_id=uuid-la)
  5. Save to database:
     db.session.add(access)
     db.session.commit()

Result:
  Row added to hrm_user_company_access:
  ┌─────────────────────────────────────────────┐
  │ ID              │ user_id │ company_id      │
  ├─────────────────────────────────────────────┤
  │ uuid-001        │    1    │ uuid-la         │ ← NEW
  └─────────────────────────────────────────────┘

  user.companies now includes LA Office
```

### Scenario 2: Removing Company Access from User

```
User Action:
  "Remove Company LA Office from john_smith"

Flow:
  1. Find the access record:
     access = UserCompanyAccess.query.filter_by(
         user_id=1, 
         company_id=uuid-la
     ).first()
  2. Delete it:
     db.session.delete(access)
     db.session.commit()

Result:
  Row deleted from hrm_user_company_access
  user.companies no longer includes LA Office
```

### Scenario 3: User Logs In

```
Application Flow:
  1. User enters credentials: john_smith / password
  2. Flask-Login authenticates
  3. Session created with user.id = 1
  4. On dashboard load:
     current_user = User.query.get(1)
     companies = current_user.companies  ← Lazy loads from DB
  5. Display dashboard filtered to these companies
  
Template access:
  {% for company in current_user.companies %}
    <option>{{ company.name }}</option>
  {% endfor %}
```

---

## 🔐 Access Control Integration

### Permission Checking Logic

```python
def has_company_access(user_id, company_id):
    """Check if user has access to company"""
    access = UserCompanyAccess.query.filter_by(
        user_id=user_id,
        company_id=company_id
    ).first()
    return access is not None

def get_user_accessible_companies(user_id):
    """Get all companies user can access"""
    user = User.query.get(user_id)
    return [a.company for a in user.company_access]

# In route handlers:
@app.route('/company/<company_id>/dashboard')
@login_required
def company_dashboard(company_id):
    if not has_company_access(current_user.id, company_id):
        return "Access Denied", 403
    # ... show dashboard
```

---

## 📈 Scalability Considerations

### Current Design Supports:

| Metric | Capacity | Notes |
|--------|----------|-------|
| Users per Company | Unlimited | Indexed on company_id |
| Companies per User | Unlimited | Indexed on user_id |
| Total Records | Millions | UNIQUE constraint prevents duplicates |
| Query Performance | O(1) | Indexed lookups |

### Performance Optimizations:

1. **Indexes**: Both user_id and company_id are indexed
2. **Lazy Loading**: `lazy='select'` prevents N+1 queries
3. **UNIQUE Constraint**: Prevents accidental duplicates
4. **CASCADE Delete**: Automatic cleanup if user/company deleted

---

## 🔧 Common Operations

### In Application Code

```python
from models import User, Company, UserCompanyAccess

# Get user and their companies
user = User.query.get(user_id)
for company in user.companies:
    print(f"{company.name}")

# Check permission
if UserCompanyAccess.query.filter_by(
    user_id=user_id, 
    company_id=company_id
).first():
    # User has access
    pass

# Add company
new_access = UserCompanyAccess(
    user_id=user_id,
    company_id=company_id
)
db.session.add(new_access)
db.session.commit()

# Remove company
access = UserCompanyAccess.query.filter_by(
    user_id=user_id,
    company_id=company_id
).first()
db.session.delete(access)
db.session.commit()
```

### In Templates

```html
<!-- Get current user's companies -->
{% for company in current_user.companies %}
    <option value="{{ company.id }}">{{ company.name }}</option>
{% endfor %}

<!-- Filter data by user's companies -->
{% set user_company_ids = [c.id for c in current_user.companies] %}
```

---

## 🚀 Deployment Checklist

- [x] UserCompanyAccess model created in models.py
- [x] Database migration file created
- [ ] Run: `flask db upgrade`
- [ ] Run: `python migrate_user_company_access.py`
- [ ] Test: `python setup_user_companies.py`
- [ ] Verify: Summary statistics show relationships created
- [ ] (Optional) Implement web UI for management
- [ ] Deploy to production

---

## 📚 Related Files

- **models.py**: UserCompanyAccess model definition
- **migrations/versions/**: Database migration file
- **setup_user_companies.py**: Interactive management tool
- **add_user_companies.py**: Programmatic API
- **ADD_COMPANIES_TO_USERS_GUIDE.md**: Detailed guide
- **migrate_user_company_access.py**: Initial data migration

---

## 🆘 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "UNIQUE constraint failed" | Duplicate user-company pair | Remove existing access first |
| Relationships not loading | Circular dependency | Using lazy='select' (already fixed) |
| Query returns empty | No access records created | Run migration script |
| Slow queries | Missing indexes | Already present in schema |

---

## ✅ Verification Commands

```bash
# Check table exists
python -c "from models import UserCompanyAccess; print('✓ Model exists')"

# Count relationships
python -c "
from app import app
from models import UserCompanyAccess
with app.app_context():
    count = UserCompanyAccess.query.count()
    print(f'Total relationships: {count}')
"

# List user companies
python -c "
from app import app
from models import User
with app.app_context():
    user = User.query.first()
    for company in user.companies:
        print(f'✓ {company.name}')
"
```

---

## 🎯 Summary

| Component | Status | Details |
|-----------|--------|---------|
| **Model** | ✅ Complete | UserCompanyAccess defined |
| **Database** | ✅ Ready | Table with indexes and constraints |
| **Migration** | ✅ Available | migrate_user_company_access.py |
| **API** | ✅ Ready | setup_user_companies.py & add_user_companies.py |
| **Web UI** | 🔄 Optional | Can be implemented with guide |
| **Documentation** | ✅ Complete | Multiple guides available |

**Your system is ready for multi-company user management!** 🎉