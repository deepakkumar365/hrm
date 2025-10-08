# 👥 User Credentials Summary - Flask HRMS

## 📊 Database: hrm_users Table

### Current Users (4 accounts)

```
┌────┬──────────────┬─────────────────────┬──────────────┬─────────────────┬────────┐
│ ID │ Username     │ Email               │ Role         │ Organization ID │ Active │
├────┼──────────────┼─────────────────────┼──────────────┼─────────────────┼────────┤
│ 1  │ superadmin   │ superadmin@hrm.com  │ SUPER_ADMIN  │ 2               │ ✅ Yes │
│ 2  │ admin        │ admin@hrm.com       │ ADMIN        │ 2               │ ✅ Yes │
│ 3  │ manager      │ manager@hrm.com     │ HR_MANAGER   │ 2               │ ✅ Yes │
│ 4  │ user         │ user@hrm.com        │ EMPLOYEE     │ 2               │ ✅ Yes │
└────┴──────────────┴─────────────────────┴──────────────┴─────────────────┴────────┘
```

---

## 🔑 Login Credentials

### All Users (Default Password)

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `superadmin` | `admin123` | SUPER_ADMIN | Full system access |
| `admin` | `admin123` | ADMIN | Administrative access |
| `manager` | `admin123` | HR_MANAGER | HR management access |
| `user` | `admin123` | EMPLOYEE | Basic employee access |

⚠️ **SECURITY WARNING:** All users currently have the same password: `admin123`

---

## 🔐 Password Encryption Details

### Hashing Algorithm: **Scrypt**

**Library:** `werkzeug.security` (Flask/Python)

**Hash Format:**
```
scrypt:32768:8:1$<salt>$<hash>
```

**Parameters:**
- **Algorithm:** Scrypt (memory-hard, ASIC-resistant)
- **Cost Factor (N):** 32,768
- **Block Size (r):** 8
- **Parallelization (p):** 1
- **Salt:** 16 random characters (unique per password)
- **Total Hash Length:** 162 characters

### Example Password Hash

**Plain Password:** `admin123`

**Stored Hash:**
```
scrypt:32768:8:1$huIN2EgLH8BRvd9k$29f6cf3fed6ddf9d522b2ac400085fb829d178165c94aa...
```

**Breakdown:**
```
scrypt           → Algorithm name
32768            → Cost factor (computational difficulty)
8                → Block size (memory requirement)
1                → Parallelization factor
huIN2EgLH8BRvd9k → Random salt (prevents rainbow tables)
29f6cf3f...      → Actual password hash (128 characters)
```

---

## 🛡️ Security Features

### 1. **One-Way Hashing**
- ✅ Passwords cannot be decrypted
- ✅ Only verification is possible
- ✅ Even database admins cannot see actual passwords

### 2. **Unique Salts**
- ✅ Each password gets a unique random salt
- ✅ Prevents rainbow table attacks
- ✅ Same password = different hashes for different users

### 3. **Memory-Hard Algorithm**
- ✅ Scrypt requires significant RAM
- ✅ Makes brute-force attacks expensive
- ✅ Resistant to GPU/ASIC attacks

### 4. **Timing-Safe Comparison**
- ✅ Prevents timing attacks
- ✅ Constant-time password verification

---

## 💻 How Passwords Are Handled

### Setting a Password (Code)

```python
from models import User

# Create user
user = User(username='john', email='john@example.com')

# Set password (automatically hashed)
user.set_password('mySecurePassword123!')

# Password is now stored as:
# scrypt:32768:8:1$randomSalt$hashedValue...
```

### Verifying a Password (Code)

```python
from models import User

# Get user
user = User.query.filter_by(username='john').first()

# Check password
if user.check_password('mySecurePassword123!'):
    print("✅ Login successful!")
else:
    print("❌ Invalid password!")
```

### Implementation (models.py)

```python
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    password_hash = db.Column(db.String(256), nullable=False)
    
    def set_password(self, password):
        """Hash password using Scrypt"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
```

---

## 🔧 Managing Passwords

### Reset All Default Passwords

```bash
python reset_default_passwords.py
```

**Output:**
```
🔐 Resetting Default User Passwords...
✅ Reset password for: superadmin (superadmin@hrm.com)
✅ Reset password for: admin (admin@hrm.com)
✅ Reset password for: manager (manager@hrm.com)
✅ Reset password for: user (user@hrm.com)
✅ Successfully reset 4 passwords
```

### Change Individual Password

```python
from app import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(username='superadmin').first()
    user.set_password('NewSecurePassword123!')
    db.session.commit()
    print(f"✅ Password changed for {user.username}")
```

### View Users (Without Passwords)

```bash
python show_users.py
```

---

## 🚨 Security Recommendations

### ⚠️ CRITICAL - Before Production

1. **Change All Default Passwords**
   ```bash
   python reset_default_passwords.py
   # Then manually change each password to unique, strong passwords
   ```

2. **Use Strong Passwords**
   - Minimum 12 characters
   - Mix of uppercase, lowercase, numbers, special characters
   - No dictionary words
   - No personal information

3. **Implement Password Policy**
   - Force password change on first login
   - Regular password expiry (e.g., 90 days)
   - Password history (prevent reuse)
   - Minimum complexity requirements

4. **Add Security Features**
   - Account lockout after failed attempts
   - Two-factor authentication (2FA)
   - Password reset via email
   - Security questions (optional)
   - CAPTCHA after 3 failed attempts

5. **Enable Logging**
   - Log all login attempts
   - Log password changes
   - Monitor for suspicious activity
   - Alert on multiple failed logins

---

## 📋 Password Strength Guide

### ❌ Weak Passwords (Never Use)
```
admin123          → Too simple, commonly used
password          → Dictionary word
12345678          → Sequential numbers
qwerty            → Keyboard pattern
admin             → Too short, predictable
```

### ✅ Strong Passwords (Recommended)
```
Tr0ub4dor&3!                    → 12 chars, mixed case, numbers, symbols
MyC0mpl3x&P@ssw0rd!2024        → 23 chars, very strong
correct-horse-battery-staple    → 28 chars, memorable passphrase
P@ssw0rd!Secure#2024           → 20 chars, strong
```

### Password Strength Checker

```python
def check_password_strength(password):
    """Check if password meets security requirements"""
    issues = []
    
    if len(password) < 12:
        issues.append("Too short (minimum 12 characters)")
    
    if not any(c.isupper() for c in password):
        issues.append("Missing uppercase letter")
    
    if not any(c.islower() for c in password):
        issues.append("Missing lowercase letter")
    
    if not any(c.isdigit() for c in password):
        issues.append("Missing number")
    
    if not any(c in '!@#$%^&*(),.?":{}|<>' for c in password):
        issues.append("Missing special character")
    
    if issues:
        return False, issues
    return True, ["Password is strong!"]

# Test
is_strong, messages = check_password_strength('admin123')
print(messages)
# Output: ['Too short (minimum 12 characters)', 'Missing uppercase letter', ...]
```

---

## 🎯 Quick Access Guide

### Login to Application

**URL:** `http://localhost:5000` (development)

**Credentials:**
```
Username: superadmin
Password: admin123
```

### Test Login

```bash
# Start application
python app.py

# Open browser
http://localhost:5000

# Login with:
Username: superadmin
Password: admin123
```

### Verify Password Works

```bash
python -c "
from app import app
from models import User

with app.app_context():
    user = User.query.filter_by(username='superadmin').first()
    if user.check_password('admin123'):
        print('✅ Password verified!')
    else:
        print('❌ Password incorrect!')
"
```

---

## 📚 Related Documentation

- **PASSWORD_SECURITY_INFO.md** - Detailed security information
- **QUICK_START.md** - Application quick start guide
- **ISSUE_RESOLUTION_SUMMARY.md** - Complete issue resolution details
- **show_users.py** - Script to display all users
- **reset_default_passwords.py** - Script to reset passwords

---

## 🔍 Database Schema

### hrm_users Table Structure

```sql
CREATE TABLE hrm_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(120) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,  -- Stores Scrypt hash
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    must_reset_password BOOLEAN DEFAULT TRUE,
    organization_id INTEGER REFERENCES organization(id),
    role_id INTEGER REFERENCES role(id),
    reporting_manager_id INTEGER REFERENCES hrm_users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## ✅ Summary

### Current State
- ✅ 4 users created
- ✅ All passwords hashed with Scrypt
- ✅ All users active
- ✅ Default password: `admin123`
- ⚠️ **Must change passwords for production!**

### Encryption Method
- **Algorithm:** Scrypt (industry-standard)
- **Security Level:** High
- **Hash Length:** 162 characters
- **Reversible:** No (one-way hash)
- **Salted:** Yes (unique salt per password)

### Next Steps
1. Change all default passwords
2. Implement password policy
3. Add 2FA (optional)
4. Enable account lockout
5. Set up password reset flow

---

**Last Updated:** 2024  
**Total Users:** 4  
**Default Password:** admin123 (⚠️ CHANGE IN PRODUCTION!)  
**Hash Algorithm:** Scrypt (Werkzeug)  
**Security Status:** ⚠️ Requires password changes for production use