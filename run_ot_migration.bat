@echo off
REM Force execute OT Daily Summary migration
echo.
echo ============================================
echo OT Daily Summary Migration
echo ============================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

echo Running migration...
echo.

python force_ot_migration.py

if errorlevel 1 (
    echo.
    echo ERROR: Migration failed!
    pause
    exit /b 1
) else (
    echo.
    echo SUCCESS: Migration completed!
    echo.
    echo Next steps:
    echo 1. Refresh your browser
    echo 2. Click on: OT Management ^> Payroll Summary (Grid)
    echo 3. The page should now work
    echo.
    pause
)