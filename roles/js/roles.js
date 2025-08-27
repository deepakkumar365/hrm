// Roles Management JavaScript
let roles = [];
let filteredRoles = [];
let currentPage = 1;
const itemsPerPage = 10;
let editingRoleId = null;

// Sample data for demonstration
const sampleRoles = [
    {
        id: 1,
        name: "Software Developer",
        description: "Develops and maintains software applications",
        department: "IT",
        level: "Mid",
        employeeCount: 8,
        status: "Active"
    },
    {
        id: 2,
        name: "HR Manager",
        description: "Manages human resources operations and policies",
        department: "HR",
        level: "Manager",
        employeeCount: 2,
        status: "Active"
    },
    {
        id: 3,
        name: "Financial Analyst",
        description: "Analyzes financial data and prepares reports",
        department: "Finance",
        level: "Mid",
        employeeCount: 3,
        status: "Active"
    },
    {
        id: 4,
        name: "Marketing Specialist",
        description: "Develops and executes marketing campaigns",
        department: "Marketing",
        level: "Junior",
        employeeCount: 4,
        status: "Active"
    },
    {
        id: 5,
        name: "Senior Developer",
        description: "Senior software developer with team lead responsibilities",
        department: "IT",
        level: "Senior",
        employeeCount: 3,
        status: "Active"
    },
    {
        id: 6,
        name: "Finance Director",
        description: "Oversees all financial operations",
        department: "Finance",
        level: "Director",
        employeeCount: 1,
        status: "Active"
    },
    {
        id: 7,
        name: "Junior Developer",
        description: "Entry-level software developer",
        department: "IT",
        level: "Junior",
        employeeCount: 0,
        status: "Inactive"
    }
];

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    loadRoles();
    setupEventListeners();
});

// Load roles (in real app, this would be an API call)
function loadRoles() {
    // Simulate API call
    roles = [...sampleRoles];
    filteredRoles = [...roles];
    displayRoles();
    updatePagination();
}

// Setup event listeners
function setupEventListeners() {
    // Search input
    document.getElementById('searchInput').addEventListener('input', debounce(searchRoles, 300));
    
    // Status filter
    document.getElementById('statusFilter').addEventListener('change', searchRoles);
    
    // Delete confirmation
    document.getElementById('confirmDelete').addEventListener('click', confirmDeleteRole);
}

// Display roles in table
function displayRoles() {
    const tbody = document.querySelector('#rolesTable tbody');
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageRoles = filteredRoles.slice(startIndex, endIndex);
    
    tbody.innerHTML = pageRoles.map(role => `
        <tr>
            <td>${role.id}</td>
            <td>${role.name}</td>
            <td>${role.description || '-'}</td>
            <td>${role.department}</td>
            <td><span class="badge badge-info">${role.level}</span></td>
            <td>${role.employeeCount}</td>
            <td><span class="badge badge-${getStatusColor(role.status)}">${role.status}</span></td>
            <td>
                <button class="btn btn-info btn-xs" onclick="viewRole(${role.id})" title="View">View</button>
                <button class="btn btn-warning btn-xs" onclick="editRole(${role.id})" title="Edit">Edit</button>
                <button class="btn btn-danger btn-xs" onclick="showDeleteModal(${role.id})" title="Delete">Delete</button>
            </td>
        </tr>
    `).join('');
}

// Search and filter roles
function searchRoles() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;
    
    filteredRoles = roles.filter(role => {
        const matchesSearch = !searchTerm || 
            role.name.toLowerCase().includes(searchTerm) ||
            role.description.toLowerCase().includes(searchTerm) ||
            role.department.toLowerCase().includes(searchTerm) ||
            role.level.toLowerCase().includes(searchTerm);
            
        const matchesStatus = !statusFilter || role.status === statusFilter;
        
        return matchesSearch && matchesStatus;
    });
    
    currentPage = 1;
    displayRoles();
    updatePagination();
}

// Clear filters
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('statusFilter').value = '';
    filteredRoles = [...roles];
    currentPage = 1;
    displayRoles();
    updatePagination();
}

// Update pagination
function updatePagination() {
    const totalPages = Math.ceil(filteredRoles.length / itemsPerPage);
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
    const totalPages = Math.ceil(filteredRoles.length / itemsPerPage);
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        displayRoles();
        updatePagination();
    }
}

// Show add role modal
function showAddRoleModal() {
    editingRoleId = null;
    document.getElementById('roleModalTitle').textContent = 'Add New Role';
    document.getElementById('roleForm').reset();
    document.getElementById('roleId').value = '';
    document.getElementById('roleStatus').value = 'Active';
    $('#roleModal').modal('show');
}

// View role details
function viewRole(roleId) {
    const role = roles.find(r => r.id === roleId);
    if (role) {
        alert(`Role Details:\n\nName: ${role.name}\nDescription: ${role.description}\nDepartment: ${role.department}\nLevel: ${role.level}\nEmployee Count: ${role.employeeCount}\nStatus: ${role.status}`);
    }
}

// Edit role
function editRole(roleId) {
    const role = roles.find(r => r.id === roleId);
    if (role) {
        editingRoleId = roleId;
        document.getElementById('roleModalTitle').textContent = 'Edit Role';
        document.getElementById('roleId').value = role.id;
        document.getElementById('roleName').value = role.name;
        document.getElementById('roleDescription').value = role.description;
        document.getElementById('roleDepartment').value = role.department;
        document.getElementById('roleLevel').value = role.level;
        document.getElementById('roleStatus').value = role.status;
        $('#roleModal').modal('show');
    }
}

// Save role
function saveRole() {
    const form = document.getElementById('roleForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const roleData = {
        name: document.getElementById('roleName').value,
        description: document.getElementById('roleDescription').value,
        department: document.getElementById('roleDepartment').value,
        level: document.getElementById('roleLevel').value,
        status: document.getElementById('roleStatus').value
    };
    
    if (editingRoleId) {
        // Update existing role
        const roleIndex = roles.findIndex(r => r.id === editingRoleId);
        if (roleIndex !== -1) {
            roles[roleIndex] = { ...roles[roleIndex], ...roleData };
            showNotification('Role updated successfully', 'success');
        }
    } else {
        // Add new role
        const newRole = {
            id: Math.max(...roles.map(r => r.id)) + 1,
            ...roleData,
            employeeCount: 0
        };
        roles.push(newRole);
        showNotification('Role added successfully', 'success');
    }
    
    filteredRoles = [...roles];
    displayRoles();
    updatePagination();
    $('#roleModal').modal('hide');
}

// Show delete modal
function showDeleteModal(roleId) {
    const role = roles.find(r => r.id === roleId);
    if (role) {
        document.getElementById('deleteRoleName').textContent = role.name;
        document.getElementById('deleteRoleEmployeeCount').textContent = role.employeeCount;
        document.getElementById('confirmDelete').setAttribute('data-role-id', roleId);
        $('#deleteModal').modal('show');
    }
}

// Confirm delete role
function confirmDeleteRole() {
    const roleId = parseInt(document.getElementById('confirmDelete').getAttribute('data-role-id'));
    
    // In real app, this would be an API call
    roles = roles.filter(r => r.id !== roleId);
    filteredRoles = filteredRoles.filter(r => r.id !== roleId);
    
    displayRoles();
    updatePagination();
    $('#deleteModal').modal('hide');
    
    // Show success message
    showNotification('Role deleted successfully', 'success');
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