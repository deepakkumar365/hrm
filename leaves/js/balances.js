// Leave Balances Management JavaScript
// Handles employee leave balances, adjustments, and reporting

let leaveBalances = [];
let employees = [];
let leaveTypes = [];
let currentEmployee = null;
let currentPage = 1;
const itemsPerPage = 15; // Show 15 employee rows per page

// Initialize leave balances management
document.addEventListener('DOMContentLoaded', function() {
    initializeBalancesManagement();
});

function initializeBalancesManagement() {
    loadEmployees();
    loadLeaveTypes();
    loadLeaveBalances();
    setupDateSelectors();
    setupEventListeners();
    updateSummaryCards();
    displayEmployeeBalances();
}

function setupDateSelectors() {
    const yearSelect = document.getElementById('yearSelect');
    const currentYear = new Date().getFullYear();
    
    // Populate years
    for (let year = currentYear - 2; year <= currentYear + 1; year++) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        if (year === currentYear) {
            option.selected = true;
        }
        yearSelect.appendChild(option);
    }
    
    // Populate departments
    const departments = [...new Set(employees.map(emp => emp.department))];
    const departmentSelect = document.getElementById('departmentFilter');
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept;
        option.textContent = dept;
        departmentSelect.appendChild(option);
    });
}

function setupEventListeners() {
    // Search functionality
    document.getElementById('searchEmployee').addEventListener('input', function() {
        searchEmployees();
    });
    
    // Adjustment calculation
    document.getElementById('adjustmentDays').addEventListener('input', calculateAdjustment);
    document.getElementById('adjustmentType').addEventListener('change', calculateAdjustment);
}

function loadEmployees() {
    // Load from localStorage or use sample data
    const storedEmployees = localStorage.getItem('employees');
    if (storedEmployees) {
        employees = JSON.parse(storedEmployees);
    } else {
        // Sample employee data
        employees = [
            { id: 1, name: 'John Doe', department: 'IT', position: 'Developer', email: 'john.doe@company.com', joinDate: '2023-01-15' },
            { id: 2, name: 'Jane Smith', department: 'HR', position: 'Manager', email: 'jane.smith@company.com', joinDate: '2022-03-10' },
            { id: 3, name: 'Mike Johnson', department: 'Finance', position: 'Analyst', email: 'mike.johnson@company.com', joinDate: '2023-06-01' },
            { id: 4, name: 'Sarah Wilson', department: 'Marketing', position: 'Coordinator', email: 'sarah.wilson@company.com', joinDate: '2023-02-20' },
            { id: 5, name: 'David Brown', department: 'IT', position: 'Senior Developer', email: 'david.brown@company.com', joinDate: '2021-11-05' }
        ];
    }
    
    populateEmployeeDropdowns();
}

function populateEmployeeDropdowns() {
    const employeeSelects = ['adjustEmployee'];
    
    employeeSelects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            select.innerHTML = '<option value="">Select Employee</option>';
            employees.forEach(employee => {
                const option = document.createElement('option');
                option.value = employee.id;
                option.textContent = `${employee.name} - ${employee.department}`;
                select.appendChild(option);
            });
        }
    });
}

function loadLeaveTypes() {
    // Load from localStorage or use default types
    const storedTypes = localStorage.getItem('leaveTypes');
    if (storedTypes) {
        leaveTypes = JSON.parse(storedTypes);
    } else {
        // Default leave types
        leaveTypes = [
            { id: 'annual', name: 'Annual Leave', defaultAllocation: 20, maxCarryForward: 5, requiresApproval: true, color: '#007bff' },
            { id: 'sick', name: 'Sick Leave', defaultAllocation: 10, maxCarryForward: 2, requiresApproval: false, color: '#dc3545' },
            { id: 'personal', name: 'Personal Leave', defaultAllocation: 5, maxCarryForward: 0, requiresApproval: true, color: '#28a745' },
            { id: 'maternity', name: 'Maternity Leave', defaultAllocation: 90, maxCarryForward: 0, requiresApproval: true, color: '#ffc107' },
            { id: 'emergency', name: 'Emergency Leave', defaultAllocation: 3, maxCarryForward: 0, requiresApproval: true, color: '#fd7e14' }
        ];
        localStorage.setItem('leaveTypes', JSON.stringify(leaveTypes));
    }
}

function loadLeaveBalances() {
    // Load from localStorage
    const storedBalances = localStorage.getItem('leaveBalances');
    if (storedBalances) {
        leaveBalances = JSON.parse(storedBalances);
    } else {
        // Generate initial balances for all employees
        generateInitialBalances();
    }
}

function generateInitialBalances() {
    const currentYear = new Date().getFullYear();
    leaveBalances = [];
    
    employees.forEach(employee => {
        leaveTypes.forEach(leaveType => {
            leaveBalances.push({
                id: `${employee.id}_${leaveType.id}_${currentYear}`,
                employeeId: employee.id,
                leaveTypeId: leaveType.id,
                year: currentYear,
                allocated: leaveType.defaultAllocation,
                used: Math.floor(Math.random() * (leaveType.defaultAllocation * 0.3)), // Random used amount
                carryForward: 0,
                adjustments: [],
                lastUpdated: new Date().toISOString()
            });
        });
    });
    
    localStorage.setItem('leaveBalances', JSON.stringify(leaveBalances));
}

function updateSummaryCards() {
    const selectedYear = parseInt(document.getElementById('yearSelect').value);
    const departmentFilter = document.getElementById('departmentFilter').value;
    
    let filteredEmployees = employees;
    if (departmentFilter) {
        filteredEmployees = employees.filter(emp => emp.department === departmentFilter);
    }
    
    const yearBalances = leaveBalances.filter(balance => 
        balance.year === selectedYear && 
        filteredEmployees.some(emp => emp.id === balance.employeeId)
    );
    
    const totalEmployees = filteredEmployees.length;
    const totalAvailable = yearBalances.reduce((sum, balance) => sum + (balance.allocated + balance.carryForward - balance.used), 0);
    const totalUsed = yearBalances.reduce((sum, balance) => sum + balance.used, 0);
    const totalAllocated = yearBalances.reduce((sum, balance) => sum + balance.allocated, 0);
    const averageUtilization = totalAllocated > 0 ? Math.round((totalUsed / totalAllocated) * 100) : 0;
    
    document.getElementById('totalEmployeesCount').textContent = totalEmployees;
    document.getElementById('totalAvailableDays').textContent = totalAvailable;
    document.getElementById('totalUsedDays').textContent = totalUsed;
    document.getElementById('averageUtilization').textContent = `${averageUtilization}%`;
}

function displayEmployeeBalances() {
    const selectedYear = parseInt(document.getElementById('yearSelect').value);
    const departmentFilter = document.getElementById('departmentFilter').value;
    const searchTerm = document.getElementById('searchEmployee').value.toLowerCase();
    
    let filteredEmployees = employees.filter(emp => {
        const matchesDepartment = !departmentFilter || emp.department === departmentFilter;
        const matchesSearch = !searchTerm || 
            emp.name.toLowerCase().includes(searchTerm) ||
            emp.department.toLowerCase().includes(searchTerm);
        
        return matchesDepartment && matchesSearch;
    });
    
    const tbody = document.querySelector('#employeeBalancesTable tbody');
    tbody.innerHTML = '';
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageEmployees = filteredEmployees.slice(startIndex, endIndex);
    
    pageEmployees.forEach(employee => {
        const employeeBalances = leaveBalances.filter(balance => 
            balance.employeeId === employee.id && balance.year === selectedYear
        );
        
        const row = createEmployeeBalanceRow(employee, employeeBalances);
        tbody.appendChild(row);
    });
    
    updatePagination(filteredEmployees.length);
}

function createEmployeeBalanceRow(employee, balances) {
    const row = document.createElement('tr');
    
    // Calculate totals
    const totalUsed = balances.reduce((sum, b) => sum + b.used, 0);
    const totalAvailable = balances.reduce((sum, b) => sum + (b.allocated + b.carryForward - b.used), 0);
    const totalAllocated = balances.reduce((sum, b) => sum + b.allocated, 0);
    const utilizationPercentage = totalAllocated > 0 ? Math.round((totalUsed / totalAllocated) * 100) : 0;
    
    // Get specific leave type balances
    const annualBalance = balances.find(b => b.leaveTypeId === 'annual');
    const sickBalance = balances.find(b => b.leaveTypeId === 'sick');
    const personalBalance = balances.find(b => b.leaveTypeId === 'personal');
    
    // Helper function to format leave balance
    function formatLeaveBalance(balance) {
        if (!balance) return '<span class="text-muted">N/A</span>';
        const available = balance.allocated + balance.carryForward - balance.used;
        const usagePercentage = balance.allocated > 0 ? Math.round((balance.used / balance.allocated) * 100) : 0;
        const leaveType = leaveTypes.find(type => type.id === balance.leaveTypeId);
        
        return `
            <div class="d-flex align-items-center">
                <div class="mr-2">
                    <strong>${available}</strong>/<small>${balance.allocated}</small>
                </div>
                <div class="progress progress-custom flex-grow-1" style="width: 40px;">
                    <div class="progress-bar" style="width: ${usagePercentage}%; background-color: ${leaveType ? leaveType.color : '#007bff'};" 
                         title="${balance.used} days used"></div>
                </div>
            </div>
        `;
    }
    
    row.innerHTML = `
        <td>
            <div>
                <strong>${employee.name}</strong>
                <br><small class="text-muted">${employee.position}</small>
            </div>
        </td>
        <td>
            <span class="badge badge-secondary">${employee.department}</span>
        </td>
        <td>${formatLeaveBalance(annualBalance)}</td>
        <td>${formatLeaveBalance(sickBalance)}</td>
        <td>${formatLeaveBalance(personalBalance)}</td>
        <td><strong class="text-success">${totalAvailable}</strong></td>
        <td><strong class="text-warning">${totalUsed}</strong></td>
        <td>
            <div class="d-flex align-items-center">
                <div class="progress progress-custom flex-grow-1 mr-2" style="width: 50px;">
                    <div class="progress-bar ${utilizationPercentage > 80 ? 'bg-danger' : utilizationPercentage > 60 ? 'bg-warning' : 'bg-success'}" 
                         style="width: ${utilizationPercentage}%"></div>
                </div>
                <small><strong>${utilizationPercentage}%</strong></small>
            </div>
        </td>
        <td>
            <button class="btn btn-info btn-xs mr-1" onclick="viewEmployeeDetails(${employee.id})" title="View Details">
                <i class="fas fa-eye"></i>
            </button>
            <button class="btn btn-warning btn-xs" onclick="showAdjustBalanceModal(); document.getElementById('adjustEmployee').value=${employee.id}; updateCurrentBalance();" title="Adjust Balance">
                <i class="fas fa-edit"></i>
            </button>
        </td>
    `;
    
    return row;
}

function updatePagination(totalItems) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const pagination = document.getElementById('balancesPagination');
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
    displayEmployeeBalances();
}

function viewEmployeeDetails(employeeId) {
    const employee = employees.find(emp => emp.id === employeeId);
    const selectedYear = parseInt(document.getElementById('yearSelect').value);
    const employeeBalances = leaveBalances.filter(balance => 
        balance.employeeId === employeeId && balance.year === selectedYear
    );
    
    if (!employee) return;
    
    currentEmployee = employee;
    
    // Update modal title
    document.getElementById('balanceDetailsTitle').textContent = `${employee.name} - Leave Balance Details`;
    
    // Update employee info
    document.getElementById('employeeInfo').innerHTML = `
        <p class="mb-1"><strong>Name:</strong> ${employee.name}</p>
        <p class="mb-1"><strong>Department:</strong> ${employee.department}</p>
        <p class="mb-1"><strong>Position:</strong> ${employee.position}</p>
        <p class="mb-1"><strong>Email:</strong> ${employee.email}</p>
        <p class="mb-0"><strong>Join Date:</strong> ${formatDate(employee.joinDate)}</p>
    `;
    
    // Update leave types balance table
    const leaveTypesTableBody = document.getElementById('leaveTypesBalanceTable');
    leaveTypesTableBody.innerHTML = '';
    
    let totalAllocated = 0, totalUsed = 0, totalAvailable = 0, totalCarryForward = 0;
    
    employeeBalances.forEach(balance => {
        const leaveType = leaveTypes.find(type => type.id === balance.leaveTypeId);
        if (leaveType) {
            const available = balance.allocated + balance.carryForward - balance.used;
            const usagePercentage = balance.allocated > 0 ? Math.round((balance.used / balance.allocated) * 100) : 0;
            
            totalAllocated += balance.allocated;
            totalUsed += balance.used;
            totalAvailable += available;
            totalCarryForward += balance.carryForward;
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <span class="badge badge-primary" style="background-color: ${leaveType.color};">
                        ${leaveType.name}
                    </span>
                </td>
                <td><strong>${balance.allocated}</strong></td>
                <td>${balance.used}</td>
                <td><strong>${available}</strong></td>
                <td>${balance.carryForward}</td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="progress progress-custom flex-grow-1 mr-2" style="width: 60px;">
                            <div class="progress-bar" style="width: ${usagePercentage}%; background-color: ${leaveType.color};"></div>
                        </div>
                        <small>${usagePercentage}%</small>
                    </div>
                </td>
            `;
            leaveTypesTableBody.appendChild(row);
        }
    });
    
    // Add totals row
    const totalRow = document.createElement('tr');
    totalRow.className = 'table-info font-weight-bold';
    totalRow.innerHTML = `
        <td><strong>TOTAL</strong></td>
        <td><strong>${totalAllocated}</strong></td>
        <td><strong>${totalUsed}</strong></td>
        <td><strong>${totalAvailable}</strong></td>
        <td><strong>${totalCarryForward}</strong></td>
        <td><strong>${totalAllocated > 0 ? Math.round((totalUsed / totalAllocated) * 100) : 0}%</strong></td>
    `;
    leaveTypesTableBody.appendChild(totalRow);
    
    // Update summary stats
    const summaryContainer = document.getElementById('leaveSummary');
    summaryContainer.innerHTML = `
        <div class="row text-center">
            <div class="col-6 mb-2">
                <small class="text-muted">Total Allocated</small>
                <div><strong>${totalAllocated}</strong> days</div>
            </div>
            <div class="col-6 mb-2">
                <small class="text-muted">Total Used</small>
                <div><strong>${totalUsed}</strong> days</div>
            </div>
            <div class="col-6 mb-2">
                <small class="text-muted">Available</small>
                <div><strong>${totalAvailable}</strong> days</div>
            </div>
            <div class="col-6 mb-2">
                <small class="text-muted">Utilization</small>
                <div><strong>${totalAllocated > 0 ? Math.round((totalUsed / totalAllocated) * 100) : 0}%</strong></div>
            </div>
        </div>
    `;
    
    // Load leave history (would come from leave requests)
    loadEmployeeLeaveHistory(employeeId);
    
    $('#balanceDetailsModal').modal('show');
}

function loadEmployeeLeaveHistory(employeeId) {
    // This would typically load from leave requests data
    // For now, generate sample history
    const historyTableBody = document.getElementById('leaveHistoryTable');
    historyTableBody.innerHTML = '';
    
    // Sample leave history data
    const sampleHistory = [
        {
            startDate: '2024-01-15',
            endDate: '2024-01-19',
            leaveType: 'Annual Leave',
            days: 5,
            status: 'approved',
            reason: 'Family vacation'
        },
        {
            startDate: '2023-12-20',
            endDate: '2023-12-21',
            leaveType: 'Sick Leave',
            days: 2,
            status: 'approved',
            reason: 'Medical appointment'
        },
        {
            startDate: '2024-02-15',
            endDate: '2024-02-15',
            leaveType: 'Personal Leave',
            days: 1,
            status: 'pending',
            reason: 'Personal matters'
        },
        {
            startDate: '2023-11-10',
            endDate: '2023-11-12',
            leaveType: 'Annual Leave',
            days: 3,
            status: 'approved',
            reason: 'Long weekend break'
        },
        {
            startDate: '2023-10-05',
            endDate: '2023-10-05',
            leaveType: 'Emergency Leave',
            days: 1,
            status: 'approved',
            reason: 'Family emergency'
        }
    ];
    
    sampleHistory.forEach(leave => {
        const row = document.createElement('tr');
        const dateRange = leave.startDate === leave.endDate ? 
            formatDate(leave.startDate) : 
            `${formatDate(leave.startDate)} - ${formatDate(leave.endDate)}`;
        
        const statusColor = getStatusColor(leave.status);
        
        row.innerHTML = `
            <td>${dateRange}</td>
            <td>
                <span class="badge badge-info leave-type-badge">
                    ${leave.leaveType}
                </span>
            </td>
            <td><strong>${leave.days}</strong></td>
            <td>
                <span class="badge badge-${statusColor}">
                    ${leave.status.toUpperCase()}
                </span>
            </td>
            <td><small>${leave.reason}</small></td>
        `;
        historyTableBody.appendChild(row);
    });
    
    // If no history, show message
    if (sampleHistory.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="5" class="text-center text-muted">
                <em>No leave history found</em>
            </td>
        `;
        historyTableBody.appendChild(row);
    }
}

function getStatusColor(status) {
    switch (status) {
        case 'approved': return 'success';
        case 'pending': return 'warning';
        case 'rejected': return 'danger';
        case 'cancelled': return 'secondary';
        default: return 'secondary';
    }
}

function showAdjustmentModal() {
    document.getElementById('adjustBalanceForm').reset();
    $('#adjustBalanceModal').modal('show');
}

function showAdjustBalanceModal() {
    if (currentEmployee) {
        document.getElementById('adjustEmployee').value = currentEmployee.id;
        updateCurrentBalance();
    }
    $('#balanceDetailsModal').modal('hide');
    $('#adjustBalanceModal').modal('show');
}

function updateCurrentBalance() {
    const employeeId = parseInt(document.getElementById('adjustEmployee').value);
    const leaveTypeId = document.getElementById('adjustLeaveType').value;
    const selectedYear = parseInt(document.getElementById('yearSelect').value);
    
    if (employeeId && leaveTypeId) {
        const balance = leaveBalances.find(b => 
            b.employeeId === employeeId && 
            b.leaveTypeId === leaveTypeId && 
            b.year === selectedYear
        );
        
        if (balance) {
            const currentBalance = balance.allocated + balance.carryForward - balance.used;
            document.getElementById('currentBalance').value = currentBalance;
            calculateAdjustment();
        }
    }
}

function calculateAdjustment() {
    const currentBalance = parseFloat(document.getElementById('currentBalance').value) || 0;
    const adjustmentDays = parseFloat(document.getElementById('adjustmentDays').value) || 0;
    const adjustmentType = document.getElementById('adjustmentType').value;
    
    let newBalance = currentBalance;
    let adjustmentText = '';
    
    switch (adjustmentType) {
        case 'add':
            newBalance = currentBalance + adjustmentDays;
            adjustmentText = `+${adjustmentDays}`;
            break;
        case 'subtract':
            newBalance = Math.max(0, currentBalance - adjustmentDays);
            adjustmentText = `-${adjustmentDays}`;
            break;
        case 'set':
            newBalance = adjustmentDays;
            adjustmentText = `Set to ${adjustmentDays}`;
            break;
    }
    
    document.getElementById('summaryCurrentBalance').textContent = currentBalance;
    document.getElementById('summaryAdjustment').textContent = adjustmentText;
    document.getElementById('summaryNewBalance').textContent = newBalance;
}

function saveBalanceAdjustment() {
    const form = document.getElementById('adjustBalanceForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const employeeId = parseInt(document.getElementById('adjustEmployee').value);
    const leaveTypeId = document.getElementById('adjustLeaveType').value;
    const adjustmentDays = parseFloat(document.getElementById('adjustmentDays').value);
    const adjustmentType = document.getElementById('adjustmentType').value;
    const reason = document.getElementById('adjustmentReason').value;
    const selectedYear = parseInt(document.getElementById('yearSelect').value);
    
    const balanceIndex = leaveBalances.findIndex(b => 
        b.employeeId === employeeId && 
        b.leaveTypeId === leaveTypeId && 
        b.year === selectedYear
    );
    
    if (balanceIndex !== -1) {
        const balance = leaveBalances[balanceIndex];
        const oldBalance = balance.allocated + balance.carryForward - balance.used;
        
        // Create adjustment record
        const adjustment = {
            id: Date.now(),
            type: adjustmentType,
            days: adjustmentDays,
            reason: reason,
            oldBalance: oldBalance,
            newBalance: 0, // Will be calculated
            createdBy: 'Current User',
            createdAt: new Date().toISOString()
        };
        
        // Apply adjustment
        switch (adjustmentType) {
            case 'add':
                balance.allocated += adjustmentDays;
                break;
            case 'subtract':
                balance.allocated = Math.max(0, balance.allocated - adjustmentDays);
                break;
            case 'set':
                balance.allocated = adjustmentDays + balance.used - balance.carryForward;
                break;
        }
        
        adjustment.newBalance = balance.allocated + balance.carryForward - balance.used;
        
        if (!balance.adjustments) {
            balance.adjustments = [];
        }
        balance.adjustments.push(adjustment);
        balance.lastUpdated = new Date().toISOString();
        
        // Save to localStorage
        localStorage.setItem('leaveBalances', JSON.stringify(leaveBalances));
        
        // Refresh displays
        updateSummaryCards();
        displayEmployeeBalances();
        
        $('#adjustBalanceModal').modal('hide');
        alert('Balance adjustment saved successfully!');
    }
}

function loadBalances() {
    updateSummaryCards();
    displayEmployeeBalances();
}

function searchEmployees() {
    currentPage = 1;
    displayEmployeeBalances();
}

function exportBalances() {
    const selectedYear = parseInt(document.getElementById('yearSelect').value);
    const departmentFilter = document.getElementById('departmentFilter').value;
    
    let filteredEmployees = employees;
    if (departmentFilter) {
        filteredEmployees = employees.filter(emp => emp.department === departmentFilter);
    }
    
    // Create CSV content
    let csvContent = 'Employee,Department,Leave Type,Allocated,Used,Available,Carry Forward\n';
    
    filteredEmployees.forEach(employee => {
        const employeeBalances = leaveBalances.filter(balance => 
            balance.employeeId === employee.id && balance.year === selectedYear
        );
        
        employeeBalances.forEach(balance => {
            const leaveType = leaveTypes.find(type => type.id === balance.leaveTypeId);
            if (leaveType) {
                const available = balance.allocated + balance.carryForward - balance.used;
                csvContent += `"${employee.name}","${employee.department}","${leaveType.name}",${balance.allocated},${balance.used},${available},${balance.carryForward}\n`;
            }
        });
    });
    
    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `leave_balances_${selectedYear}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function showLeaveTypesModal() {
    loadLeaveTypesTable();
    $('#leaveTypesModal').modal('show');
}

function loadLeaveTypesTable() {
    const tbody = document.getElementById('leaveTypesTable');
    tbody.innerHTML = '';
    
    leaveTypes.forEach(type => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${type.name}</td>
            <td>${type.defaultAllocation} days</td>
            <td>${type.maxCarryForward} days</td>
            <td>${type.requiresApproval ? 'Yes' : 'No'}</td>
            <td>
                <button class="btn btn-warning btn-xs mr-1" onclick="editLeaveType('${type.id}')">Edit</button>
                <button class="btn btn-danger btn-xs" onclick="deleteLeaveType('${type.id}')">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function showBulkUpdateModal() {
    // Populate departments for bulk update
    const departments = [...new Set(employees.map(emp => emp.department))];
    const select = document.getElementById('bulkDepartment');
    select.innerHTML = '<option value="">All Departments</option>';
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept;
        option.textContent = dept;
        select.appendChild(option);
    });
    
    $('#bulkUpdateModal').modal('show');
}

function executeBulkUpdate() {
    const form = document.getElementById('bulkUpdateForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const department = document.getElementById('bulkDepartment').value;
    const leaveTypeId = document.getElementById('bulkLeaveType').value;
    const operation = document.getElementById('bulkOperation').value;
    const days = parseFloat(document.getElementById('bulkDays').value);
    const reason = document.getElementById('bulkReason').value;
    const selectedYear = parseInt(document.getElementById('yearSelect').value);
    
    let targetEmployees = employees;
    if (department) {
        targetEmployees = employees.filter(emp => emp.department === department);
    }
    
    if (confirm(`Are you sure you want to ${operation} ${days} days for ${targetEmployees.length} employees?`)) {
        let updatedCount = 0;
        
        targetEmployees.forEach(employee => {
            const balanceIndex = leaveBalances.findIndex(b => 
                b.employeeId === employee.id && 
                b.leaveTypeId === leaveTypeId && 
                b.year === selectedYear
            );
            
            if (balanceIndex !== -1) {
                const balance = leaveBalances[balanceIndex];
                const oldBalance = balance.allocated + balance.carryForward - balance.used;
                
                switch (operation) {
                    case 'add':
                        balance.allocated += days;
                        break;
                    case 'set':
                        balance.allocated = days + balance.used - balance.carryForward;
                        break;
                    case 'reset':
                        const leaveType = leaveTypes.find(type => type.id === leaveTypeId);
                        if (leaveType) {
                            balance.allocated = leaveType.defaultAllocation;
                            balance.used = 0;
                            balance.carryForward = 0;
                        }
                        break;
                }
                
                // Add adjustment record
                const adjustment = {
                    id: Date.now() + employee.id,
                    type: 'bulk_' + operation,
                    days: days,
                    reason: reason,
                    oldBalance: oldBalance,
                    newBalance: balance.allocated + balance.carryForward - balance.used,
                    createdBy: 'Current User',
                    createdAt: new Date().toISOString()
                };
                
                if (!balance.adjustments) {
                    balance.adjustments = [];
                }
                balance.adjustments.push(adjustment);
                balance.lastUpdated = new Date().toISOString();
                
                updatedCount++;
            }
        });
        
        // Save to localStorage
        localStorage.setItem('leaveBalances', JSON.stringify(leaveBalances));
        
        // Refresh displays
        updateSummaryCards();
        displayEmployeeBalances();
        
        $('#bulkUpdateModal').modal('hide');
        alert(`Bulk update completed! ${updatedCount} employee balances updated.`);
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Event listeners for dynamic updates
document.addEventListener('change', function(e) {
    if (e.target.id === 'adjustEmployee' || e.target.id === 'adjustLeaveType') {
        updateCurrentBalance();
    }
});