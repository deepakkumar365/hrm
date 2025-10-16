@echo off
echo ============================================================
echo  DESIGNATION AND ROLE ENHANCEMENT MIGRATION SCRIPT
echo ============================================================
echo.
echo This will:
echo  - Create hrm_designations table
echo  - Create hrm_employee_companies association table
echo  - Create hrm_user_roles association table
echo  - Migrate existing position data to designations
echo  - Migrate existing company and role relationships
echo.
pause
echo.
echo Running migration...
echo.

cd /d D:\Projects\HRMS\hrm
python run_designation_migration.py

echo.
echo ============================================================
echo  Migration script completed
echo ============================================================
echo.
pause