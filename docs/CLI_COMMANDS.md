# HRMS CLI Commands Documentation

This document describes the Flask CLI commands available for managing the HRMS database.

## Available Commands

### 1. Reset Users (`reset-users`)

**Purpose**: Delete all existing users and create 4 new default users with predefined credentials.

**⚠️ WARNING**: This command will DELETE ALL USERS from the database!

**Usage**:
```powershell
flask reset-users --confirm
```

**What it does**:
1. Deletes all existing users from the `hrm_users` table
2. Ensures required roles exist (Super Admin, Admin, Manager, User)
3. Ensures a default organization exists
4. Creates 4 new users with the following credentials:

| Username      | Password         | Role        | Email                  |
|---------------|------------------|-------------|------------------------|
| superadmin    | superadmin123    | Super Admin | superadmin@hrm.com     |
| tenantadmin   | tenantadmin123   | Admin       | tenantadmin@hrm.com    |
| manager       | manager123       | Manager     | manager@hrm.com        |
| employee      | employee123      | User        | employee@hrm.com       |

**Example Output**:
```
🔄 Starting user reset process...
📋 Step 1: Deleting all existing users...
✅ Deleted 10 users
📋 Step 2: Checking required roles...
  ✓ Role exists: Super Admin
  ✓ Role exists: Admin
  ✓ Role exists: Manager
  ✓ Role exists: User
📋 Step 3: Checking default organization...
  ✓ Organization exists: Default Organization
📋 Step 4: Creating 4 new users...
  ➕ Created user: superadmin (Role: Super Admin)
  ➕ Created user: tenantadmin (Role: Admin)
  ➕ Created user: manager (Role: Manager)
  ➕ Created user: employee (Role: User)

============================================================
✅ USER RESET COMPLETED SUCCESSFULLY!
============================================================
```

---

### 2. List Users (`list-users`)

**Purpose**: Display all users in the system with their details.

**Usage**:
```powershell
flask list-users
```

**What it shows**:
- User ID
- Username
- Full Name
- Email
- Role
- Organization
- Status (Active/Inactive)
- Created Date

**Example Output**:
```
👥 Total Users: 4
================================================================================

ID: 1
  Username:     superadmin
  Name:         Super Admin
  Email:        superadmin@hrm.com
  Role:         Super Admin
  Organization: Default Organization
  Status:       ✅ Active
  Created:      2024-01-15 10:30:00
--------------------------------------------------------------------------------
```

---

### 3. Create User (`create-user`)

**Purpose**: Interactively create a new user.

**Usage**:
```powershell
flask create-user
```

**Interactive Prompts**:
- Username
- Password (hidden input with confirmation)
- Email
- First Name
- Last Name
- Role (Super Admin/Admin/Manager/User)

**Example Session**:
```
Username: johndoe
Password: ********
Repeat for confirmation: ********
Email: john.doe@company.com
First Name: John
Last Name: Doe
Role (Super Admin/Admin/Manager/User) [User]: Manager

✅ User created successfully!
  Username: johndoe
  Email:    john.doe@company.com
  Role:     Manager
```

**Options** (non-interactive mode):
```powershell
flask create-user --username johndoe --password secret123 --email john@company.com --first-name John --last-name Doe --role Manager
```

---

## Prerequisites

Before running any CLI commands, ensure:

1. **Virtual Environment is Activated** (if using one):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Environment Variables are Set**:
   - Ensure `.env` file exists with proper database configuration
   - `FLASK_APP` should point to `main.py` (or set it):
     ```powershell
     $env:FLASK_APP = "main.py"
     ```

3. **Database is Initialized**:
   ```powershell
   flask db upgrade
   ```

---

## Common Use Cases

### Scenario 1: Fresh Start with Default Users

If you want to start fresh with only the 4 default users:

```powershell
# Reset users
flask reset-users --confirm

# Verify users were created
flask list-users

# Login with any of the default credentials
# Example: username=superadmin, password=superadmin123
```

---

### Scenario 2: Check Current Users

To see who has access to the system:

```powershell
flask list-users
```

---

### Scenario 3: Add a New User

To add a new user without deleting existing ones:

```powershell
flask create-user
# Follow the interactive prompts
```

---

## Troubleshooting

### Error: "No module named 'cli_commands'"

**Solution**: Ensure `cli_commands.py` is imported in `main.py`:
```python
import cli_commands  # noqa: F401
```

---

### Error: "Could not locate a Flask application"

**Solution**: Set the FLASK_APP environment variable:
```powershell
$env:FLASK_APP = "main.py"
```

---

### Error: "Role 'X' not found"

**Solution**: The required roles don't exist. Run `reset-users` first to create them:
```powershell
flask reset-users --confirm
```

---

### Error: "No organization found"

**Solution**: Create a default organization first or run `reset-users`:
```powershell
flask reset-users --confirm
```

---

## Security Notes

1. **Default Passwords**: The default users created by `reset-users` have simple passwords for development/testing. **Change these in production!**

2. **Password Reset**: By default, `must_reset_password` is set to `False` for easy testing. In production, consider setting this to `True`.

3. **Confirmation Required**: The `reset-users` command requires the `--confirm` flag to prevent accidental data loss.

4. **Backup First**: Always backup your database before running `reset-users` in any environment with important data.

---

## Development vs Production

### Development
```powershell
# It's safe to use reset-users frequently
flask reset-users --confirm
```

### Production
```powershell
# ⚠️ NEVER run reset-users in production without a backup!
# Instead, use create-user to add individual users:
flask create-user
```

---

## Integration with Application Startup

The CLI commands are automatically registered when the application starts because `cli_commands.py` is imported in `main.py`. No additional configuration is needed.

---

## Future Enhancements

Potential additions to the CLI commands:

- `flask reset-password <username>` - Reset a specific user's password
- `flask deactivate-user <username>` - Deactivate a user account
- `flask activate-user <username>` - Reactivate a user account
- `flask change-role <username> <new-role>` - Change a user's role
- `flask export-users` - Export users to CSV
- `flask import-users <csv-file>` - Import users from CSV

---

## Support

For issues or questions about CLI commands, please refer to the main HRMS documentation or contact the development team.