// Departments Management JavaScript
let departments = [];
let filteredDepartments = [];
let currentPage = 1;
const itemsPerPage = 10;
let editingDepartmentId = null;

// Sample data for demonstration
const sampleDepartments = [
    {
        id: 1,
        name: "Information Technology",
        description: "Manages all IT infrastructure, software development, and technical support",
        manager: "Jane Smith",
        managerId: 2,
        employeeCount: 12,
        budget: 500000,
        location: "Building A, Floor 3",
        status: "Active"
    },
    {
        id: 2,
        name: "Human Resources",
        description: "Handles recruitment, employee relations, and HR policies",
        manager: "John Doe",
        managerId: 1,
        employeeCount: 5,
        budget: 200000,
        location: "Building B, Floor 1",
        status: "Active"
    },
    {
        id: 3,
        name: "Finance",
        description: "Manages financial planning, accounting, and budgeting",
        manager: "Sarah Wilson",
        managerId: 4,
        employeeCount: 8,
        budget: 300000,
        location: "Building A, Floor 2",
        status: "Active"
    },
    {
        id: 4,
        name: "Marketing",
        description: "Develops marketing strategies and manages brand communications",
        manager: "Mike Johnson",
        managerId: 3,
        employeeCount: 6,
        budget: 250000,
        location: "Building B, Floor 2",
        status: "Active"
    },
    {
        id: 5,
        name: "Operations",
        description: "Oversees daily operations and process improvements",
        manager: "Lisa Davis",
        managerId: 5,
        employeeCount: 10,
        budget: 400000,
        location: "Building A, Floor 1",
        status: "Active"
    },
    {
        id: 6,
        name: "Research & Development",
        description: "Focuses on innovation and new product development",
        manager: "",
        managerId: null,
        employeeCount: 0,
        budget: 150000,
        location: "Building C, Floor 1",
        status: "Inactive"
    }
];

// Sample managers for dropdown
const sampleManagers = [
    { id: 1, name: "John Doe" },
    { id: 2, name: "Jane Smith" },
    { id: 3, name: "Mike Johnson" },
    { id: 4, name: "Sarah Wilson" },
    { id: 5, name: "Lisa Davis" },
    { id: 6, name: "Tom Brown" },
    { id: 7, name: "Emily Chen" }
];

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    loadDepartments();
    loadManagers();
    setupEventListeners();
});

// Load departments (in real app, this would be an API call)
function loadDepartments() {
    // Simulate API call
    departments = [...sampleDepartments];
    filteredDepartments = [...departments];
    displayDepartments();
    updatePagination();
}

// Load managers for dropdown
function loadManagers() {
    const select = document.getElementById('departmentManager');
    
    sampleManagers.forEach(manager => {
        const option = document.createElement('option');
        option.value = manager.id;
        option.textContent = manager.name;
        select.appendChild(option);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Search input
    document.getElementById('searchInput').addEventListener('input', debounce(searchDepartments, 300));
    
    // Status filter
    document.getElementById('statusFilter').addEventListener('change', searchDepartments);
    
    // Delete confirmation
    document.getElementById('confirmDelete').addEventListener('click', confirmDeleteDepartment);
}

// Display departments in table
function displayDepartments() {
    const tbody = document.querySelector('#departmentsTable tbody');
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageDepartments = filteredDepartments.slice(startIndex, endIndex);
    
    tbody.innerHTML = pageDepartments.map(dept => `
        <tr>
            <td>${dept.id}</td>
            <td>${dept.name}</td>
            <td>${dept.description || '-'}</td>
            <td>${dept.manager || 'Not Assigned'}</td>
            <td>${dept.employeeCount}</td>
            <td>$${dept.budget ? dept.budget.toLocaleString() : '0'}</td>
            <td><span class="badge badge-${getStatusColor(dept.status)}">${dept.status}</span></td>
            <td>
                <button class="btn btn-info btn-xs" onclick="viewDepartment(${dept.id})" title="View">View</button>
                <button class="btn btn-warning btn-xs" onclick="editDepartment(${dept.id})" title="Edit">Edit</button>
                <button class="btn btn-danger btn-xs" onclick="showDeleteModal(${dept.id})" title="Delete">Delete</button>
            </td>
        </tr>
    `).join('');
}

// Search and filter departments
function searchDepartments() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;
    
    filteredDepartments = departments.filter(dept => {
        const matchesSearch = !searchTerm || 
            dept.name.toLowerCase().includes(searchTerm) ||
            dept.description.toLowerCase().includes(searchTerm) ||
            dept.manager.toLowerCase().includes(searchTerm) ||
            dept.location.toLowerCase().includes(searchTerm);
            
        const matchesStatus = !statusFilter || dept.status === statusFilter;
        
        return matchesSearch && matchesStatus;
    });
    
    currentPage = 1;
    displayDepartments();
    updatePagination();
}

// Clear filters
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('statusFilter').value = '';
    filteredDepartments = [...departments];
    currentPage = 1;
    displayDepartments();
    updatePagination();
}

// Update pagination
function updatePagination() {
    const totalPages = Math.ceil(filteredDepartments.length / itemsPerPage);
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
    const totalPages = Math.ceil(filteredDepartments.length / itemsPerPage);
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        displayDepartments();
        updatePagination();
    }
}

// Show add department modal
function showAddDepartmentModal() {
    editingDepartmentId = null;
    document.getElementById('departmentModalTitle').textContent = 'Add New Department';
    document.getElementById('departmentForm').reset();
    document.getElementById('departmentId').value = '';
    document.getElementById('departmentStatus').value = 'Active';
    $('#departmentModal').modal('show');
}

// View department details
function viewDepartment(departmentId) {
    const dept = departments.find(d => d.id === departmentId);
    if (dept) {
        alert(`Department Details:\n\nName: ${dept.name}\nDescription: ${dept.description}\nManager: ${dept.manager || 'Not Assigned'}\nEmployee Count: ${dept.employeeCount}\nBudget: $${dept.budget ? dept.budget.toLocaleString() : '0'}\nLocation: ${dept.location}\nStatus: ${dept.status}`);
    }
}

// Edit department
function editDepartment(departmentId) {
    const dept = departments.find(d => d.id === departmentId);
    if (dept) {
        editingDepartmentId = departmentId;
        document.getElementById('departmentModalTitle').textContent = 'Edit Department';
        document.getElementById('departmentId').value = dept.id;
        document.getElementById('departmentName').value = dept.name;
        document.getElementById('departmentDescription').value = dept.description;
        document.getElementById('departmentManager').value = dept.managerId || '';
        document.getElementById('departmentBudget').value = dept.budget || '';
        document.getElementById('departmentLocation').value = dept.location || '';
        document.getElementById('departmentStatus').value = dept.status;
        $('#departmentModal').modal('show');
    }
}

// Save department
function saveDepartment() {
    const form = document.getElementById('departmentForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const managerId = document.getElementById('departmentManager').value;
    const managerName = managerId ? sampleManagers.find(m => m.id == managerId)?.name || '' : '';
    
    const departmentData = {
        name: document.getElementById('departmentName').value,
        description: document.getElementById('departmentDescription').value,
        managerId: managerId ? parseInt(managerId) : null,
        manager: managerName,
        budget: parseInt(document.getElementById('departmentBudget').value) || 0,
        location: document.getElementById('departmentLocation').value,
        status: document.getElementById('departmentStatus').value
    };
    
    if (editingDepartmentId) {
        // Update existing department
        const deptIndex = departments.findIndex(d => d.id === editingDepartmentId);
        if (deptIndex !== -1) {
            departments[deptIndex] = { ...departments[deptIndex], ...departmentData };
            showNotification('Department updated successfully', 'success');
        }
    } else {
        // Add new department
        const newDepartment = {
            id: Math.max(...departments.map(d => d.id)) + 1,
            ...departmentData,
            employeeCount: 0
        };
        departments.push(newDepartment);
        showNotification('Department added successfully', 'success');
    }
    
    filteredDepartments = [...departments];
    displayDepartments();
    updatePagination();
    $('#departmentModal').modal('hide');
}

// Show delete modal
function showDeleteModal(departmentId) {
    const dept = departments.find(d => d.id === departmentId);
    if (dept) {
        document.getElementById('deleteDepartmentName').textContent = dept.name;
        document.getElementById('deleteDepartmentEmployeeCount').textContent = dept.employeeCount;
        document.getElementById('confirmDelete').setAttribute('data-department-id', departmentId);
        $('#deleteModal').modal('show');
    }
}

// Confirm delete department
function confirmDeleteDepartment() {
    const departmentId = parseInt(document.getElementById('confirmDelete').getAttribute('data-department-id'));
    
    // In real app, this would be an API call
    departments = departments.filter(d => d.id !== departmentId);
    filteredDepartments = filteredDepartments.filter(d => d.id !== departmentId);
    
    displayDepartments();
    updatePagination();
    $('#deleteModal').modal('hide');
    
    // Show success message
    showNotification('Department deleted successfully', 'success');
}

// Utility functions
function getStatusColor(status) {
    switch (status) {
        case 'Active': return 'success';
        case 'Inactive': return 'secondary';
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
    // Simple notification - in real app, you might use a toast library
    const alertClass = type === 'success' ? 'alert-success' : 
                     type === 'error' ? 'alert-danger' : 'alert-info';
    
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