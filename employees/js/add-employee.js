// Add Employee JavaScript
document.addEventListener('DOMContentLoaded', function() {
    loadManagers();
    setupFormValidation();
    setDefaultValues();
});

// Load managers for the dropdown
function loadManagers() {
    // In real app, this would be an API call to get managers
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

// Set default values
function setDefaultValues() {
    // Set hire date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('hireDate').value = today;
    
    // Set default status
    document.getElementById('status').value = 'Active';
}

// Setup form validation and submission
function setupFormValidation() {
    const form = document.getElementById('addEmployeeForm');
    
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
    const form = document.getElementById('addEmployeeForm');
    
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
    const formData = new FormData(document.getElementById('addEmployeeForm'));
    const employeeData = {};
    
    // Convert FormData to object
    for (let [key, value] of formData.entries()) {
        employeeData[key] = value;
    }
    
    // Generate new ID (in real app, this would be handled by the backend)
    employeeData.id = Date.now();
    
    // Show loading state
    const submitBtn = document.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Adding Employee...';
    submitBtn.disabled = true;
    
    // Simulate API call
    setTimeout(() => {
        try {
            // In real app, this would be an actual API call
            console.log('Employee data to be saved:', employeeData);
            
            // Save to localStorage for demo purposes
            let employees = JSON.parse(localStorage.getItem('employees') || '[]');
            employees.push(employeeData);
            localStorage.setItem('employees', JSON.stringify(employees));
            
            showNotification('Employee added successfully!', 'success');
            
            // Redirect to employee list after a short delay
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1500);
            
        } catch (error) {
            console.error('Error adding employee:', error);
            showNotification('Error adding employee. Please try again.', 'error');
            
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