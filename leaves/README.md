# Leave Management Module

This module provides comprehensive leave management functionality for the HRM system, including leave requests and balance management.

## Files Structure

```
leaves/
├── requests.html       # Leave requests management interface
├── balances.html       # Leave balances management interface
├── js/
│   ├── requests.js     # JavaScript for leave requests functionality
│   └── balances.js     # JavaScript for leave balances functionality
└── README.md           # This file
```

## Features

### Leave Requests Management (`requests.html`)
- **Request Creation**: Submit new leave requests with detailed information
- **Approval Workflow**: Pending → Approved → Rejected status management
- **Request Types**: Support for multiple leave types (Annual, Sick, Personal, Maternity, Emergency)
- **Balance Integration**: Real-time balance checking during request creation
- **Bulk Operations**: Approve or reject multiple requests at once
- **Search & Filter**: Find requests by employee, status, or leave type
- **Export Reports**: Generate CSV reports for management and HR
- **Email Reminders**: Send notifications for pending requests
- **Work Handover**: Assign work responsibilities during leave
- **Emergency Contacts**: Record emergency contact information

#### Request Features:
- **Automatic Calculations**: Calculate total leave days automatically
- **Balance Validation**: Check available balance before approval
- **Reason Tracking**: Record detailed reasons for leave requests
- **Status History**: Track approval/rejection history with timestamps
- **Document Management**: Ready for file attachment integration

### Leave Balances Management (`balances.html`)
- **Employee Balance Overview**: Visual cards showing all employees' leave balances
- **Leave Type Management**: Configure different types of leave with rules
- **Balance Adjustments**: Add, subtract, or set specific balance amounts
- **Bulk Updates**: Update multiple employees' balances simultaneously
- **Carry Forward**: Handle year-end balance carry forwards
- **Usage Analytics**: Track leave utilization across departments
- **Export Reports**: Generate comprehensive balance reports
- **Audit Trail**: Complete history of all balance adjustments

#### Balance Features:
- **Visual Progress Bars**: See leave usage at a glance
- **Department Filtering**: View balances by department
- **Year Selection**: Manage balances for different years
- **Automatic Allocation**: Set default allocations for new employees
- **Adjustment Tracking**: Record reasons for all balance changes

## Usage

### For HR - Managing Leave Requests:
1. Navigate to **Leaves → Requests**
2. View pending requests in the summary dashboard
3. Click "View" to see detailed request information
4. Approve or reject requests with reasons
5. Use bulk operations for multiple requests
6. Export reports for management review

### For HR - Managing Leave Balances:
1. Navigate to **Leaves → Balances**
2. Select year and department filters
3. View employee balance cards with visual indicators
4. Click "View Details" for comprehensive employee information
5. Use "Adjust Balance" for individual corrections
6. Use "Bulk Update" for department-wide changes

### For Employees - Submitting Requests:
1. Navigate to **Leaves → Requests**
2. Click "New Request" button
3. Fill in leave details and dates
4. System shows available balance automatically
5. Add emergency contact and work handover information
6. Submit for approval

## Leave Types Configuration

The system supports configurable leave types with the following properties:
- **Annual Leave**: 20 days default, 5 days carry forward
- **Sick Leave**: 10 days default, 2 days carry forward
- **Personal Leave**: 5 days default, no carry forward
- **Maternity Leave**: 90 days default, no carry forward
- **Emergency Leave**: 3 days default, no carry forward

Each leave type can be configured with:
- Default annual allocation
- Maximum carry forward days
- Approval requirements
- Color coding for visual identification

## Data Storage
- Uses browser localStorage for data persistence
- Leave requests and balances stored separately
- Adjustment history maintained for audit purposes
- Data survives browser sessions
- Ready for backend API integration

## Technical Details
- **Framework**: Vanilla JavaScript with Bootstrap 4
- **Storage**: localStorage (easily replaceable with API calls)
- **Responsive**: Works on desktop and mobile devices
- **Export**: CSV format for reports
- **Validation**: Client-side form validation with balance checking

## Integration Points
- **Employee Database**: Links to employee records
- **Attendance System**: Can integrate with daily attendance
- **Payroll System**: Leave data available for payroll calculations
- **Email System**: Ready for notification integration

## Workflow Examples

### Standard Leave Request Flow:
1. Employee submits request
2. System checks available balance
3. Request goes to pending status
4. Manager reviews and approves/rejects
5. Employee and HR receive notifications
6. Balance automatically updated upon approval

### Year-End Balance Management:
1. HR reviews all employee balances
2. Calculate carry forward amounts
3. Use bulk update to reset annual allocations
4. Generate reports for audit purposes
5. Notify employees of new year balances

## Customization Options
- **Leave Types**: Add custom leave types with specific rules
- **Approval Hierarchy**: Configure multi-level approval workflows
- **Balance Rules**: Set department-specific allocation rules
- **Notification Templates**: Customize email notification content
- **Report Formats**: Modify export formats and content

## Future Enhancements
- **Calendar Integration**: Visual calendar view of approved leaves
- **Mobile App**: Dedicated mobile application for requests
- **Advanced Analytics**: Predictive analytics for leave planning
- **Integration APIs**: REST APIs for third-party integrations
- **Document Attachments**: Support for medical certificates and documents
- **Automated Workflows**: Rule-based automatic approvals for certain scenarios