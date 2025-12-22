Database Cleanup & Re-seeding Feature
Implemented a development-only utility to clean HRM and core tables and re-seed them with essential master data.

Features Implemented
Database Cleanup Utility: 
core/dev_utils.py
 contains 
clean_database_hrm()
 which:
Checks if ENVIRONMENT is set to development.
Truncates targeted HRM and core tables (with CASCADE).
Re-seeds essential tables: 
Tenant
, 
Organization
, 
Role
, 
User
 (Superadmin), 
TenantConfiguration
, 
Department
, 
Designation
, 
WorkingHours
, and 
WorkSchedule
.
Initializes the Access Control Matrix (RBAC).
Dev Routes: 
routes/dev_routes.py
 provides the /dev/clean-db POST endpoint.
UI Integration: Added a "Clean Database (Dev Only)" button to the login page (
templates/auth/login.html
), visible only in development mode.
Security: Strict environment checks and confirmation prompts to prevent accidental data loss in production.
Technical Details
Multi-Table Truncation
The cleanup uses a single TRUNCATE TABLE ... RESTART IDENTITY CASCADE command for efficiency and to handle complex foreign key relationships. The SQLAlchemy session is cleared using db.session.expunge_all() after truncation to prevent stale object references.

Role Table Synchronization
A critical schema mismatch was identified where the database constraint for hrm_users.role_id points to the 
role
 table (lowercase), while the HRM module primarily uses hrm_roles. The utility now seeds both tables to ensure compatibility across different system components.

Standardized Roles
Role names have been standardized to match system-wide expectations:

Super Admin
Tenant Admin
HR Manager
Employee
Verified Data
Running the cleanup results in the following state:

Tenant: "Noltrion" (Code: NOL)
Organization: "Noltrion Invovation Pvt Ltd" (ID: 1)
Superadmin: superadmin@noltrion.com / Admin@123 (Role: Super Admin, ID: 1)
Master Data: Standard departments, designations, working hours, and work schedules initialized.
Access Control: Permissions matrix initialized for all roles.
Files Modified/Added
File	Status	Description
core/dev_utils.py
[NEW]	Core logic for cleanup and re-seeding.
routes/dev_routes.py
[NEW]	Blueprint routes for dev-only actions.
main.py
[MODIFY]	Registered dev_bp.
routes/routes.py
[MODIFY]	Pass ENVIRONMENT to login template.
templates/auth/login.html
[MODIFY]	Added conditional cleanup button.
UI Improvements
Fixed Horizontal Navbar
Implemented a fix to ensure the top horizontal navbar stays in a fixed position at the top of the viewport when scrolling.

Changed Position: Modifed .navbar from sticky to fixed.
Layout Adjustments: Updated .page-container padding-top to 
calc(var(--header-height) + 0.75rem)
 to prevent content from being hidden behind the fixed header while maintaining a consistent visual gap.
Cross-Device Consistency: Verified that the sidebar and mobile toggle continue to work seamlessly with the new fixed layout.
Bug Fixes
Resolved ModuleNotFoundError
Fixed an issue where the 
dashboard
 route would fail with ModuleNotFoundError: No module named 'routes_hr_manager' for HR Managers and Tenant Admins.

Root Cause: An incorrect relative import in 
routes/routes.py
 at line 384.
Resolution: Updated the import to use the correct absolute path: from routes.routes_hr_manager import hr_manager_dashboard.
Verification Results
The feature was verified by:

Checking the existence of the button on the login page in developmental mode.
Executing the cleanup and confirming successful redirection to login.
Inspecting the database to verify that hrm_users contains only the superadmin and that all master data tables are correctly populated.
Confirming that the login with superadmin@noltrion.com works after cleanup.