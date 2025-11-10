@echo off
cd /d "D:\Projects\HRMS\hrm"
python -m flask db upgrade
pause