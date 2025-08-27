// Overtime Management JavaScript
// Handles OT calculations, approvals, and reporting

let overtimeData = [];
let employees = [];
let currentOTEntry = null;
let currentPage = 1;
const itemsPerPage = 10;

// Initialize overtime management
document.addEventListener('DOMContentLoaded', function() {
    initializeOvertimeManagement();
});

function initializeOvertimeManagement() {
    loadEmployees();
    loadOvertimeData();
    setupDateSelectors();
    setupEventListeners();
    
    // Set default date to today
    document.getElementById('otDate').value = new Date().toISOString().split('T')[0];
}

function setupDateSelectors() {
    const monthSelect = document.getElementById('monthSelect');
    const yearSelect = document.getElementById('yearSelect');
    const currentDate = new Date();
    
    // Populate months
    const months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];
    
    months.forEach((month, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = month;
        if (index === currentDate.getMonth()) {
            option.selected = true;
        }
        monthSelect.appendChild(option);
    });
    
    // Populate years
    const currentYear = currentDate.getFullYear();
    for (let year = currentYear - 2; year <= currentYear + 1; year++) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        if (year === currentYear) {
            option.selected = true;
        }
        yearSelect.appendChild(option);
    }
}

function setupEventListeners() {
    // Search functionality
    document.getElementById('searchOT').addEventListener('input', function() {
        searchOTRecords();
    });
}

function loadEmployees() {
    // Load from localStorage or use sample data
    const storedEmployees = localStorage.getItem('employees');
    if (storedEmployees) {
        employees = JSON.parse(storedEmployees);
    } else {
        // Sample employee data
        employees = [
            { id: 1, name: 'John Doe', department: 'IT', position: 'Developer', hourlyRate: 25.00 },
            { id: 2, name: 'Jane Smith', department: 'HR', position: 'Manager', hourlyRate: 30.00 },
            { id: 3, name: 'Mike Johnson', department: 'Finance', position: 'Analyst', hourlyRate: 22.00 },
            { id: 4, name: 'Sarah Wilson', department: 'Marketing', position: 'Coordinator', hourlyRate: 20.00 },
            { id: 5, name: 'David Brown', department: 'IT', position: 'Senior Developer', hourlyRate: 35.00 }
        ];
    }
    
    populateEmployeeDropdown();
}

function populateEmployeeDropdown() {
    const employeeSelect = document.getElementById('otEmployee');
    employeeSelect.innerHTML = '<option value="">Select Employee</option>';
    
    employees.forEach(employee => {
        const option = document.createElement('option');
        option.value = employee.id;
        option.textContent = `${employee.name} - ${employee.department}`;
        option.dataset.hourlyRate = employee.hourlyRate;
        employeeSelect.appendChild(option);
    });
}

function loadOvertimeData() {
    // Load from localStorage
    const storedOT = localStorage.getItem('overtimeData');
    if (storedOT) {
        overtimeData = JSON.parse(storedOT);
    } else {
        // Sample OT data
        overtimeData = [
            {
                id: 1,
                date: '2024-01-15',
                employeeId: 1,
                regularHours: 8,
                totalHours: 10,
                otHours: 2,
                hourlyRate: 25.00,
                otMultiplier: 1.5,
                otAmount: 75.00,
                status: 'approved',
                reason: 'Project deadline',
                createdAt: new Date().toISOString()
            },
            {
                id: 2,
                date: '2024-01-16',
                employeeId: 2,
                regularHours: 8,
                totalHours: 9.5,
                otHours: 1.5,
                hourlyRate: 30.00,
                otMultiplier: 1.5,
                otAmount: 67.50,
                status: 'pending',
                reason: 'Staff meeting preparation',
                createdAt: new Date().toISOString()
            }
        ];
    }
    
    updateOTSummary();
    displayOTRecords();
}

function updateOTSummary() {
    const selectedMonth = parseInt(document.getElementById('monthSelect').value);
    const selectedYear = parseInt(document.getElementById('yearSelect').value);
    
    const monthlyOT = overtimeData.filter(ot => {
        const otDate = new Date(ot.date);
        return otDate.getMonth() === selectedMonth && otDate.getFullYear() === selectedYear;
    });
    
    const totalHours = monthlyOT.reduce((sum, ot) => sum + ot.otHours, 0);
    const approvedHours = monthlyOT.filter(ot => ot.status === 'approved').reduce((sum, ot) => sum + ot.otHours, 0);
    const pendingHours = monthlyOT.filter(ot => ot.status === 'pending').reduce((sum, ot) => sum + ot.otHours, 0);
    const totalCost = monthlyOT.filter(ot => ot.status === 'approved').reduce((sum, ot) => sum + ot.otAmount, 0);
    
    document.getElementById('totalOTHours').textContent = totalHours.toFixed(1);
    document.getElementById('approvedOTHours').textContent = approvedHours.toFixed(1);
    document.getElementById('pendingOTHours').textContent = pendingHours.toFixed(1);
    document.getElementById('totalOTCost').textContent = `$${totalCost.toFixed(2)}`;
}

function displayOTRecords() {
    const selectedMonth = parseInt(document.getElementById('monthSelect').value);
    const selectedYear = parseInt(document.getElementById('yearSelect').value);
    const searchTerm = document.getElementById('searchOT').value.toLowerCase();
    
    let filteredOT = overtimeData.filter(ot => {
        const otDate = new Date(ot.date);
        const employee = employees.find(emp => emp.id === ot.employeeId);
        const matchesDate = otDate.getMonth() === selectedMonth && otDate.getFullYear() === selectedYear;
        const matchesSearch = !searchTerm || 
            (employee && employee.name.toLowerCase().includes(searchTerm)) ||
            (employee && employee.department.toLowerCase().includes(searchTerm));
        
        return matchesDate && matchesSearch;
    });
    
    // Sort by date (newest first)
    filteredOT.sort((a, b) => new Date(b.date) - new Date(a.date));
    
    const tbody = document.querySelector('#overtimeTable tbody');
    tbody.innerHTML = '';
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageData = filteredOT.slice(startIndex, endIndex);
    
    pageData.forEach(ot => {
        const employee = employees.find(emp => emp.id === ot.employeeId);
        if (!employee) return;
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${formatDate(ot.date)}</td>
            <td>${employee.name}</td>
            <td>${employee.department}</td>
            <td>${ot.regularHours}</td>
            <td>${ot.otHours}</td>
            <td>${ot.otMultiplier}x</td>
            <td>$${ot.otAmount.toFixed(2)}</td>
            <td>
                <span class="badge badge-${getStatusColor(ot.status)} ot-rate-badge">
                    ${ot.status.toUpperCase()}
                </span>
            </td>
            <td>${ot.reason}</td>
            <td>
                <button class="btn btn-info btn-xs mr-1" onclick="viewOTDetails(${ot.id})">View</button>
                <button class="btn btn-warning btn-xs mr-1" onclick="editOTEntry(${ot.id})">Edit</button>
                <button class="btn btn-danger btn-xs" onclick="deleteOTEntry(${ot.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    updatePagination(filteredOT.length);
}

function getStatusColor(status) {
    switch (status) {
        case 'approved': return 'success';
        case 'pending': return 'warning';
        case 'rejected': return 'danger';
        default: return 'secondary';
    }
}

function updatePagination(totalItems) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const pagination = document.getElementById('otPagination');
    pagination.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    // Previous button
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
    prevLi.innerHTML = '<a class="page-link" href="#" onclick="changePage(' + (currentPage - 1) + ')">Previous</a>';
    pagination.appendChild(prevLi);
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === currentPage ? 'active' : ''}`;
        li.innerHTML = '<a class="page-link" href="#" onclick="changePage(' + i + ')">' + i + '</a>';
        pagination.appendChild(li);
    }
    
    // Next button
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
    nextLi.innerHTML = '<a class="page-link" href="#" onclick="changePage(' + (currentPage + 1) + ')">Next</a>';
    pagination.appendChild(nextLi);
}

function changePage(page) {
    currentPage = page;
    displayOTRecords();
}

function showAddOTModal() {
    currentOTEntry = null;
    document.getElementById('otModalTitle').textContent = 'Add Overtime Entry';
    document.getElementById('otForm').reset();
    document.getElementById('otDate').value = new Date().toISOString().split('T')[0];
    document.getElementById('regularHours').value = 8;
    document.getElementById('otMultiplier').value = 1.5;
    document.getElementById('otStatus').value = 'pending';
    
    // Clear calculations
    document.getElementById('otHours').value = '';
    document.getElementById('otAmount').value = '';
    updateCalculationBreakdown(0, 0, 0);
    
    $('#otModal').modal('show');
}

function editOTEntry(otId) {
    const ot = overtimeData.find(entry => entry.id === otId);
    if (!ot) return;
    
    currentOTEntry = ot;
    document.getElementById('otModalTitle').textContent = 'Edit Overtime Entry';
    
    // Populate form
    document.getElementById('otDate').value = ot.date;
    document.getElementById('otEmployee').value = ot.employeeId;
    document.getElementById('regularHours').value = ot.regularHours;
    document.getElementById('totalHours').value = ot.totalHours;
    document.getElementById('otHours').value = ot.otHours;
    document.getElementById('hourlyRate').value = ot.hourlyRate;
    document.getElementById('otMultiplier').value = ot.otMultiplier;
    document.getElementById('otAmount').value = ot.otAmount;
    document.getElementById('otReason').value = ot.reason;
    document.getElementById('otStatus').value = ot.status;
    
    calculateOT();
    $('#otModal').modal('show');
}

function calculateOT() {
    const regularHours = parseFloat(document.getElementById('regularHours').value) || 0;
    const totalHours = parseFloat(document.getElementById('totalHours').value) || 0;
    const hourlyRate = parseFloat(document.getElementById('hourlyRate').value) || 0;
    const otMultiplier = parseFloat(document.getElementById('otMultiplier').value) || 1.5;
    
    const otHours = Math.max(0, totalHours - regularHours);
    const otAmount = otHours * hourlyRate * otMultiplier;
    
    document.getElementById('otHours').value = otHours.toFixed(1);
    document.getElementById('otAmount').value = otAmount.toFixed(2);
    
    // Update calculation breakdown
    const regularPay = regularHours * hourlyRate;
    const otPay = otAmount;
    const totalPay = regularPay + otPay;
    
    updateCalculationBreakdown(regularPay, otPay, totalPay);
}

function updateCalculationBreakdown(regularPay, otPay, totalPay) {
    document.getElementById('regularPay').textContent = `$${regularPay.toFixed(2)}`;
    document.getElementById('otPay').textContent = `$${otPay.toFixed(2)}`;
    document.getElementById('totalPay').textContent = `$${totalPay.toFixed(2)}`;
}

// Auto-fill hourly rate when employee is selected
document.addEventListener('change', function(e) {
    if (e.target.id === 'otEmployee') {
        const selectedOption = e.target.options[e.target.selectedIndex];
        const hourlyRate = selectedOption.dataset.hourlyRate;
        if (hourlyRate) {
            document.getElementById('hourlyRate').value = hourlyRate;
            calculateOT();
        }
    }
});

function saveOTEntry() {
    const form = document.getElementById('otForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const otData = {
        id: currentOTEntry ? currentOTEntry.id : Date.now(),
        date: document.getElementById('otDate').value,
        employeeId: parseInt(document.getElementById('otEmployee').value),
        regularHours: parseFloat(document.getElementById('regularHours').value),
        totalHours: parseFloat(document.getElementById('totalHours').value),
        otHours: parseFloat(document.getElementById('otHours').value),
        hourlyRate: parseFloat(document.getElementById('hourlyRate').value),
        otMultiplier: parseFloat(document.getElementById('otMultiplier').value),
        otAmount: parseFloat(document.getElementById('otAmount').value),
        status: document.getElementById('otStatus').value,
        reason: document.getElementById('otReason').value,
        createdAt: currentOTEntry ? currentOTEntry.createdAt : new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };
    
    if (currentOTEntry) {
        // Update existing entry
        const index = overtimeData.findIndex(ot => ot.id === currentOTEntry.id);
        if (index !== -1) {
            overtimeData[index] = otData;
        }
    } else {
        // Add new entry
        overtimeData.push(otData);
    }
    
    // Save to localStorage
    localStorage.setItem('overtimeData', JSON.stringify(overtimeData));
    
    // Refresh display
    updateOTSummary();
    displayOTRecords();
    
    $('#otModal').modal('hide');
    
    // Show success message
    alert(currentOTEntry ? 'OT entry updated successfully!' : 'OT entry added successfully!');
}

function deleteOTEntry(otId) {
    if (confirm('Are you sure you want to delete this OT entry?')) {
        overtimeData = overtimeData.filter(ot => ot.id !== otId);
        localStorage.setItem('overtimeData', JSON.stringify(overtimeData));
        
        updateOTSummary();
        displayOTRecords();
        
        alert('OT entry deleted successfully!');
    }
}

function viewOTDetails(otId) {
    const ot = overtimeData.find(entry => entry.id === otId);
    const employee = employees.find(emp => emp.id === ot.employeeId);
    
    if (!ot || !employee) return;
    
    const detailsContent = document.getElementById('otDetailsContent');
    detailsContent.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Employee Information</h6>
                <p><strong>Name:</strong> ${employee.name}</p>
                <p><strong>Department:</strong> ${employee.department}</p>
                <p><strong>Position:</strong> ${employee.position}</p>
            </div>
            <div class="col-md-6">
                <h6>Overtime Details</h6>
                <p><strong>Date:</strong> ${formatDate(ot.date)}</p>
                <p><strong>Status:</strong> <span class="badge badge-${getStatusColor(ot.status)}">${ot.status.toUpperCase()}</span></p>
                <p><strong>Reason:</strong> ${ot.reason}</p>
            </div>
        </div>
        <hr>
        <div class="row">
            <div class="col-md-12">
                <h6>Time & Payment Breakdown</h6>
                <table class="table table-sm">
                    <tr><td>Regular Hours:</td><td>${ot.regularHours}</td></tr>
                    <tr><td>Total Hours Worked:</td><td>${ot.totalHours}</td></tr>
                    <tr><td>Overtime Hours:</td><td>${ot.otHours}</td></tr>
                    <tr><td>Hourly Rate:</td><td>$${ot.hourlyRate.toFixed(2)}</td></tr>
                    <tr><td>OT Multiplier:</td><td>${ot.otMultiplier}x</td></tr>
                    <tr><td>Regular Pay:</td><td>$${(ot.regularHours * ot.hourlyRate).toFixed(2)}</td></tr>
                    <tr><td><strong>OT Amount:</strong></td><td><strong>$${ot.otAmount.toFixed(2)}</strong></td></tr>
                    <tr><td><strong>Total Pay:</strong></td><td><strong>$${((ot.regularHours * ot.hourlyRate) + ot.otAmount).toFixed(2)}</strong></td></tr>
                </table>
            </div>
        </div>
    `;
    
    currentOTEntry = ot;
    $('#otDetailsModal').modal('show');
}

function approveOT() {
    if (currentOTEntry) {
        currentOTEntry.status = 'approved';
        const index = overtimeData.findIndex(ot => ot.id === currentOTEntry.id);
        if (index !== -1) {
            overtimeData[index] = currentOTEntry;
            localStorage.setItem('overtimeData', JSON.stringify(overtimeData));
            
            updateOTSummary();
            displayOTRecords();
            $('#otDetailsModal').modal('hide');
            
            alert('OT entry approved successfully!');
        }
    }
}

function rejectOT() {
    if (currentOTEntry) {
        const reason = prompt('Enter reason for rejection:');
        if (reason) {
            currentOTEntry.status = 'rejected';
            currentOTEntry.rejectionReason = reason;
            
            const index = overtimeData.findIndex(ot => ot.id === currentOTEntry.id);
            if (index !== -1) {
                overtimeData[index] = currentOTEntry;
                localStorage.setItem('overtimeData', JSON.stringify(overtimeData));
                
                updateOTSummary();
                displayOTRecords();
                $('#otDetailsModal').modal('hide');
                
                alert('OT entry rejected successfully!');
            }
        }
    }
}

function approveAllPending() {
    if (confirm('Are you sure you want to approve all pending OT entries?')) {
        let approvedCount = 0;
        overtimeData.forEach(ot => {
            if (ot.status === 'pending') {
                ot.status = 'approved';
                approvedCount++;
            }
        });
        
        if (approvedCount > 0) {
            localStorage.setItem('overtimeData', JSON.stringify(overtimeData));
            updateOTSummary();
            displayOTRecords();
            alert(`${approvedCount} OT entries approved successfully!`);
        } else {
            alert('No pending OT entries found.');
        }
    }
}

function searchOTRecords() {
    currentPage = 1;
    displayOTRecords();
}

function calculateOTPayroll() {
    const selectedMonth = parseInt(document.getElementById('monthSelect').value);
    const selectedYear = parseInt(document.getElementById('yearSelect').value);
    
    const monthlyOT = overtimeData.filter(ot => {
        const otDate = new Date(ot.date);
        return otDate.getMonth() === selectedMonth && 
               otDate.getFullYear() === selectedYear && 
               ot.status === 'approved';
    });
    
    if (monthlyOT.length === 0) {
        alert('No approved OT entries found for the selected month.');
        return;
    }
    
    // Group by employee
    const payrollData = {};
    monthlyOT.forEach(ot => {
        const employee = employees.find(emp => emp.id === ot.employeeId);
        if (!employee) return;
        
        if (!payrollData[ot.employeeId]) {
            payrollData[ot.employeeId] = {
                employee: employee,
                totalOTHours: 0,
                totalOTAmount: 0,
                entries: []
            };
        }
        
        payrollData[ot.employeeId].totalOTHours += ot.otHours;
        payrollData[ot.employeeId].totalOTAmount += ot.otAmount;
        payrollData[ot.employeeId].entries.push(ot);
    });
    
    // Generate payroll report
    let report = 'OVERTIME PAYROLL REPORT\n';
    report += `Month: ${document.getElementById('monthSelect').options[selectedMonth].text} ${selectedYear}\n`;
    report += '='.repeat(50) + '\n\n';
    
    let grandTotal = 0;
    Object.values(payrollData).forEach(data => {
        report += `Employee: ${data.employee.name}\n`;
        report += `Department: ${data.employee.department}\n`;
        report += `Total OT Hours: ${data.totalOTHours.toFixed(1)}\n`;
        report += `Total OT Amount: $${data.totalOTAmount.toFixed(2)}\n`;
        report += '-'.repeat(30) + '\n';
        grandTotal += data.totalOTAmount;
    });
    
    report += `\nGRAND TOTAL: $${grandTotal.toFixed(2)}`;
    
    // Display in alert (in real app, this would be a proper report)
    alert(report);
}

function exportOvertimeReport() {
    const selectedMonth = parseInt(document.getElementById('monthSelect').value);
    const selectedYear = parseInt(document.getElementById('yearSelect').value);
    
    const monthlyOT = overtimeData.filter(ot => {
        const otDate = new Date(ot.date);
        return otDate.getMonth() === selectedMonth && otDate.getFullYear() === selectedYear;
    });
    
    if (monthlyOT.length === 0) {
        alert('No OT data found for the selected month.');
        return;
    }
    
    // Create CSV content
    let csvContent = 'Date,Employee,Department,Regular Hours,OT Hours,OT Rate,OT Amount,Status,Reason\n';
    
    monthlyOT.forEach(ot => {
        const employee = employees.find(emp => emp.id === ot.employeeId);
        if (employee) {
            csvContent += `${ot.date},"${employee.name}","${employee.department}",${ot.regularHours},${ot.otHours},${ot.otMultiplier}x,$${ot.otAmount.toFixed(2)},"${ot.status}","${ot.reason}"\n`;
        }
    });
    
    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `overtime_report_${selectedYear}_${(selectedMonth + 1).toString().padStart(2, '0')}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}