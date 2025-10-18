# Export Functionality - Quick Integration Guide

## Quick Start (3 Steps)

### Step 1: Include Export Script (One Time)

Add to `templates/base.html` before `</body>`:
```html
<!-- Export Functionality -->
<script src="{{ url_for('static', filename='js/export.js') }}"></script>
```

### Step 2: Add Export Toolbar to List Page

Add this code **above your table**:

```html
<!-- Export Toolbar -->
<div class="export-toolbar">
    <div class="export-label">
        <i class="fas fa-download"></i>
        Export Data:
    </div>
    <div class="export-buttons">
        <button type="button" class="export-btn export-csv" 
                onclick="exportToCSV('YOUR_TABLE_ID', 'YOUR_FILENAME')" 
                title="Export Data">
            <i class="fas fa-file-csv"></i>
            CSV
        </button>
        <button type="button" class="export-btn export-excel" 
                onclick="exportToExcel('YOUR_TABLE_ID', 'YOUR_FILENAME')" 
                title="Export Data">
            <i class="fas fa-file-excel"></i>
            Excel
        </button>
        <button type="button" class="export-btn export-pdf" 
                onclick="exportToPDF('YOUR_TABLE_ID', 'YOUR_FILENAME')" 
                title="Export Data">
            <i class="fas fa-file-pdf"></i>
            PDF
        </button>
    </div>
</div>
```

### Step 3: Update Parameters

Replace these values:
- `YOUR_TABLE_ID` → Your table's ID attribute (e.g., 'employeeTable')
- `YOUR_FILENAME` → Base filename for export (e.g., 'employees')

---

## Real Examples

### Example 1: Employee List

```html
<!-- In templates/employees/list.html -->

<!-- Add export toolbar above table -->
<div class="export-toolbar">
    <div class="export-label">
        <i class="fas fa-download"></i>
        Export Data:
    </div>
    <div class="export-buttons">
        <button type="button" class="export-btn export-csv" 
                onclick="exportToCSV('employeeTable', 'employees')" 
                title="Export Data">
            <i class="fas fa-file-csv"></i>
            CSV
        </button>
        <button type="button" class="export-btn export-excel" 
                onclick="exportToExcel('employeeTable', 'employees')" 
                title="Export Data">
            <i class="fas fa-file-excel"></i>
            Excel
        </button>
        <button type="button" class="export-btn export-pdf" 
                onclick="exportToPDF('employeeTable', 'employees')" 
                title="Export Data">
            <i class="fas fa-file-pdf"></i>
            PDF
        </button>
    </div>
</div>

<!-- Your existing table -->
<table id="employeeTable" class="table">
    <!-- table content -->
</table>
```

### Example 2: Attendance List

```html
<!-- In templates/attendance/list.html -->

<div class="export-toolbar">
    <div class="export-label">
        <i class="fas fa-download"></i>
        Export Data:
    </div>
    <div class="export-buttons">
        <button type="button" class="export-btn export-csv" 
                onclick="exportToCSV('attendanceTable', 'attendance')" 
                title="Export Data">
            <i class="fas fa-file-csv"></i>
            CSV
        </button>
        <button type="button" class="export-btn export-excel" 
                onclick="exportToExcel('attendanceTable', 'attendance')" 
                title="Export Data">
            <i class="fas fa-file-excel"></i>
            Excel
        </button>
        <button type="button" class="export-btn export-pdf" 
                onclick="exportToPDF('attendanceTable', 'attendance')" 
                title="Export Data">
            <i class="fas fa-file-pdf"></i>
            PDF
        </button>
    </div>
</div>

<table id="attendanceTable" class="table">
    <!-- table content -->
</table>
```

### Example 3: Payroll List

```html
<!-- In templates/payroll/list.html -->

<div class="export-toolbar">
    <div class="export-label">
        <i class="fas fa-download"></i>
        Export Data:
    </div>
    <div class="export-buttons">
        <button type="button" class="export-btn export-csv" 
                onclick="exportToCSV('payrollTable', 'payroll')" 
                title="Export Data">
            <i class="fas fa-file-csv"></i>
            CSV
        </button>
        <button type="button" class="export-btn export-excel" 
                onclick="exportToExcel('payrollTable', 'payroll')" 
                title="Export Data">
            <i class="fas fa-file-excel"></i>
            Excel
        </button>
        <button type="button" class="export-btn export-pdf" 
                onclick="exportToPDF('payrollTable', 'payroll')" 
                title="Export Data">
            <i class="fas fa-file-pdf"></i>
            PDF
        </button>
    </div>
</div>

<table id="payrollTable" class="table">
    <!-- table content -->
</table>
```

---

## Alternative: Dropdown Style (Mobile-Friendly)

If you prefer a compact dropdown menu:

```html
<div class="export-toolbar">
    <div class="export-dropdown">
        <button type="button" class="export-dropdown-btn" onclick="toggleExportDropdown()">
            <i class="fas fa-download"></i>
            Export Data
            <i class="fas fa-chevron-down"></i>
        </button>
        <div class="export-dropdown-menu" id="exportDropdown">
            <button type="button" class="export-dropdown-item" 
                    onclick="exportToCSV('YOUR_TABLE_ID', 'YOUR_FILENAME'); toggleExportDropdown();">
                <i class="fas fa-file-csv"></i>
                Export as CSV
            </button>
            <button type="button" class="export-dropdown-item" 
                    onclick="exportToExcel('YOUR_TABLE_ID', 'YOUR_FILENAME'); toggleExportDropdown();">
                <i class="fas fa-file-excel"></i>
                Export as Excel
            </button>
            <button type="button" class="export-dropdown-item" 
                    onclick="exportToPDF('YOUR_TABLE_ID', 'YOUR_FILENAME'); toggleExportDropdown();">
                <i class="fas fa-file-pdf"></i>
                Export as PDF
            </button>
        </div>
    </div>
</div>
```

---

## Pages That Need Export Integration

### Main Modules
- [ ] `templates/employees/list.html` → Table ID: `employeeTable`, Filename: `employees`
- [ ] `templates/attendance/list.html` → Table ID: `attendanceTable`, Filename: `attendance`
- [ ] `templates/leave/list.html` → Table ID: `leaveTable`, Filename: `leave_requests`
- [ ] `templates/payroll/list.html` → Table ID: `payrollTable`, Filename: `payroll`
- [ ] `templates/claims/list.html` → Table ID: `claimsTable`, Filename: `claims`
- [ ] `templates/appraisal/list.html` → Table ID: `appraisalTable`, Filename: `appraisals`
- [ ] `templates/users/list.html` → Table ID: `usersTable`, Filename: `users`

### Master Data
- [ ] `templates/masters/departments/list.html` → Table ID: `departmentsTable`, Filename: `departments`
- [ ] `templates/masters/roles/list.html` → Table ID: `rolesTable`, Filename: `roles`
- [ ] `templates/masters/work_schedules/list.html` → Table ID: `schedulesTable`, Filename: `work_schedules`
- [ ] `templates/masters/working_hours/list.html` → Table ID: `hoursTable`, Filename: `working_hours`

### Other
- [ ] `templates/documents/admin_list.html` → Table ID: `documentsTable`, Filename: `documents`
- [ ] `templates/documents/documents_list.html` → Table ID: `documentsTable`, Filename: `my_documents`
- [ ] `templates/team/team_list.html` → Table ID: `teamTable`, Filename: `team_members`

---

## Troubleshooting

### Export buttons not showing?
1. Check if `export.js` is included in base.html
2. Check if CSS styles are loaded
3. Clear browser cache

### Export not working?
1. Verify table has correct ID attribute
2. Check onclick handler has correct parameters
3. Open browser console and check for errors
4. Verify table has data

### Actions column appearing in export?
- The script automatically removes columns with "Actions" in the header
- Make sure your actions column header contains the word "Actions"

### Special characters not displaying correctly?
- CSV export handles special characters automatically
- For Excel, ensure proper encoding in your data

---

## What Gets Exported?

✅ **Included:**
- All visible table rows
- All columns except "Actions"
- Current sorting order
- Filtered data (if filters applied)
- Table headers

❌ **Excluded:**
- Actions column
- Hidden rows (pagination)
- Page headers/footers
- Navigation menus
- Buttons and forms

---

## File Naming

Exported files are automatically named with date:
- CSV: `filename_2024-01-15.csv`
- Excel: `filename_2024-01-15.xls`
- PDF: User chooses filename in print dialog

---

## Browser Compatibility

✅ Tested and working:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## Need Help?

See full documentation: `GENERAL_ENHANCEMENTS_IMPLEMENTATION.md`