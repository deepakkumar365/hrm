// Leave Requests Management JavaScript
// Handles leave request creation, approval, and management

let leaveRequests = [];
let employees = [];
let currentRequest = null;
let currentPage = 1;
const itemsPerPage = 10;

// Initialize leave requests management
document.addEventListener('DOMContentLoaded', function() {
    initializeRequestsManagement();
});

function initializeRequestsManagement() {
    loadEmployees();
    loadLeaveRequests();
    setupEventListeners();
    updateSummaryCards();
}

function setupEventListeners() {
    // Search functionality
    document.getElementById('searchRequests').addEventListener('input', function() {
        searchRequests();
    });
    
    // Status change handler
    document.getElementById('requestStatus').addEventListener('change', function() {
        const rejectionGroup = document.getElementById('rejectionReasonGroup');
        if (this.value === 'rejected' || this.value === 'cancelled') {
            rejectionGroup.style.display = 'block';
        } else {
            rejectionGroup.style.display = 'none';
        }
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
            { id: 1, name: 'John Doe', department: 'IT', position: 'Developer', email: 'john.doe@company.com' },
            { id: 2, name: 'Jane Smith', department: 'HR', position: 'Manager', email: 'jane.smith@company.com' },
            { id: 3, name: 'Mike Johnson', department: 'Finance', position: 'Analyst', email: 'mike.johnson@company.com' },
            { id: 4, name: 'Sarah Wilson', department: 'Marketing', position: 'Coordinator', email: 'sarah.wilson@company.com' },
            { id: 5, name: 'David Brown', department: 'IT', position: 'Senior Developer', email: 'david.brown@company.com' }
        ];
    }
    
    populateEmployeeDropdowns();
}

function populateEmployeeDropdowns() {
    const employeeSelects = ['requestEmployee', 'workHandover'];
    
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

function loadLeaveRequests() {
    // Load from localStorage
    const storedRequests = localStorage.getItem('leaveRequests');
    if (storedRequests) {
        leaveRequests = JSON.parse(storedRequests);
    } else {
        // Sample leave requests data
        leaveRequests = [
            {
                id: 1,
                employeeId: 1,
                leaveType: 'annual',
                startDate: '2024-02-15',
                endDate: '2024-02-19',
                totalDays: 5,
                reason: 'Family vacation',
                status: 'pending',
                appliedDate: '2024-01-20',
                emergencyContact: 'Jane Doe - 555-0123',
                workHandover: 2,
                createdAt: new Date().toISOString()
            },
            {
                id: 2,
                employeeId: 2,
                leaveType: 'sick',
                startDate: '2024-01-25',
                endDate: '2024-01-26',
                totalDays: 2,
                reason: 'Medical appointment',
                status: 'approved',
                appliedDate: '2024-01-24',
                approvedBy: 'HR Manager',
                approvedDate: '2024-01-24',
                createdAt: new Date().toISOString()
            },
            {
                id: 3,
                employeeId: 3,
                leaveType: 'personal',
                startDate: '2024-02-01',
                endDate: '2024-02-01',
                totalDays: 1,
                reason: 'Personal matters',
                status: 'rejected',
                appliedDate: '2024-01-30',
                rejectionReason: 'Insufficient notice period',
                rejectedBy: 'Department Manager',
                rejectedDate: '2024-01-31',
                createdAt: new Date().toISOString()
            }
        ];
    }
    
    updateSummaryCards();
    displayRequests();
}

function updateSummaryCards() {
    const today = new Date().toISOString().split('T')[0];
    const currentMonth = new Date().getMonth();
    const currentYear = new Date().getFullYear();
    
    // Count pending requests
    const pendingCount = leaveRequests.filter(req => req.status === 'pending').length;
    
    // Count approved today
    const approvedTodayCount = leaveRequests.filter(req => 
        req.status === 'approved' && 
        req.approvedDate && 
        req.approvedDate.split('T')[0] === today
    ).length;
    
    // Count requests this month
    const monthlyCount = leaveRequests.filter(req => {
        const appliedDate = new Date(req.appliedDate);
        return appliedDate.getMonth() === currentMonth && appliedDate.getFullYear() === currentYear;
    }).length;
    
    // Count employees currently on leave
    const onLeaveCount = leaveRequests.filter(req => {
        if (req.status !== 'approved') return false;
        const startDate = new Date(req.startDate);
        const endDate = new Date(req.endDate);
        const todayDate = new Date(today);
        return todayDate >= startDate && todayDate <= endDate;
    }).length;
    
    document.getElementById('pendingCount').textContent = pendingCount;
    document.getElementById('approvedTodayCount').textContent = approvedTodayCount;
    document.getElementById('monthlyCount').textContent = monthlyCount;
    document.getElementById('onLeaveCount').textContent = onLeaveCount;
}

function displayRequests() {
    const statusFilter = document.getElementById('statusFilter').value;
    const typeFilter = document.getElementById('typeFilter').value;
    const searchTerm = document.getElementById('searchRequests').value.toLowerCase();
    
    let filteredRequests = leaveRequests.filter(req => {
        const employee = employees.find(emp => emp.id === req.employeeId);
        const matchesStatus = !statusFilter || req.status === statusFilter;
        const matchesType = !typeFilter || req.leaveType === typeFilter;
        const matchesSearch = !searchTerm || 
            (employee && employee.name.toLowerCase().includes(searchTerm)) ||
            (employee && employee.department.toLowerCase().includes(searchTerm)) ||
            req.reason.toLowerCase().includes(searchTerm);
        
        return matchesStatus && matchesType && matchesSearch;
    });
    
    // Sort by applied date (newest first)
    filteredRequests.sort((a, b) => new Date(b.appliedDate) - new Date(a.appliedDate));
    
    const tbody = document.querySelector('#requestsTable tbody');
    tbody.innerHTML = '';
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageData = filteredRequests.slice(startIndex, endIndex);
    
    pageData.forEach(req => {
        const employee = employees.find(emp => emp.id === req.employeeId);
        if (!employee) return;
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><input type="checkbox" class="request-checkbox" value="${req.id}"></td>
            <td>LR${req.id.toString().padStart(4, '0')}</td>
            <td>${employee.name}</td>
            <td>${employee.department}</td>
            <td>
                <span class="badge badge-info leave-type-badge">
                    ${getLeaveTypeLabel(req.leaveType)}
                </span>
            </td>
            <td>${formatDate(req.startDate)}</td>
            <td>${formatDate(req.endDate)}</td>
            <td>${req.totalDays}</td>
            <td>
                <span class="badge badge-${getStatusColor(req.status)} leave-badge">
                    ${req.status.toUpperCase()}
                </span>
            </td>
            <td>${formatDate(req.appliedDate)}</td>
            <td>
                <button class="btn btn-info btn-xs mr-1" onclick="viewRequestDetails(${req.id})">View</button>
                <button class="btn btn-warning btn-xs mr-1" onclick="editRequest(${req.id})">Edit</button>
                <button class="btn btn-danger btn-xs" onclick="deleteRequest(${req.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    updatePagination(filteredRequests.length);
}

function getLeaveTypeLabel(type) {
    const labels = {
        'annual': 'Annual',
        'sick': 'Sick',
        'personal': 'Personal',
        'maternity': 'Maternity',
        'emergency': 'Emergency'
    };
    return labels[type] || type;
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

function updatePagination(totalItems) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const pagination = document.getElementById('requestsPagination');
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
    displayRequests();
}

function showAddRequestModal() {
    currentRequest = null;
    document.getElementById('requestModalTitle').textContent = 'New Leave Request';
    document.getElementById('requestForm').reset();
    document.getElementById('requestStatus').value = 'pending';
    document.getElementById('rejectionReasonGroup').style.display = 'none';
    document.getElementById('leaveInfo').style.display = 'none';
    
    // Set default dates
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    document.getElementById('startDate').value = tomorrow.toISOString().split('T')[0];
    document.getElementById('endDate').value = tomorrow.toISOString().split('T')[0];
    
    $('#requestModal').modal('show');
}

function editRequest(requestId) {
    const request = leaveRequests.find(req => req.id === requestId);
    if (!request) return;
    
    currentRequest = request;
    document.getElementById('requestModalTitle').textContent = 'Edit Leave Request';
    
    // Populate form
    document.getElementById('requestEmployee').value = request.employeeId;
    document.getElementById('leaveType').value = request.leaveType;
    document.getElementById('startDate').value = request.startDate;
    document.getElementById('endDate').value = request.endDate;
    document.getElementById('totalDays').value = request.totalDays;
    document.getElementById('leaveReason').value = request.reason;
    document.getElementById('emergencyContact').value = request.emergencyContact || '';
    document.getElementById('workHandover').value = request.workHandover || '';
    document.getElementById('requestStatus').value = request.status;
    document.getElementById('rejectionReason').value = request.rejectionReason || '';
    
    // Show/hide rejection reason
    const rejectionGroup = document.getElementById('rejectionReasonGroup');
    if (request.status === 'rejected' || request.status === 'cancelled') {
        rejectionGroup.style.display = 'block';
    } else {
        rejectionGroup.style.display = 'none';
    }
    
    updateLeaveInfo();
    $('#requestModal').modal('show');
}

function calculateDays() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    if (startDate && endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        if (end >= start) {
            const timeDiff = end.getTime() - start.getTime();
            const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24)) + 1; // Include both start and end dates
            document.getElementById('totalDays').value = daysDiff;
        } else {
            document.getElementById('totalDays').value = 0;
        }
    }
}

function updateLeaveInfo() {
    const employeeId = document.getElementById('requestEmployee').value;
    const leaveType = document.getElementById('leaveType').value;
    const totalDays = parseInt(document.getElementById('totalDays').value) || 0;
    
    if (employeeId && leaveType) {
        // Get employee's leave balance (this would come from the balances system)
        const leaveBalances = getEmployeeLeaveBalance(employeeId, leaveType);
        
        document.getElementById('availableBalance').textContent = leaveBalances.available;
        document.getElementById('usedBalance').textContent = leaveBalances.used;
        document.getElementById('remainingBalance').textContent = Math.max(0, leaveBalances.available - totalDays);
        
        document.getElementById('leaveInfo').style.display = 'block';
    } else {
        document.getElementById('leaveInfo').style.display = 'none';
    }
}

function getEmployeeLeaveBalance(employeeId, leaveType) {
    // This would typically fetch from the leave balances system
    // For now, return sample data
    const defaultBalances = {
        'annual': { available: 20, used: 5 },
        'sick': { available: 10, used: 2 },
        'personal': { available: 5, used: 1 },
        'maternity': { available: 90, used: 0 },
        'emergency': { available: 3, used: 0 }
    };
    
    return defaultBalances[leaveType] || { available: 0, used: 0 };
}

function saveLeaveRequest() {
    const form = document.getElementById('requestForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const requestData = {
        id: currentRequest ? currentRequest.id : Date.now(),
        employeeId: parseInt(document.getElementById('requestEmployee').value),
        leaveType: document.getElementById('leaveType').value,
        startDate: document.getElementById('startDate').value,
        endDate: document.getElementById('endDate').value,
        totalDays: parseInt(document.getElementById('totalDays').value),
        reason: document.getElementById('leaveReason').value,
        emergencyContact: document.getElementById('emergencyContact').value,
        workHandover: parseInt(document.getElementById('workHandover').value) || null,
        status: document.getElementById('requestStatus').value,
        rejectionReason: document.getElementById('rejectionReason').value,
        appliedDate: currentRequest ? currentRequest.appliedDate : new Date().toISOString().split('T')[0],
        createdAt: currentRequest ? currentRequest.createdAt : new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };
    
    // Add approval/rejection metadata
    if (requestData.status === 'approved' && (!currentRequest || currentRequest.status !== 'approved')) {
        requestData.approvedBy = 'Current User'; // Would be actual user
        requestData.approvedDate = new Date().toISOString();
    } else if (requestData.status === 'rejected' && (!currentRequest || currentRequest.status !== 'rejected')) {
        requestData.rejectedBy = 'Current User'; // Would be actual user
        requestData.rejectedDate = new Date().toISOString();
    }
    
    if (currentRequest) {
        // Update existing request
        const index = leaveRequests.findIndex(req => req.id === currentRequest.id);
        if (index !== -1) {
            leaveRequests[index] = requestData;
        }
    } else {
        // Add new request
        leaveRequests.push(requestData);
    }
    
    // Save to localStorage
    localStorage.setItem('leaveRequests', JSON.stringify(leaveRequests));
    
    // Refresh display
    updateSummaryCards();
    displayRequests();
    
    $('#requestModal').modal('hide');
    
    // Show success message
    alert(currentRequest ? 'Leave request updated successfully!' : 'Leave request submitted successfully!');
}

function deleteRequest(requestId) {
    if (confirm('Are you sure you want to delete this leave request?')) {
        leaveRequests = leaveRequests.filter(req => req.id !== requestId);
        localStorage.setItem('leaveRequests', JSON.stringify(leaveRequests));
        
        updateSummaryCards();
        displayRequests();
        
        alert('Leave request deleted successfully!');
    }
}

function viewRequestDetails(requestId) {
    const request = leaveRequests.find(req => req.id === requestId);
    const employee = employees.find(emp => emp.id === request.employeeId);
    const handoverEmployee = request.workHandover ? employees.find(emp => emp.id === request.workHandover) : null;
    
    if (!request || !employee) return;
    
    const detailsContent = document.getElementById('requestDetailsContent');
    detailsContent.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Employee Information</h6>
                <p><strong>Name:</strong> ${employee.name}</p>
                <p><strong>Department:</strong> ${employee.department}</p>
                <p><strong>Position:</strong> ${employee.position}</p>
                <p><strong>Email:</strong> ${employee.email}</p>
            </div>
            <div class="col-md-6">
                <h6>Leave Details</h6>
                <p><strong>Request ID:</strong> LR${request.id.toString().padStart(4, '0')}</p>
                <p><strong>Leave Type:</strong> ${getLeaveTypeLabel(request.leaveType)}</p>
                <p><strong>Status:</strong> <span class="badge badge-${getStatusColor(request.status)}">${request.status.toUpperCase()}</span></p>
                <p><strong>Applied Date:</strong> ${formatDate(request.appliedDate)}</p>
            </div>
        </div>
        <hr>
        <div class="row">
            <div class="col-md-12">
                <h6>Leave Period</h6>
                <p><strong>Start Date:</strong> ${formatDate(request.startDate)}</p>
                <p><strong>End Date:</strong> ${formatDate(request.endDate)}</p>
                <p><strong>Total Days:</strong> ${request.totalDays}</p>
                <p><strong>Reason:</strong> ${request.reason}</p>
                ${request.emergencyContact ? `<p><strong>Emergency Contact:</strong> ${request.emergencyContact}</p>` : ''}
                ${handoverEmployee ? `<p><strong>Work Handover To:</strong> ${handoverEmployee.name}</p>` : ''}
            </div>
        </div>
        ${request.rejectionReason ? `
        <hr>
        <div class="row">
            <div class="col-md-12">
                <h6>Rejection/Cancellation Details</h6>
                <p><strong>Reason:</strong> ${request.rejectionReason}</p>
                ${request.rejectedBy ? `<p><strong>Rejected By:</strong> ${request.rejectedBy}</p>` : ''}
                ${request.rejectedDate ? `<p><strong>Rejected Date:</strong> ${formatDate(request.rejectedDate)}</p>` : ''}
            </div>
        </div>
        ` : ''}
    `;
    
    currentRequest = request;
    $('#requestDetailsModal').modal('show');
}

function approveRequest() {
    if (currentRequest && currentRequest.status === 'pending') {
        currentRequest.status = 'approved';
        currentRequest.approvedBy = 'Current User'; // Would be actual user
        currentRequest.approvedDate = new Date().toISOString();
        
        const index = leaveRequests.findIndex(req => req.id === currentRequest.id);
        if (index !== -1) {
            leaveRequests[index] = currentRequest;
            localStorage.setItem('leaveRequests', JSON.stringify(leaveRequests));
            
            updateSummaryCards();
            displayRequests();
            $('#requestDetailsModal').modal('hide');
            
            alert('Leave request approved successfully!');
        }
    }
}

function rejectRequest() {
    if (currentRequest && currentRequest.status === 'pending') {
        const reason = prompt('Enter reason for rejection:');
        if (reason) {
            currentRequest.status = 'rejected';
            currentRequest.rejectionReason = reason;
            currentRequest.rejectedBy = 'Current User'; // Would be actual user
            currentRequest.rejectedDate = new Date().toISOString();
            
            const index = leaveRequests.findIndex(req => req.id === currentRequest.id);
            if (index !== -1) {
                leaveRequests[index] = currentRequest;
                localStorage.setItem('leaveRequests', JSON.stringify(leaveRequests));
                
                updateSummaryCards();
                displayRequests();
                $('#requestDetailsModal').modal('hide');
                
                alert('Leave request rejected successfully!');
            }
        }
    }
}

function toggleSelectAll() {
    const selectAll = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('.request-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAll.checked;
    });
}

function approveSelected() {
    const selectedIds = Array.from(document.querySelectorAll('.request-checkbox:checked'))
        .map(cb => parseInt(cb.value));
    
    if (selectedIds.length === 0) {
        alert('Please select requests to approve.');
        return;
    }
    
    if (confirm(`Are you sure you want to approve ${selectedIds.length} selected requests?`)) {
        let approvedCount = 0;
        selectedIds.forEach(id => {
            const request = leaveRequests.find(req => req.id === id);
            if (request && request.status === 'pending') {
                request.status = 'approved';
                request.approvedBy = 'Current User';
                request.approvedDate = new Date().toISOString();
                approvedCount++;
            }
        });
        
        if (approvedCount > 0) {
            localStorage.setItem('leaveRequests', JSON.stringify(leaveRequests));
            updateSummaryCards();
            displayRequests();
            alert(`${approvedCount} requests approved successfully!`);
        }
    }
}

function rejectSelected() {
    const selectedIds = Array.from(document.querySelectorAll('.request-checkbox:checked'))
        .map(cb => parseInt(cb.value));
    
    if (selectedIds.length === 0) {
        alert('Please select requests to reject.');
        return;
    }
    
    const reason = prompt('Enter reason for rejection:');
    if (reason && confirm(`Are you sure you want to reject ${selectedIds.length} selected requests?`)) {
        let rejectedCount = 0;
        selectedIds.forEach(id => {
            const request = leaveRequests.find(req => req.id === id);
            if (request && request.status === 'pending') {
                request.status = 'rejected';
                request.rejectionReason = reason;
                request.rejectedBy = 'Current User';
                request.rejectedDate = new Date().toISOString();
                rejectedCount++;
            }
        });
        
        if (rejectedCount > 0) {
            localStorage.setItem('leaveRequests', JSON.stringify(leaveRequests));
            updateSummaryCards();
            displayRequests();
            alert(`${rejectedCount} requests rejected successfully!`);
        }
    }
}

function filterRequests() {
    currentPage = 1;
    displayRequests();
}

function searchRequests() {
    currentPage = 1;
    displayRequests();
}

function exportRequests() {
    const statusFilter = document.getElementById('statusFilter').value;
    const typeFilter = document.getElementById('typeFilter').value;
    
    let filteredRequests = leaveRequests.filter(req => {
        const matchesStatus = !statusFilter || req.status === statusFilter;
        const matchesType = !typeFilter || req.leaveType === typeFilter;
        return matchesStatus && matchesType;
    });
    
    if (filteredRequests.length === 0) {
        alert('No requests found to export.');
        return;
    }
    
    // Create CSV content
    let csvContent = 'Request ID,Employee,Department,Leave Type,Start Date,End Date,Days,Status,Applied Date,Reason\n';
    
    filteredRequests.forEach(req => {
        const employee = employees.find(emp => emp.id === req.employeeId);
        if (employee) {
            csvContent += `LR${req.id.toString().padStart(4, '0')},"${employee.name}","${employee.department}","${getLeaveTypeLabel(req.leaveType)}","${req.startDate}","${req.endDate}",${req.totalDays},"${req.status}","${req.appliedDate}","${req.reason}"\n`;
        }
    });
    
    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `leave_requests_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function sendReminders() {
    const pendingRequests = leaveRequests.filter(req => req.status === 'pending');
    
    if (pendingRequests.length === 0) {
        alert('No pending requests found.');
        return;
    }
    
    // In a real application, this would send actual email reminders
    alert(`Reminder emails sent for ${pendingRequests.length} pending requests.`);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}