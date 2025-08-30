/**
 * Singapore HRM System - Mobile-First JavaScript
 * Progressive Web App functionality and mobile optimizations
 */

class HRMApp {
    constructor() {
        this.isOnline = navigator.onLine;
        this.version = '1.0.0';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeServiceWorker();
        this.setupOfflineCapabilities();
        this.initializeMobileOptimizations();
        this.setupAttendanceFeatures();
        this.initializeNotifications();
        console.log('HRM System initialized');
    }

    setupEventListeners() {
        // Network status monitoring
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.showNotification('Connection restored', 'success');
            this.syncOfflineData();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showNotification('Working offline', 'warning');
        });

        // Touch and gesture optimizations
        document.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
        document.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: true });

        // Form enhancements
        document.addEventListener('DOMContentLoaded', () => {
            this.enhanceForms();
            this.setupMobileNavigation();
            this.initializeQuickActions();
        });

        // Prevent zoom on form focus (iOS)
        document.querySelectorAll('input, select, textarea').forEach(input => {
            input.addEventListener('focus', () => {
                if (window.DeviceMotionEvent && /iPhone|iPad|iPod/.test(navigator.userAgent)) {
                    input.style.fontSize = '16px';
                }
            });
        });
    }

    initializeServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('Service Worker registered:', registration);
                    
                    // Check for updates
                    registration.addEventListener('updatefound', () => {
                        const newWorker = registration.installing;
                        newWorker.addEventListener('statechange', () => {
                            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                this.showUpdateNotification();
                            }
                        });
                    });
                })
                .catch(error => console.log('Service Worker registration failed:', error));
        }
    }

    setupOfflineCapabilities() {
        // Cache critical data for offline use
        this.offlineStorage = {
            attendance: this.getFromStorage('attendance_cache') || [],
            employees: this.getFromStorage('employee_cache') || [],
            leaves: this.getFromStorage('leave_cache') || []
        };

        // Sync button for manual sync
        this.createSyncButton();
    }

    initializeMobileOptimizations() {
        // Viewport height fix for mobile browsers
        this.setViewportHeight();
        window.addEventListener('resize', this.setViewportHeight.bind(this));
        window.addEventListener('orientationchange', () => {
            setTimeout(this.setViewportHeight.bind(this), 100);
        });

        // Mobile-friendly data tables
        this.enhanceDataTables();

        // Touch-friendly dropdowns
        this.enhanceDropdowns();

        // Mobile search optimization
        this.setupMobileSearch();
    }

    setupAttendanceFeatures() {
        // Geolocation for attendance
        this.setupGeolocation();

        // Quick attendance actions
        this.setupQuickAttendance();

        // Offline attendance storage
        this.attendanceQueue = this.getFromStorage('attendance_queue') || [];
    }

    initializeNotifications() {
        // Request notification permission
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }

        // Setup notification handlers
        this.setupNotificationHandlers();
    }

    // Mobile Navigation
    setupMobileNavigation() {
        const navbar = document.querySelector('.navbar');
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');

        if (navbarToggler && navbarCollapse) {
            // Close mobile menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!navbar.contains(e.target) && navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            });

            // Close mobile menu when selecting item
            navbarCollapse.querySelectorAll('.nav-link').forEach(link => {
                link.addEventListener('click', () => {
                    if (navbarCollapse.classList.contains('show')) {
                        navbarToggler.click();
                    }
                });
            });
        }

        // Add scroll behavior for navbar
        let lastScrollTop = 0;
        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                // Scrolling down
                navbar.style.transform = 'translateY(-100%)';
            } else {
                // Scrolling up
                navbar.style.transform = 'translateY(0)';
            }
            lastScrollTop = scrollTop;
        }, { passive: true });
    }

    // Quick Actions Setup
    initializeQuickActions() {
        const quickActionBtn = document.querySelector('[data-bs-toggle="dropdown"]');
        if (quickActionBtn) {
            // Add haptic feedback for supported devices
            quickActionBtn.addEventListener('click', () => {
                if (navigator.vibrate) {
                    navigator.vibrate(50);
                }
            });
        }

        // Setup quick action handlers
        this.setupQuickActionHandlers();
    }

    setupQuickActionHandlers() {
        // Quick attendance marking
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="quick-attendance"]')) {
                this.handleQuickAttendance();
            }
        });

        // Quick leave request
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="quick-leave"]')) {
                this.handleQuickLeave();
            }
        });

        // Quick claim submission
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="quick-claim"]')) {
                this.handleQuickClaim();
            }
        });
    }

    // Geolocation Services
    setupGeolocation() {
        this.geolocation = {
            options: {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000 // 5 minutes
            },
            
            getCurrentPosition: () => {
                return new Promise((resolve, reject) => {
                    if (!navigator.geolocation) {
                        reject(new Error('Geolocation not supported'));
                        return;
                    }
                    
                    navigator.geolocation.getCurrentPosition(resolve, reject, this.geolocation.options);
                });
            }
        };
    }

    async getLocationForAttendance() {
        try {
            const position = await this.geolocation.getCurrentPosition();
            return {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy
            };
        } catch (error) {
            console.warn('Geolocation failed:', error.message);
            return null;
        }
    }

    // Attendance Functions
    setupQuickAttendance() {
        const attendanceBtn = document.getElementById('quickAttendanceBtn');
        if (attendanceBtn) {
            attendanceBtn.addEventListener('click', this.handleQuickAttendance.bind(this));
        }
    }

    async handleQuickAttendance() {
        const location = await this.getLocationForAttendance();
        
        // Get current attendance status
        try {
            const response = await fetch('/api/attendance/check');
            const status = await response.json();
            
            let action = 'clock_in';
            if (status.clocked_in && !status.clocked_out) {
                action = 'clock_out';
            }
            
            this.markAttendance(action, location);
            
        } catch (error) {
            if (!this.isOnline) {
                // Store for offline sync
                this.storeOfflineAttendance({
                    action: 'clock_in',
                    location: location,
                    timestamp: new Date().toISOString()
                });
                this.showNotification('Attendance saved offline', 'info');
            }
        }
    }

    async markAttendance(action, location) {
        const data = {
            action: action,
            latitude: location?.latitude,
            longitude: location?.longitude
        };

        try {
            const response = await fetch('/attendance/mark', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams(data)
            });

            if (response.ok) {
                this.showNotification(`Successfully ${action.replace('_', ' ')}`, 'success');
                // Update UI
                this.updateAttendanceStatus();
            } else {
                throw new Error('Network response was not ok');
            }
        } catch (error) {
            console.error('Attendance marking failed:', error);
            this.showNotification('Failed to mark attendance', 'error');
        }
    }

    storeOfflineAttendance(attendanceData) {
        this.attendanceQueue.push(attendanceData);
        this.saveToStorage('attendance_queue', this.attendanceQueue);
    }

    async syncOfflineData() {
        if (this.attendanceQueue.length > 0) {
            for (const attendance of this.attendanceQueue) {
                try {
                    await this.markAttendance(attendance.action, attendance.location);
                } catch (error) {
                    console.error('Failed to sync attendance:', error);
                }
            }
            
            // Clear queue after successful sync
            this.attendanceQueue = [];
            this.saveToStorage('attendance_queue', []);
            this.showNotification('Offline data synced successfully', 'success');
        }
    }

    // Form Enhancements
    enhanceForms() {
        // Add loading states to form submissions
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
                    
                    // Re-enable after timeout (fallback)
                    setTimeout(() => {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalText;
                    }, 10000);
                }
            });
        });

        // Enhanced validation
        this.setupFormValidation();

        // Auto-save drafts
        this.setupAutoSave();
    }

    setupFormValidation() {
        // Real-time validation
        document.querySelectorAll('.needs-validation').forEach(form => {
            form.addEventListener('input', (e) => {
                if (e.target.matches('input, select, textarea')) {
                    this.validateField(e.target);
                }
            });
        });
    }

    validateField(field) {
        const isValid = field.checkValidity();
        field.classList.toggle('is-valid', isValid);
        field.classList.toggle('is-invalid', !isValid);
        
        // Show custom feedback
        const feedback = field.parentNode.querySelector('.invalid-feedback');
        if (feedback && !isValid) {
            feedback.style.display = 'block';
        } else if (feedback) {
            feedback.style.display = 'none';
        }
    }

    setupAutoSave() {
        const autoSaveForms = document.querySelectorAll('[data-autosave]');
        autoSaveForms.forEach(form => {
            const formId = form.id || form.dataset.autosave;
            
            // Load saved data
            const savedData = this.getFromStorage(`form_${formId}`);
            if (savedData) {
                this.populateForm(form, savedData);
            }
            
            // Save on input
            form.addEventListener('input', this.debounce(() => {
                const formData = new FormData(form);
                this.saveToStorage(`form_${formId}`, Object.fromEntries(formData));
            }, 1000));
        });
    }

    populateForm(form, data) {
        Object.keys(data).forEach(key => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field) {
                field.value = data[key];
            }
        });
    }

    // Data Table Enhancements
    enhanceDataTables() {
        // Convert tables to mobile-friendly cards on small screens
        const tables = document.querySelectorAll('.table-responsive table');
        tables.forEach(table => {
            if (window.innerWidth < 768) {
                this.convertTableToCards(table);
            }
        });

        // Add data labels for mobile view
        this.addDataLabels();
    }

    convertTableToCards(table) {
        const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            cells.forEach((cell, index) => {
                if (headers[index]) {
                    cell.setAttribute('data-label', headers[index]);
                }
            });
        });
    }

    addDataLabels() {
        document.querySelectorAll('.table-responsive td').forEach(cell => {
            const header = cell.closest('table').querySelector(`thead th:nth-child(${cell.cellIndex + 1})`);
            if (header) {
                cell.setAttribute('data-label', header.textContent.trim());
            }
        });
    }

    // Search Functionality
    setupMobileSearch() {
        const searchInputs = document.querySelectorAll('input[type="search"], .mobile-search input');
        searchInputs.forEach(input => {
            // Add search icon
            if (!input.parentNode.querySelector('.search-icon')) {
                const icon = document.createElement('i');
                icon.className = 'fas fa-search search-icon';
                input.parentNode.insertBefore(icon, input);
                input.parentNode.classList.add('mobile-search');
            }

            // Add real-time search
            input.addEventListener('input', this.debounce((e) => {
                this.performSearch(e.target.value, e.target.dataset.target);
            }, 300));
        });
    }

    performSearch(query, target) {
        if (!target) return;
        
        const targetElements = document.querySelectorAll(target);
        targetElements.forEach(element => {
            const text = element.textContent.toLowerCase();
            const match = text.includes(query.toLowerCase());
            element.style.display = match ? '' : 'none';
        });
    }

    // Dropdown Enhancements
    enhanceDropdowns() {
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            // Add touch-friendly spacing
            menu.classList.add('mobile-friendly');
            
            // Close on item selection
            menu.addEventListener('click', (e) => {
                if (e.target.matches('.dropdown-item')) {
                    const dropdown = bootstrap.Dropdown.getInstance(menu.previousElementSibling);
                    if (dropdown) {
                        dropdown.hide();
                    }
                }
            });
        });
    }

    // Notification System
    showNotification(message, type = 'info', duration = 3000) {
        // Check if we can show browser notifications
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('HRM System', {
                body: message,
                icon: '/static/icon-192.png'
            });
        }

        // Show toast notification
        this.showToast(message, type, duration);
    }

    showToast(message, type, duration) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${this.getIconForType(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        const container = this.getToastContainer();
        container.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast, { delay: duration });
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    getToastContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
        }
        return container;
    }

    getIconForType(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    setupNotificationHandlers() {
        // Handle push notifications when app is in background
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.addEventListener('message', event => {
                if (event.data && event.data.type === 'notification') {
                    this.showNotification(event.data.message, event.data.messageType);
                }
            });
        }
    }

    showUpdateNotification() {
        const updateBanner = document.createElement('div');
        updateBanner.className = 'alert alert-info alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
        updateBanner.style.zIndex = '9999';
        updateBanner.innerHTML = `
            <i class="fas fa-download me-2"></i>
            A new version is available!
            <button type="button" class="btn btn-sm btn-outline-info ms-2" onclick="window.location.reload()">
                Update Now
            </button>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(updateBanner);
    }

    // Touch Handlers
    handleTouchStart(e) {
        this.touchStartY = e.touches[0].clientY;
        this.touchStartTime = Date.now();
    }

    handleTouchMove(e) {
        if (!this.touchStartY) return;

        const touchY = e.touches[0].clientY;
        const touchDiff = this.touchStartY - touchY;

        // Pull to refresh implementation
        if (touchDiff < -100 && window.pageYOffset === 0) {
            this.triggerPullToRefresh();
        }
    }

    triggerPullToRefresh() {
        if (this.refreshing) return;
        
        this.refreshing = true;
        this.showNotification('Refreshing...', 'info');
        
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    }

    // Utility Functions
    setViewportHeight() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    createSyncButton() {
        if (!this.isOnline && !document.querySelector('#syncButton')) {
            const syncBtn = document.createElement('button');
            syncBtn.id = 'syncButton';
            syncBtn.className = 'btn btn-warning position-fixed bottom-0 start-50 translate-middle-x mb-3';
            syncBtn.innerHTML = '<i class="fas fa-sync me-1"></i>Sync Offline Data';
            syncBtn.addEventListener('click', () => this.syncOfflineData());
            document.body.appendChild(syncBtn);
        }
    }

    updateAttendanceStatus() {
        // Refresh attendance status display
        fetch('/api/attendance/check')
            .then(response => response.json())
            .then(data => {
                const statusElements = document.querySelectorAll('.attendance-status');
                statusElements.forEach(element => {
                    this.updateAttendanceDisplay(element, data);
                });
            })
            .catch(error => console.error('Failed to update attendance status:', error));
    }

    updateAttendanceDisplay(element, data) {
        // Update attendance display based on current status
        if (data.clocked_in && !data.clocked_out) {
            element.classList.add('clocked-in');
            element.querySelector('.status-text').textContent = `Clocked in at ${data.clock_in_time}`;
        } else if (data.clocked_out) {
            element.classList.add('completed');
            element.querySelector('.status-text').textContent = 'Day completed';
        }
    }

    // Storage Utilities
    saveToStorage(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
        } catch (error) {
            console.warn('Failed to save to localStorage:', error);
        }
    }

    getFromStorage(key) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.warn('Failed to read from localStorage:', error);
            return null;
        }
    }

    debounce(func, wait) {
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

    // Quick Action Handlers
    handleQuickLeave() {
        window.location.href = '/leave/request';
    }

    handleQuickClaim() {
        window.location.href = '/claims/submit';
    }
}

// Initialize the application
const hrmApp = new HRMApp();

// Export for global access
window.HRMApp = hrmApp;

// Additional utility functions for templates
window.HRMUtils = {
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('en-SG', {
            style: 'currency',
            currency: 'SGD'
        }).format(amount);
    },

    formatDate: (date) => {
        return new Intl.DateTimeFormat('en-SG', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        }).format(new Date(date));
    },

    formatTime: (time) => {
        return new Intl.DateTimeFormat('en-SG', {
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(time));
    },

    showConfirm: (message) => {
        return new Promise((resolve) => {
            const result = confirm(message);
            resolve(result);
        });
    },

    vibrate: (pattern = 50) => {
        if (navigator.vibrate) {
            navigator.vibrate(pattern);
        }
    }
};
