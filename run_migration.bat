@echo off
REM ==================================================
REM Migration Runner - Fixed Migration Chain
REM ==================================================

echo.
echo Running Database Migrations...
echo.

cd /d "D:\Projects\HRMS\hrm"

REM Run Flask migration command
python -m flask db upgrade

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ SUCCESS! Migration completed successfully
    echo.
    echo Next steps:
    echo 1. Start the Flask application: python main.py
    echo 2. Navigate to Masters menu
    echo 3. Check for Employee Groups and Leave Allocation options
    echo 4. Verify database tables were created
    echo.
) else (
    echo.
    echo ✗ ERROR! Migration failed
    echo Please check the error messages above
    echo.
)

pause