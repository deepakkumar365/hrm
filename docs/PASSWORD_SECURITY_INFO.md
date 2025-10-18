# 🔐 Password Security Information - Flask HRMS

## 📊 Current Users in Database

### User Accounts (4 total)

| ID | Username | Email | Role ID | Organization ID | Active | Must Reset |
|----|----------|-------|---------|-----------------|--------|------------|
| 1 | `superadmin` | superadmin@hrm.com | 1 (SUPER_ADMIN) | 2 | ✅ Yes | ❌ No |
| 2 | `admin` | admin@hrm.com | 2 (ADMIN) | 2 | ✅ Yes | ❌ No |
| 3 | `manager` | manager@hrm.com | 3 (HR_MANAGER) | 2 | ✅ Yes | ❌ No |
| 4 | `user` | user@hrm.com | 4 (EMPLOYEE) | 2 | ✅ Yes | ❌ No |

### Default Passwords

**All users have the same default password:** `admin123`

⚠️ **CRITICAL SECURITY WARNING:**
- These are default development passwords
- **MUST be changed immediately in production**
- Never use these passwords in a production environment
- Change passwords on first login

---

## 🔒 Password Hashing Method

### Technology Used

**Library:** `werkzeug.security` (part of Flask ecosystem)

**Algorithm:** **Scrypt** (as of Werkzeug 2.3+)
- Previously used PBKDF2-SHA256
- Scrypt is more secure and resistant to hardware attacks

### Hash Format

```
scrypt:32768:8:1$<salt>$<hash>
```

**Components:**
- `scrypt` - Algorithm name
- `32768` - Cost factor (N parameter)
- `8` - Block size (r parameter)
- `1` - Parallelization (p parameter)
- `<salt>` - Random salt (16 characters)
- `<hash>` - Actual password hash (128 characters)

**Total hash length:** 162 characters

### Example Hash

```
scrypt:32768:8:1$huIN2EgLH8BRvd9k$29f6cf3fed6ddf9d522b2ac400085fb829d178165c94aa...
```

---

## 💻 Implementation Details

### Code Location: `models.py`

```python
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    # ... other fields ...
    password_hash = db.Column(db.String(256), nullable=False)
    
    def set_password(self, password):
        """Hash and store password securely"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)
```

### How It Works

#### 1. **Setting a Password** (`set_password()`)
```python
user = User(username='john')
user.set_password('mypassword123')
# Stores: scrypt:32768:8:1$randomsalt$hashedpassword...
```

#### 2. **Checking a Password** (`check_password()`)
```python
if user.check_password('mypassword123'):
    print("Password correct!")
else:
    print("Password incorrect!")
```

---

## 🛡️ Security Features

### 1. **Scrypt Algorithm**
- **Memory-hard:** Requires significant RAM, making brute-force attacks expensive
- **ASIC-resistant:** Difficult to create specialized hardware for cracking
- **Tunable parameters:** Can adjust difficulty as hardware improves

### 2. **Automatic Salting**
- Each password gets a unique random salt
- Prevents rainbow table attacks
- Salt is stored with the hash (safe practice)

### 3. **One-Way Hashing**
- Impossible to reverse the hash to get the original password
- Even database administrators cannot see actual passwords
- Only verification is possible, not decryption

### 4. **Timing-Safe Comparison**
- `check_password_hash()` uses constant-time comparison
- Prevents timing attacks

---

## 📋 Password Security Best Practices

### ✅ What We're Doing Right

1. ✅ Using industry-standard hashing (Scrypt)
2. ✅ Automatic salting for each password
3. ✅ Never storing plain-text passwords
4. ✅ Using secure comparison functions
5. ✅ Storing hashes in appropriate length field (256 chars)

### ⚠️ What You Should Do

1. **Change Default Passwords Immediately**
   ```bash
   python reset_default_passwords.py
   # Then manually change to strong passwords
   ```

2. **Implement Password Policy**
   - Minimum 8 characters
   - Require uppercase, lowercase, numbers, special chars
   - Prevent common passwords
   - Force password expiry (optional)

3. **Enable Password Reset Flow**
   - Implement "Forgot Password" functionality
   - Use secure tokens for reset links
   - Set token expiration (e.g., 1 hour)

4. **Add Account Lockout**
   - Lock account after N failed login attempts
   - Implement CAPTCHA after 3 failed attempts
   - Log all failed login attempts

5. **Enable Two-Factor Authentication (2FA)**
   - Add TOTP support (Google Authenticator)
   - SMS verification (optional)
   - Backup codes for recovery

---

## 🔧 Useful Commands

### Reset All Default Passwords
```bash
python reset_default_passwords.py
```

### Show Current Users
```bash
python show_users.py
```

### Change Password Programmatically
```python
from app import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(username='superadmin').first()
    user.set_password('new_secure_password_123!')
    db.session.commit()
    print(f"Password changed for {user.username}")
```

### Verify Password
```python
from app import app
from models import User

with app.app_context():
    user = User.query.filter_by(username='superadmin').first()
    if user.check_password('admin123'):
        print("Password is correct!")
    else:
        print("Password is incorrect!")
```

---

## 🚨 Security Warnings

### ⚠️ NEVER DO THIS:

1. ❌ Store passwords in plain text
2. ❌ Use weak hashing (MD5, SHA1)
3. ❌ Share passwords via email or chat
4. ❌ Hardcode passwords in source code
5. ❌ Use the same password for multiple accounts
6. ❌ Log passwords (even in debug mode)
7. ❌ Display passwords in error messages

### ✅ ALWAYS DO THIS:

1. ✅ Use strong, unique passwords
2. ✅ Change default passwords immediately
3. ✅ Use environment variables for secrets
4. ✅ Enable HTTPS in production
5. ✅ Implement rate limiting on login
6. ✅ Log authentication attempts
7. ✅ Regular security audits

---

## 📊 Password Strength Recommendations

### Weak Passwords (❌ Don't Use)
```
admin123
password
12345678
qwerty
admin
```

### Strong Passwords (✅ Use These)
```
Tr0ub4dor&3!
correct-horse-battery-staple
P@ssw0rd!2024#Secure
MyC0mpl3x&P@ssw0rd!
```

### Password Requirements (Recommended)
- **Minimum length:** 12 characters
- **Uppercase letters:** At least 1
- **Lowercase letters:** At least 1
- **Numbers:** At least 1
- **Special characters:** At least 1 (!@#$%^&*)
- **No common words:** Avoid dictionary words
- **No personal info:** No names, birthdays, etc.

---

## 🔍 Checking Password Strength

### Add Password Validation (Recommended)

```python
import re

def validate_password_strength(password):
    """Validate password meets security requirements"""
    if len(password) < 12:
        return False, "Password must be at least 12 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain special character"
    
    return True, "Password is strong"

# Usage
is_valid, message = validate_password_strength('admin123')
print(message)  # "Password must be at least 12 characters"
```

---

## 📚 Additional Resources

### Werkzeug Security Documentation
- https://werkzeug.palletsprojects.com/en/latest/utils/#module-werkzeug.security

### Password Security Best Practices
- OWASP Password Storage Cheat Sheet
- NIST Digital Identity Guidelines
- CWE-259: Use of Hard-coded Password

### Scrypt Algorithm
- RFC 7914: The scrypt Password-Based Key Derivation Function
- https://en.wikipedia.org/wiki/Scrypt

---

## 🎯 Action Items for Production

### Before Deployment Checklist

- [ ] Change all default passwords
- [ ] Implement password strength validation
- [ ] Add password reset functionality
- [ ] Enable account lockout after failed attempts
- [ ] Implement rate limiting on login endpoint
- [ ] Add logging for authentication events
- [ ] Enable HTTPS/SSL
- [ ] Set secure session cookies
- [ ] Implement CSRF protection
- [ ] Add 2FA support (optional but recommended)
- [ ] Regular security audits
- [ ] Password expiry policy (optional)

---

## 📞 Quick Reference

### Current Hash Details
```
Algorithm: Scrypt
Cost Factor: 32768
Block Size: 8
Parallelization: 1
Salt Length: 16 characters
Hash Length: 162 characters total
Security Level: High (Industry Standard)
```

### Default Credentials (Development Only)
```
Username: superadmin
Password: admin123
⚠️  CHANGE IN PRODUCTION!
```

---

**Last Updated:** 2024  
**Security Level:** High (with proper password management)  
**Status:** ⚠️ Default passwords need to be changed for production