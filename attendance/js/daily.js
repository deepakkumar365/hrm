// Daily Attendance Management JavaScript
let employees = [];
let attendanceData = [];
let filteredAttendance = [];
let currentPage = 1;
let currentEmployeeId = null;
const itemsPerPage = 15;

// Sample employees data (in real app, this would come from API)
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

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Set today's date as default
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('attendanceDate').value = today;
    
    loadEmployees();
    loadAttendanceForDate();
    setupEventListeners();
});

// Load employees data
function loadEmployees() {
    employees = [...sampleEmployees];
}

// Setup event listeners
function setupEventListeners() {
    // Search input
    document.getElementById('searchEmployee').addEventListener('input', debounce(searchEmployees, 300));
    
    // Date change
    document.getElementById('attendanceDate').addEventListener('change', loadAttendanceForDate);
}

// Load attendance for selected date
function loadAttendanceForDate() {
    const selectedDate = document.getElementById('attendanceDate').value;
    if (!selectedDate) {
        showNotification('Please select a date', 'warning');
        return;
    }
    
    // Initialize attendance data for the date
    initializeAttendanceData(selectedDate);
    displayAttendance();
    updateSummary();
    updatePagination();
}

// Initialize attendance data for all active employees
function initializeAttendanceData(date) {
    // Get existing attendance data for the date (from localStorage or API)
    const existingData = getStoredAttendance(date);
    
    attendanceData = employees.map(emp => {
        const existing = existingData.find(att => att.employeeId === emp.id);
        
        if (existing) {
            return existing;
        } else {
            // Default attendance status based on employee status
            let defaultAttendance = 'Present';
            if (emp.status === 'On Leave') {
                defaultAttendance = 'On Leave';
            }
            
            return {
                employeeId: emp.id,
                date: date,
                attendance: defaultAttendance,
                timeIn: defaultAttendance === 'Present' ? '09:00' : '',
                timeOut: defaultAttendance === 'Present' ? '17:00' : '',
                notes: ''
            };
        }
    });
    
    filteredAttendance = [...attendanceData];
}

// Get stored attendance data from localStorage
function getStoredAttendance(date) {
    const stored = localStorage.getItem(`attendance_${date}`);
    return stored ? JSON.parse(stored) : [];
}

// Save attendance data to localStorage
function saveAttendanceToStorage(date, data) {
    localStorage.setItem(`attendance_${date}`, JSON.stringify(data));
}

// Display attendance table
function displayAttendance() {
    const tbody = document.querySelector('#attendanceTable tbody');
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageAttendance = filteredAttendance.slice(startIndex, endIndex);
    
    tbody.innerHTML = pageAttendance.map(att => {
        const employee = employees.find(emp => emp.id === att.employeeId);
        if (!employee) return '';
        
        return `
            <tr>
                <td>${employee.id}</td>
                <td>${employee.firstName} ${employee.lastName}</td>
                <td>${employee.department}</td>
                <td>${employee.position}</td>
                <td><span class="badge badge-${getEmployeeStatusColor(employee.status)}">${employee.status}</span></td>
                <td>
                    <select class="form-control form-control-sm" onchange="updateAttendance(${att.employeeId}, 'attendance', this.value)">
                        <option value="Present" ${att.attendance === 'Present' ? 'selected' : ''}>Present</option>
                        <option value="Absent" ${att.attendance === 'Absent' ? 'selected' : ''}>Absent</option>
                        <option value="Late" ${att.attendance === 'Late' ? 'selected' : ''}>Late</option>
                        <option value="Half Day" ${att.attendance === 'Half Day' ? 'selected' : ''}>Half Day</option>
                        <option value="On Leave" ${att.attendance === 'On Leave' ? 'selected' : ''}>On Leave</option>
                    </select>
                </td>
                <td>
                    <input type="time" class="form-control form-control-sm" value="${att.timeIn}" 
                           onchange="updateAttendance(${att.employeeId}, 'timeIn', this.value)"
                           ${att.attendance === 'Absent' || att.attendance === 'On Leave' ? 'disabled' : ''}>
                </td>
                <td>
                    <input type="time" class="form-control form-control-sm" value="${att.timeOut}" 
                           onchange="updateAttendance(${att.employeeId}, 'timeOut', this.value)"
                           ${att.attendance === 'Absent' || att.attendance === 'On Leave' ? 'disabled' : ''}>
                </td>
                <td>
                    <button class="btn btn-info btn-xs" onclick="showNotesModal(${att.employeeId})" title="Add Notes">
                        ${att.notes ? '📝' : '➕'}
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Update attendance data
function updateAttendance(employeeId, field, value) {
    const attendanceIndex = attendanceData.findIndex(att => att.employeeId === employeeId);
    if (attendanceIndex !== -1) {
        attendanceData[attendanceIndex][field] = value;
        
        // Auto-clear time fields for absent/on leave employees
        if (field === 'attendance' && (value === 'Absent' || value === 'On Leave')) {
            attendanceData[attendanceIndex].timeIn = '';
            attendanceData[attendanceIndex].timeOut = '';
        }
        
        // Auto-set default times for present employees
        if (field === 'attendance' && value === 'Present') {
            if (!attendanceData[attendanceIndex].timeIn) {
                attendanceData[attendanceIndex].timeIn = '09:00';
            }
            if (!attendanceData[attendanceIndex].timeOut) {
                attendanceData[attendanceIndex].timeOut = '17:00';
            }
        }
        
        // Update filtered data
        const filteredIndex = filteredAttendance.findIndex(att => att.employeeId === employeeId);
        if (filteredIndex !== -1) {
            filteredAttendance[filteredIndex] = {...attendanceData[attendanceIndex]};
        }
        
        displayAttendance();
        updateSummary();
    }
}

// Show notes modal
function showNotesModal(employeeId) {
    const employee = employees.find(emp => emp.id === employeeId);
    const attendance = attendanceData.find(att => att.employeeId === employeeId);
    
    if (employee && attendance) {
        currentEmployeeId = employeeId;
        document.getElementById('employeeName').value = `${employee.firstName} ${employee.lastName}`;
        document.getElementById('attendanceNotes').value = attendance.notes || '';
        $('#notesModal').modal('show');
    }
}

// Save notes
function saveNotes() {
    const notes = document.getElementById('attendanceNotes').value;
    if (currentEmployeeId) {
        updateAttendance(currentEmployeeId, 'notes', notes);
        $('#notesModal').modal('hide');
        showNotification('Notes saved successfully', 'success');
    }
}

// Update summary counts
function updateSummary() {
    const present = filteredAttendance.filter(att => att.attendance === 'Present' || att.attendance === 'Late').length;
    const absent = filteredAttendance.filter(att => att.attendance === 'Absent').length;
    const onLeave = filteredAttendance.filter(att => att.attendance === 'On Leave').length;
    const total = filteredAttendance.length;
    
    document.getElementById('presentCount').textContent = present;
    document.getElementById('absentCount').textContent = absent;
    document.getElementById('onLeaveCount').textContent = onLeave;
    document.getElementById('totalCount').textContent = total;
}

// Mark all present
function markAllPresent() {
    if (confirm('Are you sure you want to mark all active employees as present?')) {
        attendanceData.forEach(att => {
            const employee = employees.find(emp => emp.id === att.employeeId);
            if (employee && employee.status === 'Active') {
                att.attendance = 'Present';
                att.timeIn = att.timeIn || '09:00';
                att.timeOut = att.timeOut || '17:00';
            }
        });
        
        filteredAttendance = [...attendanceData];
        displayAttendance();
        updateSummary();
        showNotification('All active employees marked as present', 'success');
    }
}

// Save attendance
function saveAttendance() {
    const selectedDate = document.getElementById('attendanceDate').value;
    if (!selectedDate) {
        showNotification('Please select a date', 'warning');
        return;
    }
    
    // Validate attendance data
    const invalidEntries = attendanceData.filter(att => {
        return (att.attendance === 'Present' || att.attendance === 'Late') && (!att.timeIn || !att.timeOut);
    });
    
    if (invalidEntries.length > 0) {
        showNotification(`Please set time in/out for all present employees (${invalidEntries.length} missing)`, 'warning');
        return;
    }
    
    // Save to localStorage (in real app, this would be an API call)
    saveAttendanceToStorage(selectedDate, attendanceData);
    showNotification('Attendance saved successfully', 'success');
}

// Export attendance
function exportAttendance() {
    const selectedDate = document.getElementById('attendanceDate').value;
    if (!selectedDate) {
        showNotification('Please select a date', 'warning');
        return;
    }
    
    // Create CSV content
    let csvContent = 'Employee ID,Name,Department,Position,Attendance,Time In,Time Out,Notes\n';
    
    filteredAttendance.forEach(att => {
        const employee = employees.find(emp => emp.id === att.employeeId);
        if (employee) {
            csvContent += `${employee.id},"${employee.firstName} ${employee.lastName}","${employee.department}","${employee.position}","${att.attendance}","${att.timeIn}","${att.timeOut}","${att.notes || ''}"\n`;
        }
    });
    
    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `attendance_${selectedDate}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showNotification('Attendance exported successfully', 'success');
}

// Search employees
function searchEmployees() {
    const searchTerm = document.getElementById('searchEmployee').value.toLowerCase();
    
    if (!searchTerm) {
        filteredAttendance = [...attendanceData];
    } else {
        filteredAttendance = attendanceData.filter(att => {
            const employee = employees.find(emp => emp.id === att.employeeId);
            if (!employee) return false;
            
            return employee.firstName.toLowerCase().includes(searchTerm) ||
                   employee.lastName.toLowerCase().includes(searchTerm) ||
                   employee.department.toLowerCase().includes(searchTerm) ||
                   employee.position.toLowerCase().includes(searchTerm);
        });
    }
    
    currentPage = 1;
    displayAttendance();
    updateSummary();
    updatePagination();
}

// Update pagination
function updatePagination() {
    const totalPages = Math.ceil(filteredAttendance.length / itemsPerPage);
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
    const totalPages = Math.ceil(filteredAttendance.length / itemsPerPage);
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        displayAttendance();
        updatePagination();
    }
}

// Utility functions
function getEmployeeStatusColor(status) {
    switch (status) {
        case 'Active': return 'success';
        case 'Inactive': return 'secondary';
        case 'On Leave': return 'warning';
        default: return 'secondary';
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