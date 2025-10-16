@echo off
echo ============================================================
echo  ROLES TABLE ANALYSIS SCRIPT
echo ============================================================
echo.
echo This will analyze both public.roles and public.hrm_roles tables
echo.
pause
echo.
echo Running analysis...
echo.

cd /d D:\Projects\HRMS\hrm
python analyze_roles_simple.py

echo.
echo ============================================================
echo  Analysis completed
echo ============================================================
echo.
pause