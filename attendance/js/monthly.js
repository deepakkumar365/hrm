// Monthly Attendance Management JavaScript
let employees = [];
let monthlyAttendanceData = [];
let filteredEmployees = [];
let currentPage = 1;
let currentMonth = new Date().getMonth() + 1;
let currentYear = new Date().getFullYear();
const itemsPerPage = 20;

// Sample employees data (same as daily attendance)
const sampleEmployees = [
    {
        id: 1,
        firstName: "John",
        lastName: "Doe",
        email: "john.doe@company.com",
        department: "IT",
        position: "Software Developer",
        status: "Active"
    },
    {
        id: 2,
        firstName: "Jane",
        lastName: "Smith",
        email: "jane.smith@company.com",
        department: "HR",
        position: "HR Manager",
        status: "Active"
    },
    {
        id: 3,
        firstName: "Mike",
        lastName: "Johnson",
        email: "mike.johnson@company.com",
        department: "Finance",
        position: "Financial Analyst",
        status: "Active"
    },
    {
        id: 4,
        firstName: "Sarah",
        lastName: "Wilson",
        email: "sarah.wilson@company.com",
        department: "Finance",
        position: "Finance Director",
        status: "Active"
    },
    {
        id: 5,
        firstName: "Tom",
        lastName: "Brown",
        email: "tom.brown@company.com",
        department: "Marketing",
        position: "Marketing Specialist",
        status: "On Leave"
    },
    {
        id: 6,
        firstName: "Lisa",
        lastName: "Davis",
        email: "lisa.davis@company.com",
        department: "Marketing",
        position: "Marketing Manager",
        status: "Active"
    },
    {
        id: 7,
        firstName: "David",
        lastName: "Miller",
        email: "david.miller@company.com",
        department: "IT",
        position: "System Administrator",
        status: "Active"
    },
    {
        id: 8,
        firstName: "Emily",
        lastName: "Garcia",
        email: "emily.garcia@company.com",
        department: "HR",
        position: "HR Specialist",
        status: "Active"
    }
];

// Holidays for the year (you can customize this)
const holidays = [
    '2024-01-01', // New Year
    '2024-07-04', // Independence Day
    '2024-12-25', // Christmas
    // Add more holidays as needed
];

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    loadEmployees();
    initializeSelectors();
    loadMonthlyAttendance();
    setupEventListeners();
});

// Load employees data
function loadEmployees() {
    employees = [...sampleEmployees];
    filteredEmployees = [...employees];
    loadDepartmentFilter();
}

// Initialize month and year selectors
function initializeSelectors() {
    const monthSelect = document.getElementById('monthSelect');
    const yearSelect = document.getElementById('yearSelect');
    
    // Populate months
    const months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];
    
    months.forEach((month, index) => {
        const option = document.createElement('option');
        option.value = index + 1;
        option.textContent = month;
        option.selected = (index + 1) === currentMonth;
        monthSelect.appendChild(option);
    });
    
    // Populate years (current year ± 2)
    for (let year = currentYear - 2; year <= currentYear + 2; year++) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        option.selected = year === currentYear;
        yearSelect.appendChild(option);
    }
}

// Load department filter
function loadDepartmentFilter() {
    const departments = [...new Set(employees.map(emp => emp.department))];
    const select = document.getElementById('departmentFilter');
    
    // Clear existing options except the first one
    select.innerHTML = '<option value="">All Departments</option>';
    
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept;
        option.textContent = dept;
        select.appendChild(option);
    });
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('searchEmployee').addEventListener('input', debounce(applyFilters, 300));
    document.getElementById('departmentFilter').addEventListener('change', applyFilters);
}

// Load monthly attendance data
function loadMonthlyAttendance() {
    currentMonth = parseInt(document.getElementById('monthSelect').value);
    currentYear = parseInt(document.getElementById('yearSelect').value);
    
    // Get all days in the month
    const daysInMonth = new Date(currentYear, currentMonth, 0).getDate();
    const monthDates = [];
    
    for (let day = 1; day <= daysInMonth; day++) {
        monthDates.push(new Date(currentYear, currentMonth - 1, day));
    }
    
    // Load attendance data for each employee for the month
    monthlyAttendanceData = filteredEmployees.map(employee => {
        const employeeAttendance = {
            employee: employee,
            attendance: {},
            summary: {
                present: 0,
                absent: 0,
                late: 0,
                halfDay: 0,
                leave: 0,
                workingDays: 0
            }
        };
        
        monthDates.forEach(date => {
            const dateStr = date.toISOString().split('T')[0];
            const dayOfWeek = date.getDay();
            
            // Check if it's weekend
            if (dayOfWeek === 0 || dayOfWeek === 6) {
                employeeAttendance.attendance[dateStr] = {
                    status: 'Weekend',
                    timeIn: '',
                    timeOut: '',
                    notes: ''
                };
            }
            // Check if it's holiday
            else if (holidays.includes(dateStr)) {
                employeeAttendance.attendance[dateStr] = {
                    status: 'Holiday',
                    timeIn: '',
                    timeOut: '',
                    notes: ''
                };
            }
            // Working day
            else {
                employeeAttendance.summary.workingDays++;
                
                // Get stored attendance or generate sample data
                const storedAttendance = getStoredAttendance(dateStr);
                const employeeRecord = storedAttendance.find(att => att.employeeId === employee.id);
                
                if (employeeRecord) {
                    employeeAttendance.attendance[dateStr] = {
                        status: employeeRecord.attendance,
                        timeIn: employeeRecord.timeIn,
                        timeOut: employeeRecord.timeOut,
                        notes: employeeRecord.notes
                    };
                } else {
                    // Generate sample attendance (mostly present with some random absences)
                    const randomValue = Math.random();
                    let status = 'Present';
                    
                    if (employee.status === 'On Leave') {
                        status = 'On Leave';
                    } else if (randomValue < 0.05) {
                        status = 'Absent';
                    } else if (randomValue < 0.1) {
                        status = 'Late';
                    } else if (randomValue < 0.12) {
                        status = 'Half Day';
                    }
                    
                    employeeAttendance.attendance[dateStr] = {
                        status: status,
                        timeIn: status === 'Present' || status === 'Late' ? '09:00' : '',
                        timeOut: status === 'Present' || status === 'Late' ? '17:00' : status === 'Half Day' ? '13:00' : '',
                        notes: ''
                    };
                }
                
                // Update summary
                const dayStatus = employeeAttendance.attendance[dateStr].status;
                switch (dayStatus) {
                    case 'Present':
                        employeeAttendance.summary.present++;
                        break;
                    case 'Absent':
                        employeeAttendance.summary.absent++;
                        break;
                    case 'Late':
                        employeeAttendance.summary.late++;
                        employeeAttendance.summary.present++; // Late is still considered present
                        break;
                    case 'Half Day':
                        employeeAttendance.summary.halfDay++;
                        employeeAttendance.summary.present += 0.5; // Half day counts as 0.5
                        break;
                    case 'On Leave':
                        employeeAttendance.summary.leave++;
                        break;
                }
            }
        });
        
        return employeeAttendance;
    });
    
    displayMonthlyAttendance();
    updateMonthlySummary();
    updatePagination();
}

// Get stored attendance data from localStorage
function getStoredAttendance(date) {
    const stored = localStorage.getItem(`attendance_${date}`);
    return stored ? JSON.parse(stored) : [];
}

// Display monthly attendance calendar
function displayMonthlyAttendance() {
    const table = document.getElementById('monthlyAttendanceTable');
    const header = document.getElementById('calendarHeader');
    const tbody = table.querySelector('tbody');
    
    // Get all days in the month
    const daysInMonth = new Date(currentYear, currentMonth, 0).getDate();
    
    // Build header with dates
    let headerHTML = `
        <th style="min-width: 150px;">Employee</th>
        <th style="min-width: 100px;">Department</th>
    `;
    
    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(currentYear, currentMonth - 1, day);
        const dayOfWeek = date.getDay();
        const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
        
        headerHTML += `<th class="attendance-cell ${isWeekend ? 'attendance-weekend' : ''}" title="${date.toDateString()}">${day}</th>`;
    }
    
    headerHTML += `
        <th style="min-width: 60px;">Present</th>
        <th style="min-width: 60px;">Absent</th>
        <th style="min-width: 60px;">%</th>
    `;
    
    header.innerHTML = headerHTML;
    
    // Build table body
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageData = monthlyAttendanceData.slice(startIndex, endIndex);
    
    tbody.innerHTML = pageData.map(empData => {
        const employee = empData.employee;
        let rowHTML = `
            <td><a href="#" onclick="showEmployeeDetail(${employee.id})" class="text-decoration-none">${employee.firstName} ${employee.lastName}</a></td>
            <td>${employee.department}</td>
        `;
        
        // Add attendance cells for each day
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(currentYear, currentMonth - 1, day);
            const dateStr = date.toISOString().split('T')[0];
            const attendance = empData.attendance[dateStr];
            
            let cellClass = '';
            let cellText = '';
            
            switch (attendance.status) {
                case 'Present':
                    cellClass = 'attendance-present';
                    cellText = 'P';
                    break;
                case 'Absent':
                    cellClass = 'attendance-absent';
                    cellText = 'A';
                    break;
                case 'Late':
                    cellClass = 'attendance-late';
                    cellText = 'L';
                    break;
                case 'Half Day':
                    cellClass = 'attendance-halfday';
                    cellText = 'H';
                    break;
                case 'On Leave':
                    cellClass = 'attendance-leave';
                    cellText = 'LV';
                    break;
                case 'Weekend':
                    cellClass = 'attendance-weekend';
                    cellText = 'W';
                    break;
                case 'Holiday':
                    cellClass = 'attendance-holiday';
                    cellText = 'HO';
                    break;
                default:
                    cellClass = '';
                    cellText = '-';
            }
            
            rowHTML += `<td class="attendance-cell ${cellClass}" title="${dateStr} - ${attendance.status}">${cellText}</td>`;
        }
        
        // Add summary columns
        const attendancePercentage = empData.summary.workingDays > 0 ? 
            ((empData.summary.present / empData.summary.workingDays) * 100).toFixed(1) : '0.0';
        
        rowHTML += `
            <td class="text-center">${empData.summary.present}</td>
            <td class="text-center">${empData.summary.absent}</td>
            <td class="text-center">${attendancePercentage}%</td>
        `;
        
        return `<tr>${rowHTML}</tr>`;
    }).join('');
}

// Show employee detail modal
function showEmployeeDetail(employeeId) {
    const empData = monthlyAttendanceData.find(data => data.employee.id === employeeId);
    if (!empData) return;
    
    const employee = empData.employee;
    
    // Update modal content
    document.getElementById('modalEmployeeName').textContent = `${employee.firstName} ${employee.lastName}`;
    document.getElementById('modalEmployeeInfo').textContent = `${employee.department} - ${employee.position}`;
    document.getElementById('modalPresentDays').textContent = empData.summary.present;
    document.getElementById('modalAbsentDays').textContent = empData.summary.absent;
    
    // Build attendance details table
    const detailsBody = document.getElementById('modalAttendanceDetails');
    const attendanceEntries = Object.entries(empData.attendance)
        .filter(([date, att]) => att.status !== 'Weekend' && att.status !== 'Holiday')
        .sort(([a], [b]) => new Date(a) - new Date(b));
    
    detailsBody.innerHTML = attendanceEntries.map(([date, att]) => `
        <tr>
            <td>${new Date(date).toLocaleDateString()}</td>
            <td><span class="badge badge-${getAttendanceStatusColor(att.status)}">${att.status}</span></td>
            <td>${att.timeIn || '-'}</td>
            <td>${att.timeOut || '-'}</td>
            <td>${att.notes || '-'}</td>
        </tr>
    `).join('');
    
    $('#employeeDetailModal').modal('show');
}

// Update monthly summary
function updateMonthlySummary() {
    const daysInMonth = new Date(currentYear, currentMonth, 0).getDate();
    let workingDays = 0;
    let totalPresent = 0;
    let totalAbsent = 0;
    
    // Calculate working days in the month
    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(currentYear, currentMonth - 1, day);
        const dayOfWeek = date.getDay();
        const dateStr = date.toISOString().split('T')[0];
        
        if (dayOfWeek !== 0 && dayOfWeek !== 6 && !holidays.includes(dateStr)) {
            workingDays++;
        }
    }
    
    // Calculate totals
    monthlyAttendanceData.forEach(empData => {
        totalPresent += empData.summary.present;
        totalAbsent += empData.summary.absent;
    });
    
    const totalEmployees = filteredEmployees.length;
    const avgAttendance = workingDays > 0 && totalEmployees > 0 ? 
        ((totalPresent / (workingDays * totalEmployees)) * 100).toFixed(1) : '0.0';
    
    document.getElementById('workingDays').textContent = workingDays;
    document.getElementById('totalPresent').textContent = Math.round(totalPresent);
    document.getElementById('totalAbsent').textContent = totalAbsent;
    document.getElementById('avgAttendance').textContent = `${avgAttendance}%`;
    document.getElementById('totalEmployees').textContent = totalEmployees;
}

// Apply filters
function applyFilters() {
    const searchTerm = document.getElementById('searchEmployee').value.toLowerCase();
    const departmentFilter = document.getElementById('departmentFilter').value;
    
    filteredEmployees = employees.filter(emp => {
        const matchesSearch = !searchTerm || 
            emp.firstName.toLowerCase().includes(searchTerm) ||
            emp.lastName.toLowerCase().includes(searchTerm) ||
            emp.position.toLowerCase().includes(searchTerm);
            
        const matchesDepartment = !departmentFilter || emp.department === departmentFilter;
        
        return matchesSearch && matchesDepartment;
    });
    
    currentPage = 1;
    loadMonthlyAttendance();
}

// Clear filters
function clearFilters() {
    document.getElementById('searchEmployee').value = '';
    document.getElementById('departmentFilter').value = '';
    filteredEmployees = [...employees];
    currentPage = 1;
    loadMonthlyAttendance();
}

// Export monthly report
function exportMonthlyReport() {
    const monthName = document.getElementById('monthSelect').selectedOptions[0].text;
    
    // Create CSV content
    let csvContent = `Monthly Attendance Report - ${monthName} ${currentYear}\n\n`;
    csvContent += 'Employee,Department,Position,Present Days,Absent Days,Working Days,Attendance %\n';
    
    monthlyAttendanceData.forEach(empData => {
        const employee = empData.employee;
        const attendancePercentage = empData.summary.workingDays > 0 ? 
            ((empData.summary.present / empData.summary.workingDays) * 100).toFixed(1) : '0.0';
        
        csvContent += `"${employee.firstName} ${employee.lastName}","${employee.department}","${employee.position}",${empData.summary.present},${empData.summary.absent},${empData.summary.workingDays},${attendancePercentage}%\n`;
    });
    
    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `monthly_attendance_${currentYear}_${currentMonth.toString().padStart(2, '0')}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showNotification('Monthly report exported successfully', 'success');
}

// Update pagination
function updatePagination() {
    const totalPages = Math.ceil(monthlyAttendanceData.length / itemsPerPage);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let paginationHTML = '';
    
    // Previous button
    paginationHTML += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${currentPage - 1})">Previous</a>
        </li>
    `;
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            paginationHTML += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
                </li>
            `;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }
    
    // Next button
    paginationHTML += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${currentPage + 1})">Next</a>
        </li>
    `;
    
    pagination.innerHTML = paginationHTML;
}

// Change page
function changePage(page) {
    const totalPages = Math.ceil(monthlyAttendanceData.length / itemsPerPage);
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        displayMonthlyAttendance();
        updatePagination();
    }
}

// Utility functions
function getAttendanceStatusColor(status) {
    switch (status) {
        case 'Present': return 'success';
        case 'Absent': return 'danger';
        case 'Late': return 'warning';
        case 'Half Day': return 'info';
        case 'On Leave': return 'secondary';
        default: return 'light';
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showNotification(message, type = 'info') {
    const alertClass = type === 'success' ? 'alert-success' : 
                     type === 'error' ? 'alert-danger' : 
                     type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert">&times;</button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}