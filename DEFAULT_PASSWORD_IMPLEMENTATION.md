# Default Password Implementation

## Overview
This document describes the implementation of a default password system for all users in the HRMS application.

## Default Password
**Password:** `Noltrion@123`

This password is now used for:
1. All newly created default users (superadmin, admin, manager, user)
2. All employees created through the employee creation form
3. All users registered through the admin registration form
4. All password resets performed by administrators

## Files Modified

### 1. `constants.py` (NEW)
- Created a new constants file to store the default password
- This centralizes the password configuration in one place
- Location: `E:/Gobi/Pro/HRMS/hrm/constants.py`

```python
DEFAULT_USER_PASSWORD = "Noltrion@123"
```

### 2. `auth.py`
**Changes:**
- Imported `DEFAULT_USER_PASSWORD` from constants
- Updated `create_default_users()` function to use the default password for all default users:
  - superadmin
  - admin
  - manager
  - user

**Before:**
```python
super_admin.set_password('superadmin123')
admin.set_password('admin123')
manager.set_password('manager123')
user.set_password('user123')
```

**After:**
```python
super_admin.set_password(DEFAULT_USER_PASSWORD)
admin.set_password(DEFAULT_USER_PASSWORD)
manager.set_password(DEFAULT_USER_PASSWORD)
user.set_password(DEFAULT_USER_PASSWORD)
```

### 3. `routes.py`
**Changes:**
- Imported `DEFAULT_USER_PASSWORD` from constants
- Updated employee creation route (around line 747) to use the default password
- Set `must_reset_password = True` to force password change on first login

**Before:**
```python
temp_password = f"{employee.first_name}123"
user.set_password(temp_password)
```

**After:**
```python
user.set_password(DEFAULT_USER_PASSWORD)
user.must_reset_password = True
```

### 4. `routes_enhancements.py`
**Changes:**
- Imported `DEFAULT_USER_PASSWORD` from constants
- Updated `employee_reset_password()` function to use the default password

**Before:**
```python
temp_password = f"{employee.first_name}123"
user.set_password(temp_password)
```

**After:**
```python
user.set_password(DEFAULT_USER_PASSWORD)
```

### 5. `update_all_passwords.py` (NEW)
- Created a utility script to update all existing users with the default password
- Location: `E:/Gobi/Pro/HRMS/hrm/update_all_passwords.py`

## How to Update Existing Users

To update all existing users in the database with the default password, run:

```bash
python update_all_passwords.py
```

The script will:
1. Display the number of users found
2. Ask for confirmation before proceeding
3. Update all user passwords to `Noltrion@123`
4. Set `must_reset_password = False` (can be changed to `True` if needed)
5. Display a summary of updated users

## Usage Scenarios

### 1. New System Installation
When the system is first installed and default users are created, they will all have the password `Noltrion@123`.

### 2. Creating New Employees
When an admin creates a new employee through the employee form:
- A user account is automatically created
- The password is set to `Noltrion@123`
- The user must change their password on first login (`must_reset_password = True`)
- A success message displays the username and password

### 3. Password Reset by Admin
When an admin resets an employee's password:
- The password is reset to `Noltrion@123`
- The user must change their password on next login

### 4. Manual User Registration
When an admin manually registers a user through the registration form:
- The admin can still set a custom password through the form
- Or the default password can be used

## Security Considerations

1. **Password Complexity:** The default password `Noltrion@123` meets common password requirements:
   - Contains uppercase letters
   - Contains lowercase letters
   - Contains numbers
   - Contains special characters (@)
   - Length: 13 characters

2. **Force Password Change:** For new employees, `must_reset_password` is set to `True`, forcing them to change the password on first login.

3. **Centralized Management:** The password is defined in one place (`constants.py`), making it easy to update if needed.

## Future Enhancements

Consider implementing:
1. Password expiration policy
2. Password history to prevent reuse
3. Account lockout after failed login attempts
4. Two-factor authentication
5. Password strength meter on password change forms

## Testing

After implementation, test the following scenarios:

1. ✅ Create a new employee and verify the password is `Noltrion@123`
2. ✅ Reset an existing employee's password and verify it's set to `Noltrion@123`
3. ✅ Run the `update_all_passwords.py` script to update existing users
4. ✅ Login with the default password
5. ✅ Verify `must_reset_password` flag works correctly

## Rollback

If you need to rollback these changes:
1. Remove the import of `DEFAULT_USER_PASSWORD` from all files
2. Restore the original password generation logic
3. Delete `constants.py` and `update_all_passwords.py`

## Support

For questions or issues related to this implementation, contact the development team.

---
**Implementation Date:** 2024
**Version:** 1.0