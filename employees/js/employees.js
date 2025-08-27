// Employee Management JavaScript
let employees = [];
let filteredEmployees = [];
let currentPage = 1;
const itemsPerPage = 10;

// Sample data for demonstration
const sampleEmployees = [
    {
        id: 1,
        firstName: "John",
        lastName: "Doe",
        email: "john.doe@company.com",
        phone: "+1-555-0123",
        department: "IT",
        position: "Software Developer",
        hireDate: "2023-01-15",
        salary: 75000,
        status: "Active",
        manager: "Jane Smith",
        address: "123 Main St, City, State 12345",
        notes: "Excellent performance in Q1 2024"
    },
    {
        id: 2,
        firstName: "Jane",
        lastName: "Smith",
        email: "jane.smith@company.com",
        phone: "+1-555-0124",
        department: "HR",
        position: "HR Manager",
        hireDate: "2022-03-10",
        salary: 85000,
        status: "Active",
        manager: "",
        address: "456 Oak Ave, City, State 12345",
        notes: "Team lead for HR initiatives"
    },
    {
        id: 3,
        firstName: "Mike",
        lastName: "Johnson",
        email: "mike.johnson@company.com",
        phone: "+1-555-0125",
        department: "Finance",
        position: "Financial Analyst",
        hireDate: "2023-06-20",
        salary: 65000,
        status: "Active",
        manager: "Sarah Wilson",
        address: "789 Pine St, City, State 12345",
        notes: "Recently completed CPA certification"
    },
    {
        id: 4,
        firstName: "Sarah",
        lastName: "Wilson",
        email: "sarah.wilson@company.com",
        phone: "+1-555-0126",
        department: "Finance",
        position: "Finance Director",
        hireDate: "2021-09-05",
        salary: 95000,
        status: "Active",
        manager: "",
        address: "321 Elm St, City, State 12345",
        notes: "Leading digital transformation in finance"
    },
    {
        id: 5,
        firstName: "Tom",
        lastName: "Brown",
        email: "tom.brown@company.com",
        phone: "+1-555-0127",
        department: "Marketing",
        position: "Marketing Specialist",
        hireDate: "2023-11-12",
        salary: 55000,
        status: "On Leave",
        manager: "Lisa Davis",
        address: "654 Maple Ave, City, State 12345",
        notes: "Currently on paternity leave"
    }
];

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    loadEmployees();
    loadDepartmentFilter();
    setupEventListeners();
});

// Load employees (in real app, this would be an API call)
function loadEmployees() {
    // Simulate API call
    employees = [...sampleEmployees];
    filteredEmployees = [...employees];
    displayEmployees();
    updatePagination();
}

// Load department filter options
function loadDepartmentFilter() {
    const departments = [...new Set(employees.map(emp => emp.department))];
    const select = document.getElementById('departmentFilter');
    
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept;
        option.textContent = dept;
        select.appendChild(option);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Search input
    document.getElementById('searchInput').addEventListener('input', debounce(searchEmployees, 300));
    
    // Department filter
    document.getElementById('departmentFilter').addEventListener('change', searchEmployees);
    
    // Delete confirmation
    document.getElementById('confirmDelete').addEventListener('click', confirmDeleteEmployee);
}

// Display employees in table
function displayEmployees() {
    const tbody = document.querySelector('#employeesTable tbody');
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageEmployees = filteredEmployees.slice(startIndex, endIndex);
    
    tbody.innerHTML = pageEmployees.map(emp => `
        <tr>
            <td>${emp.id}</td>
            <td>${emp.firstName} ${emp.lastName}</td>
            <td>${emp.email}</td>
            <td>${emp.department}</td>
            <td>${emp.position}</td>
            <td>${formatDate(emp.hireDate)}</td>
            <td><span class="badge badge-${getStatusColor(emp.status)}">${emp.status}</span></td>
            <td>
                <a href="view.html?id=${emp.id}" class="btn btn-info btn-xs" title="View">View</a>
                <a href="edit.html?id=${emp.id}" class="btn btn-warning btn-xs" title="Edit">Edit</a>
                <button class="btn btn-danger btn-xs" onclick="showDeleteModal(${emp.id})" title="Delete">Delete</button>
            </td>
        </tr>
    `).join('');
}

// Search and filter employees
function searchEmployees() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const departmentFilter = document.getElementById('departmentFilter').value;
    
    filteredEmployees = employees.filter(emp => {
        const matchesSearch = !searchTerm || 
            emp.firstName.toLowerCase().includes(searchTerm) ||
            emp.lastName.toLowerCase().includes(searchTerm) ||
            emp.email.toLowerCase().includes(searchTerm) ||
            emp.position.toLowerCase().includes(searchTerm);
            
        const matchesDepartment = !departmentFilter || emp.department === departmentFilter;
        
        return matchesSearch && matchesDepartment;
    });
    
    currentPage = 1;
    displayEmployees();
    updatePagination();
}

// Clear filters
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('departmentFilter').value = '';
    filteredEmployees = [...employees];
    currentPage = 1;
    displayEmployees();
    updatePagination();
}

// Update pagination
function updatePagination() {
    const totalPages = Math.ceil(filteredEmployees.length / itemsPerPage);
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
    const totalPages = Math.ceil(filteredEmployees.length / itemsPerPage);
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        displayEmployees();
        updatePagination();
    }
}

// Show delete modal
function showDeleteModal(employeeId) {
    const employee = employees.find(emp => emp.id === employeeId);
    if (employee) {
        document.getElementById('deleteEmployeeName').textContent = `${employee.firstName} ${employee.lastName}`;
        document.getElementById('confirmDelete').setAttribute('data-employee-id', employeeId);
        $('#deleteModal').modal('show');
    }
}

// Confirm delete employee
function confirmDeleteEmployee() {
    const employeeId = parseInt(document.getElementById('confirmDelete').getAttribute('data-employee-id'));
    
    // In real app, this would be an API call
    employees = employees.filter(emp => emp.id !== employeeId);
    filteredEmployees = filteredEmployees.filter(emp => emp.id !== employeeId);
    
    displayEmployees();
    updatePagination();
    $('#deleteModal').modal('hide');
    
    // Show success message
    showNotification('Employee deleted successfully', 'success');
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function getStatusColor(status) {
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