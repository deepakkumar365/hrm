# 📋 Add Multiple Companies to Users - Complete Guide

This guide explains how to assign multiple companies to users in your HRM system. The **UserCompanyAccess** table manages the many-to-many relationship between users and companies.

---

## 🗂️ Table Structure

```
hrm_user_company_access (Junction Table)
├── id (UUID, primary key)
├── user_id (foreign key → hrm_users.id)
├── company_id (foreign key → hrm_company.id)
├── created_at (timestamp)
└── modified_at (timestamp)
```

**Constraints:**
- Each user-company combination must be unique (`UNIQUE(user_id, company_id)`)
- Indexes on user_id and company_id for fast queries

---

## 🚀 Method 1: Python Script (Quick & Easy)

Create a file: `add_user_companies.py`

```python
#!/usr/bin/env python
"""
Script to add multiple companies to users
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Company, UserCompanyAccess

def add_company_to_user(user_id, company_id):
    """Add a single company to a user"""
    with app.app_context():
        try:
            # Check if user exists
            user = User.query.get(user_id)
            if not user:
                print(f"❌ User {user_id} not found")
                return False
            
            # Check if company exists
            company = Company.query.get(company_id)
            if not company:
                print(f"❌ Company {company_id} not found")
                return False
            
            # Check if access already exists
            existing = UserCompanyAccess.query.filter_by(
                user_id=user_id,
                company_id=company_id
            ).first()
            
            if existing:
                print(f"⚠️  User '{user.username}' already has access to '{company.name}'")
                return False
            
            # Add access
            access = UserCompanyAccess(
                user_id=user_id,
                company_id=company_id
            )
            db.session.add(access)
            db.session.commit()
            
            print(f"✅ Added '{company.name}' to user '{user.username}'")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")
            return False


def add_companies_to_user(user_id, company_ids):
    """Add multiple companies to a user at once"""
    with app.app_context():
        count = 0
        user = User.query.get(user_id)
        
        if not user:
            print(f"❌ User {user_id} not found")
            return 0
        
        print(f"🔄 Adding companies to user '{user.username}'...")
        
        for company_id in company_ids:
            company = Company.query.get(company_id)
            if not company:
                print(f"⚠️  Company {company_id} not found - skipping")
                continue
            
            # Check if access already exists
            existing = UserCompanyAccess.query.filter_by(
                user_id=user_id,
                company_id=company_id
            ).first()
            
            if existing:
                print(f"⊘ Already has access to '{company.name}'")
                continue
            
            try:
                access = UserCompanyAccess(
                    user_id=user_id,
                    company_id=company_id
                )
                db.session.add(access)
                count += 1
                print(f"✓ '{company.name}'")
            except Exception as e:
                print(f"✗ Error adding '{company.name}': {str(e)}")
        
        try:
            db.session.commit()
            print(f"✅ Successfully added {count} company(ies)")
            return count
        except Exception as e:
            db.session.rollback()
            print(f"❌ Commit failed: {str(e)}")
            return 0


def list_user_companies(user_id):
    """List all companies a user has access to"""
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            print(f"❌ User {user_id} not found")
            return
        
        print(f"\n📋 Companies for user '{user.username}':")
        print("-" * 60)
        
        if not user.company_access:
            print("No company access assigned")
            return
        
        for i, access in enumerate(user.company_access, 1):
            company = access.company
            print(f"{i}. {company.name} (ID: {company.id})")
            print(f"   Access granted: {access.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("-" * 60)
        print(f"Total: {len(user.company_access)} company(ies)")


def remove_company_from_user(user_id, company_id):
    """Remove a company from a user"""
    with app.app_context():
        try:
            access = UserCompanyAccess.query.filter_by(
                user_id=user_id,
                company_id=company_id
            ).first()
            
            if not access:
                print(f"⚠️  User {user_id} doesn't have access to company {company_id}")
                return False
            
            user = User.query.get(user_id)
            company = Company.query.get(company_id)
            
            db.session.delete(access)
            db.session.commit()
            
            print(f"✅ Removed access: '{user.username}' → '{company.name}'")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")
            return False


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    # Example 1: Add single company to a user
    # add_company_to_user(user_id=1, company_id='uuid-of-company')
    
    # Example 2: Add multiple companies to a user
    # company_ids = ['uuid-1', 'uuid-2', 'uuid-3']
    # add_companies_to_user(user_id=1, company_ids=company_ids)
    
    # Example 3: List all companies for a user
    # list_user_companies(user_id=1)
    
    # Example 4: Remove a company from a user
    # remove_company_from_user(user_id=1, company_id='uuid-of-company')
    
    print("📝 Edit this file with actual user and company IDs to run commands")
```

**Run examples:**
```bash
# First, find user and company IDs
python show_users.py          # List all users
python show_companies.py      # List all companies

# Then edit the script and uncomment the example you want to run
python add_user_companies.py
```

---

## 🎮 Method 2: Flask CLI Command

Add to your `cli_commands.py`:

```python
@app.cli.command('user-company')
@click.option('--action', type=click.Choice(['add', 'remove', 'list']), required=True)
@click.option('--user-id', type=int, help='User ID')
@click.option('--company-id', help='Company ID (UUID)')
def manage_user_companies(action, user_id, company_id):
    """Manage user company access"""
    from models import User, Company, UserCompanyAccess
    
    if action == 'add':
        if not user_id or not company_id:
            click.echo("❌ --user-id and --company-id are required")
            return
        
        user = User.query.get(user_id)
        company = Company.query.get(company_id)
        
        if not user:
            click.echo(f"❌ User {user_id} not found")
            return
        if not company:
            click.echo(f"❌ Company {company_id} not found")
            return
        
        existing = UserCompanyAccess.query.filter_by(
            user_id=user_id, company_id=company_id
        ).first()
        
        if existing:
            click.echo(f"⚠️  Already exists")
            return
        
        access = UserCompanyAccess(user_id=user_id, company_id=company_id)
        db.session.add(access)
        db.session.commit()
        click.echo(f"✅ Added '{company.name}' to user '{user.username}'")
    
    elif action == 'remove':
        if not user_id or not company_id:
            click.echo("❌ --user-id and --company-id are required")
            return
        
        access = UserCompanyAccess.query.filter_by(
            user_id=user_id, company_id=company_id
        ).first()
        
        if not access:
            click.echo(f"⚠️  Access not found")
            return
        
        db.session.delete(access)
        db.session.commit()
        click.echo(f"✅ Removed access")
    
    elif action == 'list':
        if not user_id:
            click.echo("❌ --user-id is required")
            return
        
        user = User.query.get(user_id)
        if not user:
            click.echo(f"❌ User {user_id} not found")
            return
        
        click.echo(f"\n📋 Companies for '{user.username}':")
        for access in user.company_access:
            click.echo(f"  • {access.company.name}")
```

**Usage:**
```bash
flask user-company --action add --user-id 1 --company-id "uuid"
flask user-company --action list --user-id 1
flask user-company --action remove --user-id 1 --company-id "uuid"
```

---

## 🎨 Method 3: Web UI (Create a User Management Page)

Create: `templates/access_control/manage_user_companies.html`

```html
{% extends "base.html" %}

{% block title %}Manage User Company Access{% endblock %}

{% block content %}
<div class="container mt-5">
    <h1>👥 Manage User Company Access</h1>
    <hr>
    
    <!-- User Selection -->
    <div class="card mb-4">
        <div class="card-header">
            <h5>Select User</h5>
        </div>
        <div class="card-body">
            <form id="userForm">
                <div class="mb-3">
                    <label for="userId" class="form-label">User</label>
                    <select class="form-select" id="userId" name="user_id" required onchange="loadUserCompanies()">
                        <option value="">-- Select User --</option>
                        {% for user in users %}
                        <option value="{{ user.id }}">{{ user.username }} ({{ user.role.name if user.role else 'No Role' }})</option>
                        {% endfor %}
                    </select>
                </div>
            </form>
        </div>
    </div>
    
    <!-- Current Companies -->
    <div class="card mb-4" id="currentCompaniesCard" style="display: none;">
        <div class="card-header">
            <h5>📋 Currently Assigned Companies</h5>
        </div>
        <div class="card-body">
            <ul id="currentCompaniesList" class="list-group">
            </ul>
        </div>
    </div>
    
    <!-- Add Companies -->
    <div class="card mb-4" id="addCompaniesCard" style="display: none;">
        <div class="card-header">
            <h5>➕ Add Companies</h5>
        </div>
        <div class="card-body">
            <form id="addCompanyForm">
                <div class="mb-3">
                    <label for="companyId" class="form-label">Available Companies</label>
                    <select class="form-select" id="companyId" name="company_id" required>
                        <option value="">-- Select Company --</option>
                        {% for company in companies %}
                        <option value="{{ company.id }}">{{ company.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <button type="button" class="btn btn-primary" onclick="addCompanyToUser()">Add Company</button>
            </form>
        </div>
    </div>
</div>

<script>
function loadUserCompanies() {
    const userId = document.getElementById('userId').value;
    
    if (!userId) {
        document.getElementById('currentCompaniesCard').style.display = 'none';
        document.getElementById('addCompaniesCard').style.display = 'none';
        return;
    }
    
    fetch(`/access-control/api/user-companies/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show current companies
                const list = document.getElementById('currentCompaniesList');
                list.innerHTML = '';
                
                if (data.companies.length === 0) {
                    list.innerHTML = '<li class="list-group-item">No companies assigned</li>';
                } else {
                    data.companies.forEach(company => {
                        const item = document.createElement('li');
                        item.className = 'list-group-item d-flex justify-content-between align-items-center';
                        item.innerHTML = `
                            ${company.name}
                            <button type="button" class="btn btn-sm btn-danger" 
                                    onclick="removeCompanyFromUser(${userId}, '${company.id}')">
                                Remove
                            </button>
                        `;
                        list.appendChild(item);
                    });
                }
                
                document.getElementById('currentCompaniesCard').style.display = 'block';
                document.getElementById('addCompaniesCard').style.display = 'block';
            }
        })
        .catch(error => console.error('Error:', error));
}

function addCompanyToUser() {
    const userId = document.getElementById('userId').value;
    const companyId = document.getElementById('companyId').value;
    
    if (!userId || !companyId) {
        alert('Please select both user and company');
        return;
    }
    
    fetch('/access-control/api/user-companies', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: parseInt(userId),
            company_id: companyId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Company added successfully');
            document.getElementById('companyId').value = '';
            loadUserCompanies();
        } else {
            alert('❌ Error: ' + data.error);
        }
    })
    .catch(error => {
        alert('Error: ' + error);
        console.error('Error:', error);
    });
}

function removeCompanyFromUser(userId, companyId) {
    if (!confirm('Are you sure?')) return;
    
    fetch('/access-control/api/user-companies', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: userId,
            company_id: companyId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Company removed successfully');
            loadUserCompanies();
        } else {
            alert('❌ Error: ' + data.error);
        }
    })
    .catch(error => {
        alert('Error: ' + error);
        console.error('Error:', error);
    });
}
</script>
{% endblock %}
```

Add these routes to `routes_access_control.py`:

```python
@access_control_bp.route('/api/user-companies/<int:user_id>', methods=['GET'])
@login_required
@require_role('Super Admin', 'Tenant Admin')
def get_user_companies(user_id):
    """Get all companies for a user"""
    from models import User
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    companies = [
        {
            'id': str(access.company.id),
            'name': access.company.name
        }
        for access in user.company_access
    ]
    
    return jsonify({'success': True, 'companies': companies})


@access_control_bp.route('/api/user-companies', methods=['POST'])
@login_required
@require_role('Super Admin', 'Tenant Admin')
def add_user_company():
    """Add a company to a user"""
    from models import User, Company, UserCompanyAccess
    
    data = request.get_json()
    user_id = data.get('user_id')
    company_id = data.get('company_id')
    
    user = User.query.get(user_id)
    company = Company.query.get(company_id)
    
    if not user or not company:
        return jsonify({'success': False, 'error': 'Invalid user or company'}), 400
    
    existing = UserCompanyAccess.query.filter_by(
        user_id=user_id,
        company_id=company_id
    ).first()
    
    if existing:
        return jsonify({'success': False, 'error': 'User already has access to this company'}), 400
    
    try:
        access = UserCompanyAccess(user_id=user_id, company_id=company_id)
        db.session.add(access)
        db.session.commit()
        
        log_audit('CREATE', 'UserCompanyAccess', str(access.id), 
                  f'Added {user.username} to {company.name}')
        
        return jsonify({'success': True, 'message': 'Company added successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@access_control_bp.route('/api/user-companies', methods=['DELETE'])
@login_required
@require_role('Super Admin', 'Tenant Admin')
def remove_user_company():
    """Remove a company from a user"""
    from models import User, Company, UserCompanyAccess
    
    data = request.get_json()
    user_id = data.get('user_id')
    company_id = data.get('company_id')
    
    access = UserCompanyAccess.query.filter_by(
        user_id=user_id,
        company_id=company_id
    ).first()
    
    if not access:
        return jsonify({'success': False, 'error': 'Access not found'}), 404
    
    try:
        user = User.query.get(user_id)
        company = Company.query.get(company_id)
        
        db.session.delete(access)
        db.session.commit()
        
        log_audit('DELETE', 'UserCompanyAccess', str(access.id), 
                  f'Removed {user.username} from {company.name}')
        
        return jsonify({'success': True, 'message': 'Company removed successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@access_control_bp.route('/manage-user-companies')
@login_required
@require_role('Super Admin', 'Tenant Admin')
def manage_user_companies():
    """User company management page"""
    from models import User, Company
    
    users = User.query.all()
    companies = Company.query.all()
    
    return render_template('access_control/manage_user_companies.html',
                          users=users, companies=companies)
```

---

## 📊 Database Queries

### Find all companies a user has access to:
```python
from models import User, UserCompanyAccess

user = User.query.get(user_id)
companies = [access.company for access in user.company_access]
```

### Find all users with access to a company:
```python
from models import Company, UserCompanyAccess

company = Company.query.get(company_id)
users = [access.user for access in UserCompanyAccess.query.filter_by(company_id=company_id)]
```

### Check if user has access to a company:
```python
from models import UserCompanyAccess

has_access = UserCompanyAccess.query.filter_by(
    user_id=user_id,
    company_id=company_id
).first() is not None
```

---

## ✅ Quick Start

1. **First, run the migration:**
   ```bash
   flask db upgrade
   ```

2. **Populate existing relationships:**
   ```bash
   python migrate_user_company_access.py
   ```

3. **Choose your method above and use it to add more companies**

---

## 🔍 Verification

```python
from app import app
from models import User, Company, UserCompanyAccess

with app.app_context():
    # Check total records
    total = UserCompanyAccess.query.count()
    print(f"Total user-company relationships: {total}")
    
    # Check specific user
    user = User.query.first()
    print(f"\nUser '{user.username}' has access to:")
    for access in user.company_access:
        print(f"  • {access.company.name}")
```

---

## 🆘 Troubleshooting

### Issue: "UNIQUE constraint failed"
**Solution:** The combination of user_id and company_id already exists. Remove it first then add again.

### Issue: "User not found"
**Solution:** Check that the user_id exists in the database. Run `python show_users.py`

### Issue: "Company not found"
**Solution:** Check that the company_id exists. Run `python show_companies.py`

### Issue: Changes not saved
**Solution:** Make sure you call `db.session.commit()` after making changes.

---

## 📝 Summary

| Method | Ease | Best For |
|--------|------|----------|
| Script | ⭐⭐⭐ | Bulk operations, automation |
| CLI | ⭐⭐ | Command-line users |
| Web UI | ⭐⭐⭐⭐ | Admin interface, end users |

**Recommended:** Start with **Method 1 (Script)** for quick testing, then implement **Method 3 (Web UI)** for production.