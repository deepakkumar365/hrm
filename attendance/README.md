# Attendance Management Module

This module provides comprehensive attendance management functionality for the HRM system.

## Files Structure

```
attendance/
├── daily.html          # Daily attendance management interface
├── monthly.html        # Monthly attendance reports and calendar view
├── overtime.html       # Overtime management and calculations
├── js/
│   ├── daily.js        # JavaScript for daily attendance functionality
│   ├── monthly.js      # JavaScript for monthly attendance functionality
│   └── overtime.js     # JavaScript for overtime management
└── README.md           # This file
```

## Features

### Daily Attendance Management (`daily.html`)
- **Date Selection**: Choose any date to manage attendance
- **Employee List**: View all employees with department and position details
- **Attendance Marking**: Mark employees as Present, Absent, Late, Half Day, or On Leave
- **Time Tracking**: Set time in/out for each employee
- **Quick Actions**: 
  - Mark all employees as present with one click
  - Save attendance data
  - Export attendance to CSV
- **Summary Dashboard**: Real-time counts of present, absent, and on leave employees
- **Notes System**: Add notes for individual employee attendance
- **Search & Filter**: Quickly find specific employees

### Monthly Attendance Reports (`monthly.html`)
- **Calendar View**: Visual calendar showing attendance for entire month
- **Color-coded Legend**: Easy identification of attendance status
  - Green (P) = Present
  - Red (A) = Absent
  - Yellow (L) = Late
  - Blue (H) = Half Day
  - Gray (LV) = Leave
  - Light Gray (W) = Weekend
  - Yellow (HO) = Holiday
- **Monthly Statistics**: Working days, total present/absent, average attendance
- **Employee Details**: Click employee names for detailed attendance view
- **Export Reports**: Generate CSV reports for the month
- **Department Filtering**: Filter by department or search employees

### Overtime Management (`overtime.html`)
- **OT Entry Management**: Add, edit, and delete overtime entries for employees
- **Automatic Calculations**: Calculate OT hours, rates, and amounts automatically
- **Flexible OT Rates**: Support for 1.5x, 2.0x, and custom multipliers
- **Approval Workflow**: Pending, approved, and rejected status management
- **Monthly Summary**: Real-time dashboard showing OT statistics
- **Payroll Integration**: Calculate total OT costs for payroll processing
- **Detailed Breakdown**: View complete payment calculations for each entry
- **Bulk Operations**: Approve all pending OT entries at once
- **Export Reports**: Generate CSV reports for accounting and payroll
- **Search & Filter**: Find specific employees or OT entries quickly

## Usage

### For HR Daily Operations:
1. Navigate to **Attendance → Daily**
2. Select the date (defaults to today)
3. Mark employees who are absent (others default to present)
4. Adjust time in/out as needed
5. Add notes for special circumstances
6. Click "Save Attendance" to store the data

### For Monthly Reviews:
1. Navigate to **Attendance → Monthly**
2. Select month and year
3. View color-coded attendance calendar
4. Click employee names for detailed view
5. Export reports for management

### For Overtime Management:
1. Navigate to **Attendance → Overtime**
2. Select month and year to view OT data
3. Click "Add OT Entry" to record overtime work
4. Fill in employee details, hours worked, and reason
5. System automatically calculates OT hours and payment
6. Approve or reject OT entries as needed
7. Use "Calculate Payroll" for monthly OT totals
8. Export reports for accounting and payroll processing

## Data Storage
- Uses browser localStorage for data persistence
- Each day's attendance is stored separately
- Data survives browser sessions
- Ready for backend integration

## Technical Details
- **Framework**: Vanilla JavaScript with Bootstrap 4
- **Storage**: localStorage (can be easily replaced with API calls)
- **Responsive**: Works on desktop and mobile devices
- **Export**: CSV format for reports

## Customization
- Holidays can be configured in the `holidays` array in `monthly.js`
- Working hours can be adjusted in the default time settings
- Additional attendance statuses can be added by modifying the dropdown options

## Future Enhancements
- Integration with employee database
- Automatic time tracking via biometric devices
- Email notifications for attendance issues
- Advanced reporting and analytics
- Mobile app integration