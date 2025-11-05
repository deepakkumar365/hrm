/**
 * Common Form Validation Framework
 * Provides real-time validation feedback and error toaster notifications
 * Works across all forms with class 'needs-validation'
 */

class FormValidationFramework {
    constructor() {
        this.validationRules = {};
        this.errorMessages = {};
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupAllForms();
            this.setupRealTimeValidation();
        });
    }

    /**
     * Setup all forms with needs-validation class
     */
    setupAllForms() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e, form));
        });
    }

    /**
     * Setup real-time field validation
     */
    setupRealTimeValidation() {
        const fields = document.querySelectorAll('input[required], select[required], textarea[required]');
        fields.forEach(field => {
            // Validate on blur
            field.addEventListener('blur', () => this.validateField(field));
            
            // Clear error state on input
            field.addEventListener('input', () => {
                field.classList.remove('is-invalid');
                this.removeFieldError(field);
            });

            field.addEventListener('change', () => {
                field.classList.remove('is-invalid');
                this.removeFieldError(field);
            });
        });
    }

    /**
     * Handle form submission with validation
     */
    handleFormSubmit(e, form) {
        e.preventDefault();
        e.stopPropagation();

        // Validate all fields
        const errors = this.validateForm(form);

        if (errors.length > 0) {
            // Show validation errors as toaster
            this.showValidationErrors(errors);
            
            // Mark invalid fields
            errors.forEach(error => {
                const field = form.querySelector(`[name="${error.field}"]`);
                if (field) {
                    field.classList.add('is-invalid');
                }
            });

            // Scroll to first invalid field
            const firstInvalidField = form.querySelector('.is-invalid');
            if (firstInvalidField) {
                firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstInvalidField.focus();
            }

            return false;
        }

        // Form is valid, allow submission
        form.classList.add('was-validated');
        this.showProcessingState(form);
        form.submit();
    }

    /**
     * Validate all required fields in form
     */
    validateForm(form) {
        const errors = [];
        const fields = form.querySelectorAll('input[required], select[required], textarea[required]');

        fields.forEach(field => {
            const error = this.validateField(field);
            if (error) {
                errors.push(error);
            }
        });

        return errors;
    }

    /**
     * Validate individual field
     */
    validateField(field) {
        const fieldName = this.getFieldLabel(field);
        const value = field.value.trim();
        const type = field.type.toLowerCase();

        // Check if field is required
        if (!field.hasAttribute('required')) {
            return null;
        }

        // Empty value validation
        if (!value) {
            field.classList.add('is-invalid');
            return {
                field: field.name,
                message: `${fieldName} is required`,
                type: 'required'
            };
        }

        // Email validation
        if (type === 'email' && value) {
            if (!this.isValidEmail(value)) {
                field.classList.add('is-invalid');
                return {
                    field: field.name,
                    message: `Please enter a valid ${fieldName}`,
                    type: 'email'
                };
            }
        }

        // Phone validation
        if (type === 'tel' && value) {
            if (!this.isValidPhone(value)) {
                field.classList.add('is-invalid');
                return {
                    field: field.name,
                    message: `Please enter a valid ${fieldName}`,
                    type: 'phone'
                };
            }
        }

        // Date validation
        if (type === 'date' && value) {
            if (!this.isValidDate(value)) {
                field.classList.add('is-invalid');
                return {
                    field: field.name,
                    message: `Please enter a valid ${fieldName}`,
                    type: 'date'
                };
            }
        }

        // Number validation
        if ((type === 'number' || type === 'range') && value) {
            if (isNaN(value)) {
                field.classList.add('is-invalid');
                return {
                    field: field.name,
                    message: `${fieldName} must be a valid number`,
                    type: 'number'
                };
            }

            // Check min/max
            if (field.hasAttribute('min') && parseFloat(value) < parseFloat(field.getAttribute('min'))) {
                field.classList.add('is-invalid');
                return {
                    field: field.name,
                    message: `${fieldName} must be at least ${field.getAttribute('min')}`,
                    type: 'min'
                };
            }

            if (field.hasAttribute('max') && parseFloat(value) > parseFloat(field.getAttribute('max'))) {
                field.classList.add('is-invalid');
                return {
                    field: field.name,
                    message: `${fieldName} must not exceed ${field.getAttribute('max')}`,
                    type: 'max'
                };
            }
        }

        // Length validation
        if (field.hasAttribute('minlength') && value.length < parseInt(field.getAttribute('minlength'))) {
            field.classList.add('is-invalid');
            return {
                field: field.name,
                message: `${fieldName} must be at least ${field.getAttribute('minlength')} characters`,
                type: 'minlength'
            };
        }

        if (field.hasAttribute('maxlength') && value.length > parseInt(field.getAttribute('maxlength'))) {
            field.classList.add('is-invalid');
            return {
                field: field.name,
                message: `${fieldName} must not exceed ${field.getAttribute('maxlength')} characters`,
                type: 'maxlength'
            };
        }

        // Pattern validation (regex)
        if (field.hasAttribute('pattern') && value && !new RegExp(field.getAttribute('pattern')).test(value)) {
            field.classList.add('is-invalid');
            return {
                field: field.name,
                message: `${fieldName} format is invalid`,
                type: 'pattern'
            };
        }

        // Clear validation state
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        return null;
    }

    /**
     * Show validation errors as toaster notification
     */
    showValidationErrors(errors) {
        if (errors.length === 0) return;

        // Group errors for better readability
        const errorMessages = errors.map(err => `• ${err.message}`).join('<br>');

        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-danger border-0 validation-error-toast';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body p-3">
                    <div class="d-flex align-items-start gap-2">
                        <i class="fas fa-exclamation-circle me-2 mt-1 flex-shrink-0"></i>
                        <div class="flex-grow-1">
                            <strong>Please fix the following errors:</strong>
                            <div class="mt-2 small" style="line-height: 1.6;">
                                ${errorMessages}
                            </div>
                        </div>
                    </div>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        const container = this.getToastContainer();
        container.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    /**
     * Show success notification
     */
    showSuccessNotification(message) {
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-success border-0';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-check-circle me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        const container = this.getToastContainer();
        container.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    /**
     * Get or create toast container
     */
    getToastContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        return container;
    }

    /**
     * Get user-friendly field label
     */
    getFieldLabel(field) {
        // Try to get label from associated <label> element
        const labelElement = document.querySelector(`label[for="${field.id}"]`);
        if (labelElement) {
            return labelElement.textContent.trim().replace(/\s*\*\s*$/g, '').trim();
        }

        // Use placeholder or data attribute
        if (field.placeholder) {
            return field.placeholder;
        }

        if (field.dataset.label) {
            return field.dataset.label;
        }

        // Fallback to field name with formatting
        return field.name
            .replace(/_/g, ' ')
            .replace(/([A-Z])/g, ' $1')
            .trim()
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    /**
     * Remove field error state
     */
    removeFieldError(field) {
        field.classList.remove('is-invalid');
    }

    /**
     * Validation helper functions
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidPhone(phone) {
        // Remove common formatting characters
        const cleaned = phone.replace(/[\s\-\(\)\.+]/g, '');
        // Accept 7-15 digit phone numbers
        return /^\d{7,15}$/.test(cleaned);
    }

    isValidDate(dateString) {
        const date = new Date(dateString);
        return date instanceof Date && !isNaN(date);
    }

    /**
     * Show processing state on submit button
     */
    showProcessingState(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';

            // Reset after 10 seconds (fallback)
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }, 10000);
        }
    }
}

// Initialize the validation framework when DOM is ready
let formValidation;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        formValidation = new FormValidationFramework();
    });
} else {
    formValidation = new FormValidationFramework();
}