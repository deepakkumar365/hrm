@echo off
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║     Applying Database Schema Fix: currency_code Column         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

cd /d "D:\Projects\HRMS\hrm"

REM Run the fix script
python fix_currency_column.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ╔════════════════════════════════════════════════════════════════╗
    echo ║                    ✅ FIX APPLIED SUCCESSFULLY                 ║
    echo ║                                                                ║
    echo ║   You can now access the Companies Master as Tenant Admin!     ║
    echo ╚════════════════════════════════════════════════════════════════╝
    echo.
    pause
) else (
    echo.
    echo ❌ Fix failed. Please check the error above.
    echo.
    pause
)