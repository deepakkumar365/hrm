@echo off
REM Daily Attendance Auto-Creation Task for Windows
REM This batch file can be scheduled to run daily using Windows Task Scheduler

echo ========================================
echo Daily Attendance Auto-Creation Task
echo ========================================
echo Starting at %date% %time%
echo.

REM Change to the project directory
cd /d "E:\Gobi\Pro\HRMS\hrm"

REM Run the Python script
python daily_attendance_task.py

REM Check if the script ran successfully
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Task completed successfully!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Task failed with error code: %errorlevel%
    echo ========================================
)

echo.
echo Finished at %date% %time%

REM Uncomment the line below if you want to keep the window open for debugging
REM pause