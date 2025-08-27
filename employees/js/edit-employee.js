// Edit Employee JavaScript
let currentEmployee = null;

document.addEventListener('DOMContentLoaded', function() {
    loadEmployee();
    loadManagers();
    setupFormValidation();
});

// Load employee data
function loadEmployee() {
    const urlParams = new URLSearchParams(window.location.search);
    const employeeId = urlParams.get('id');
    
    if (!employeeId) {
        showNotification('No employee ID provided', 'error');
        setTimeout(() => window.location.href = 'index.html', 2000);
        return;
    }
    
    // In real app, this would be an API call
    // For demo, using sample data
    const sampleEmployees = [
        {
            id: 1,
            firstName: "John",
            lastName: "Doe",
            email: "john.doe@company.com",
            phone: "(555) 012-3456",
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
            phone: "(555) 012-4567",
            department: "HR",
            position: "HR Manager",
            hireDate: "2022-03-10",
            salary: 85000,
            status: "Active",
            manager: "",
            address: "456 Oak Ave, City, State 12345",
            notes: "Team lead for HR initiatives"
        }
    ];
    
    currentEmployee = sampleEmployees.find(emp => emp.id == employeeId);
    
    if (!currentEmployee) {
        showNotification('Employee not found', 'error');
        setTimeout(() => window.location.href = 'index.html', 2000);
        return;
    }
    
    populateForm();
    updateViewButton();
}

// Populate form with employee data
function populateForm() {
    if (!currentEmployee) return;
    
    document.getElementById('employeeId').value = currentEmployee.id;
    document.getElementById('firstName').value = currentEmployee.firstName;
    document.getElementById('lastName').value = currentEmployee.lastName;
    document.getElementById('email').value = currentEmployee.email;
    document.getElementById('phone').value = currentEmployee.phone;
    document.getElementById('department').value = currentEmployee.department;
    document.getElementById('position').value = currentEmployee.position;
    document.getElementById('hireDate').value = currentEmployee.hireDate;
    document.getElementById('salary').value = currentEmployee.salary;
    document.getElementById('status').value = currentEmployee.status;
    document.getElementById('manager').value = currentEmployee.manager;
    document.getElementById('address').value = currentEmployee.address;
    document.getElementById('notes').value = currentEmployee.notes;
}

// Update view button link
function updateViewButton() {
    const viewBtn = document.getElementById('viewEmployeeBtn');
    if (viewBtn && currentEmployee) {
        viewBtn.href = `view.html?id=${currentEmployee.id}`;
    }
}

// Load managers for the dropdown
function loadManagers() {
    const managers = [
        { id: 1, name: "Jane Smith" },
        { id: 2, name: "Sarah Wilson" },
        { id: 3, name: "Lisa Davis" },
        { id: 4, name: "Robert Johnson" }
    ];
    
    const select = document.getElementById('manager');
    managers.forEach(manager => {
        const option = document.createElement('option');
        option.value = manager.name;
        option.textContent = manager.name;
        select.appendChild(option);
    });
}

// Setup form validation and submission
function setupFormValidation() {
    const form = document.getElementById('editEmployeeForm');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateForm()) {
            submitForm();
        }
    });
    
    // Real-time validation
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', validateField);
        field.addEventListener('input', clearFieldError);
    });
    
    // Email validation
    document.getElementById('email').addEventListener('blur', validateEmail);
    
    // Phone validation
    document.getElementById('phone').addEventListener('input', formatPhone);
    
    // Reset form
    form.addEventListener('reset', function() {
        setTimeout(() => {
            populateForm();
            clearAllErrors();
        }, 10);
    });
}

// Validate individual field
function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    clearFieldError(field);
    return true;
}

// Validate email format
function validateEmail(e) {
    const email = e.target.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        showFieldError(e.target, 'Please enter a valid email address');
        return false;
    }
    
    clearFieldError(e.target);
    return true;
}

// Format phone number
function formatPhone(e) {
    let value = e.target.value.replace(/\D/g, '');
    
    if (value.length >= 6) {
        value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
    } else if (value.length >= 3) {
        value = value.replace(/(\d{3})(\d{0,3})/, '($1) $2');
    }
    
    e.target.value = value;
}

// Validate entire form
function validateForm() {
    let isValid = true;
    const form = document.getElementById('editEmployeeForm');
    
    // Clear previous errors
    clearAllErrors();
    
    // Required fields validation
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        }
    });
    
    // Email validation
    const email = document.getElementById('email').value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (email && !emailRegex.test(email)) {
        showFieldError(document.getElementById('email'), 'Please enter a valid email address');
        isValid = false;
    }
    
    // Salary validation
    const salary = document.getElementById('salary').value;
    if (salary && (isNaN(salary) || parseFloat(salary) < 0)) {
        showFieldError(document.getElementById('salary'), 'Please enter a valid salary amount');
        isValid = false;
    }
    
    // Hire date validation
    const hireDate = new Date(document.getElementById('hireDate').value);
    const today = new Date();
    if (hireDate > today) {
        showFieldError(document.getElementById('hireDate'), 'Hire date cannot be in the future');
        isValid = false;
    }
    
    return isValid;
}

// Submit form
function submitForm() {
    const formData = new FormData(document.getElementById('editEmployeeForm'));
    const employeeData = {};
    
    // Convert FormData to object
    for (let [key, value] of formData.entries()) {
        employeeData[key] = value;
    }
    
    // Keep the original ID
    employeeData.id = parseInt(employeeData.employeeId);
    delete employeeData.employeeId;
    
    // Show loading state
    const submitBtn = document.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Updating Employee...';
    submitBtn.disabled = true;
    
    // Simulate API call
    setTimeout(() => {
        try {
            // In real app, this would be an actual API call
            console.log('Employee data to be updated:', employeeData);
            
            // Update localStorage for demo purposes
            let employees = JSON.parse(localStorage.getItem('employees') || '[]');
            const index = employees.findIndex(emp => emp.id === employeeData.id);
            
            if (index !== -1) {
                employees[index] = { ...employees[index], ...employeeData };
                localStorage.setItem('employees', JSON.stringify(employees));
            }
            
            showNotification('Employee updated successfully!', 'success');
            
            // Update current employee data
            currentEmployee = { ...currentEmployee, ...employeeData };
            
            // Reset button
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
            
        } catch (error) {
            console.error('Error updating employee:', error);
            showNotification('Error updating employee. Please try again.', 'error');
            
            // Reset button
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }, 1000);
}

// Show field error
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

// Clear field error
function clearFieldError(field) {
    if (typeof field === 'object' && field.target) {
        field = field.target;
    }
    
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Clear all errors
function clearAllErrors() {
    const errorFields = document.querySelectorAll('.is-invalid');
    errorFields.forEach(field => {
        field.classList.remove('is-invalid');
    });
    
    const errorMessages = document.querySelectorAll('.invalid-feedback');
    errorMessages.forEach(msg => msg.remove());
}

// Show notification
function showNotification(message, type = 'info') {
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
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}