#!/bin/bash
# Daily Attendance Auto-Creation Task for Linux/Unix (Render)
# This script can be scheduled to run daily using cron

echo "========================================"
echo "Daily Attendance Auto-Creation Task"
echo "========================================"
echo "Starting at $(date)"
echo

# Change to the project directory (adjust path as needed for Render)
cd "$(dirname "$0")"

# Run the Python script
python daily_attendance_task.py

# Check if the script ran successfully
if [ $? -eq 0 ]; then
    echo
    echo "========================================"
    echo "Task completed successfully!"
    echo "========================================"
else
    echo
    echo "========================================"
    echo "Task failed with error code: $?"
    echo "========================================"
fi

echo
echo "Finished at $(date)"