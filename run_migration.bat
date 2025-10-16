@echo off
echo ============================================================
echo  ROLE TABLE MIGRATION SCRIPT
echo ============================================================
echo.
echo This will migrate 'role' table to 'hrm_roles'
echo.
pause
echo.
echo Running migration...
echo.

cd /d D:\Projects\HRMS\hrm
python run_migration_direct.py

echo.
echo ============================================================
echo  Migration script completed
echo ============================================================
echo.
pause