// Dashboard JavaScript
let departmentChart = null;
let attendanceChart = null;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

// Initialize all dashboard components
function initializeDashboard() {
    updateDateTime();
    loadSummaryData();
    loadCharts();
    loadRecentActivities();
    loadUpcomingEvents();
    loadSystemNotifications();
    loadBirthdaysAndAnniversaries();
    
    // Update time every minute
    setInterval(updateDateTime, 60000);
}

// Update current date and time
function updateDateTime() {
    const now = new Date();
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    document.getElementById('currentDateTime').textContent = now.toLocaleDateString('en-US', options);
}

// Load summary statistics
function loadSummaryData() {
    // Simulate API call to get summary data
    setTimeout(() => {
        const summaryData = {
            totalEmployees: 47,
            employeeGrowth: '+3 this month',
            presentToday: 42,
            attendanceRate: '89.4%',
            onLeave: 3,
            leaveRequests: '2 pending',
            totalDepartments: 6
        };
        
        // Update summary cards
        document.getElementById('totalEmployees').textContent = summaryData.totalEmployees;
        document.getElementById('employeeGrowth').textContent = summaryData.employeeGrowth;
        document.getElementById('presentToday').textContent = summaryData.presentToday;
        document.getElementById('attendanceRate').textContent = summaryData.attendanceRate;
        document.getElementById('onLeave').textContent = summaryData.onLeave;
        document.getElementById('leaveRequests').textContent = summaryData.leaveRequests;
        document.getElementById('totalDepartments').textContent = summaryData.totalDepartments;
    }, 500);
}

// Load and create charts
function loadCharts() {
    createDepartmentChart();
    createAttendanceChart();
}

// Destroy existing charts before creating new ones
function destroyCharts() {
    if (departmentChart) {
        departmentChart.destroy();
        departmentChart = null;
    }
    if (attendanceChart) {
        attendanceChart.destroy();
        attendanceChart = null;
    }
    
    // Clear canvas elements to reset their size
    const departmentCanvas = document.getElementById('departmentChart');
    const attendanceCanvas = document.getElementById('attendanceChart');
    
    if (departmentCanvas) {
        departmentCanvas.style.width = '';
        departmentCanvas.style.height = '';
        departmentCanvas.width = departmentCanvas.offsetWidth;
        departmentCanvas.height = departmentCanvas.offsetHeight;
    }
    
    if (attendanceCanvas) {
        attendanceCanvas.style.width = '';
        attendanceCanvas.style.height = '';
        attendanceCanvas.width = attendanceCanvas.offsetWidth;
        attendanceCanvas.height = attendanceCanvas.offsetHeight;
    }
}

// Create department distribution chart
function createDepartmentChart() {
    // Destroy existing chart if it exists
    if (departmentChart) {
        departmentChart.destroy();
    }
    
    const ctx = document.getElementById('departmentChart').getContext('2d');
    
    const departmentData = {
        labels: ['IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Sales'],
        datasets: [{
            label: 'Employees',
            data: [12, 8, 9, 6, 7, 5],
            backgroundColor: [
                '#007bff',
                '#28a745',
                '#ffc107',
                '#dc3545',
                '#6f42c1',
                '#fd7e14'
            ],
            borderWidth: 1
        }]
    };
    
    departmentChart = new Chart(ctx, {
        type: 'bar',
        data: departmentData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 2
                    }
                }
            }
        }
    });
}

// Create attendance overview chart
function createAttendanceChart() {
    // Destroy existing chart if it exists
    if (attendanceChart) {
        attendanceChart.destroy();
    }
    
    const ctx = document.getElementById('attendanceChart').getContext('2d');
    
    const attendanceData = {
        labels: ['Present', 'Absent', 'On Leave'],
        datasets: [{
            data: [42, 2, 3],
            backgroundColor: ['#28a745', '#dc3545', '#ffc107'],
            borderWidth: 1
        }]
    };
    
    attendanceChart = new Chart(ctx, {
        type: 'doughnut',
        data: attendanceData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 10,
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

// Load recent activities
function loadRecentActivities() {
    setTimeout(() => {
        const activities = [
            {
                type: 'success',
                message: 'John Doe checked in at 9:15 AM',
                time: '15 minutes ago'
            },
            {
                type: 'info',
                message: 'New employee Sarah Wilson added',
                time: '2 hours ago'
            },
            {
                type: 'warning',
                message: 'Leave request from Mike Johnson',
                time: '3 hours ago'
            },
            {
                type: 'primary',
                message: 'Monthly report generated',
                time: '1 day ago'
            },
            {
                type: 'success',
                message: 'Payroll processed successfully',
                time: '2 days ago'
            }
        ];
        
        const container = document.getElementById('recentActivities');
        container.innerHTML = activities.map(activity => `
            <div class="d-flex align-items-start mb-2">
                <div class="bg-${activity.type} rounded-circle p-1 mr-2 mt-1" style="width: 8px; height: 8px;"></div>
                <div class="flex-grow-1">
                    <small class="d-block">${activity.message}</small>
                    <small class="text-muted">${activity.time}</small>
                </div>
            </div>
        `).join('');
    }, 700);
}

// Load upcoming events
function loadUpcomingEvents() {
    setTimeout(() => {
        const events = [
            {
                title: 'Team Building Event',
                date: 'Tomorrow, 2:00 PM',
                type: 'primary'
            },
            {
                title: 'Monthly All-Hands Meeting',
                date: 'Friday, 10:00 AM',
                type: 'info'
            },
            {
                title: 'Performance Review Deadline',
                date: 'Next Monday',
                type: 'warning'
            },
            {
                title: 'Company Holiday - Independence Day',
                date: 'July 4th',
                type: 'success'
            }
        ];
        
        const container = document.getElementById('upcomingEvents');
        container.innerHTML = events.map(event => `
            <div class="border-left border-${event.type} pl-3 mb-2">
                <small class="d-block font-weight-bold">${event.title}</small>
                <small class="text-muted">${event.date}</small>
            </div>
        `).join('');
    }, 900);
}

// Load system notifications
function loadSystemNotifications() {
    setTimeout(() => {
        const notifications = [
            {
                type: 'info',
                message: 'System maintenance scheduled for this weekend'
            },
            {
                type: 'warning',
                message: '3 employees have pending document submissions'
            },
            {
                type: 'success',
                message: 'Backup completed successfully'
            }
        ];
        
        const container = document.getElementById('systemNotifications');
        container.innerHTML = notifications.map(notification => `
            <div class="alert alert-${notification.type} alert-sm py-2 px-3 mb-2">
                <small>${notification.message}</small>
            </div>
        `).join('');
    }, 1100);
}

// Load birthdays and anniversaries
function loadBirthdaysAndAnniversaries() {
    setTimeout(() => {
        // Today's birthdays
        const birthdays = [
            {
                name: 'Emily Johnson',
                department: 'Marketing',
                age: 28
            }
        ];
        
        // Work anniversaries
        const anniversaries = [
            {
                name: 'Robert Smith',
                department: 'IT',
                years: 5
            },
            {
                name: 'Lisa Davis',
                department: 'HR',
                years: 3
            }
        ];
        
        // Update birthdays
        const birthdayContainer = document.getElementById('todayBirthdays');
        if (birthdays.length > 0) {
            birthdayContainer.innerHTML = birthdays.map(person => `
                <div class="d-flex align-items-center mb-2">
                    <div class="bg-warning rounded-circle d-flex align-items-center justify-content-center mr-3" style="width: 40px; height: 40px;">
                        <i class="fas fa-birthday-cake text-white"></i>
                    </div>
                    <div>
                        <small class="d-block font-weight-bold">${person.name}</small>
                        <small class="text-muted">${person.department} • ${person.age} years old</small>
                    </div>
                </div>
            `).join('');
        } else {
            birthdayContainer.innerHTML = '<p class="text-muted text-center">No birthdays today</p>';
        }
        
        // Update anniversaries
        const anniversaryContainer = document.getElementById('workAnniversaries');
        if (anniversaries.length > 0) {
            anniversaryContainer.innerHTML = anniversaries.map(person => `
                <div class="d-flex align-items-center mb-2">
                    <div class="bg-success rounded-circle d-flex align-items-center justify-content-center mr-3" style="width: 40px; height: 40px;">
                        <i class="fas fa-award text-white"></i>
                    </div>
                    <div>
                        <small class="d-block font-weight-bold">${person.name}</small>
                        <small class="text-muted">${person.department} • ${person.years} years</small>
                    </div>
                </div>
            `).join('');
        } else {
            anniversaryContainer.innerHTML = '<p class="text-muted text-center">No anniversaries today</p>';
        }
    }, 1300);
}

// Refresh dashboard data
function refreshDashboard() {
    // Show loading state
    const refreshBtn = document.querySelector('button[onclick="refreshDashboard()"]');
    const originalHTML = refreshBtn.innerHTML;
    refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
    refreshBtn.disabled = true;
    
    // Simulate refresh delay
    setTimeout(() => {
        // Destroy existing charts before refreshing
        destroyCharts();
        
        // Reload all dashboard components
        loadSummaryData();
        loadCharts(); // This will recreate the charts
        loadRecentActivities();
        loadUpcomingEvents();
        loadSystemNotifications();
        loadBirthdaysAndAnniversaries();
        
        // Reset button
        refreshBtn.innerHTML = originalHTML;
        refreshBtn.disabled = false;
        
        // Show success message
        showNotification('Dashboard refreshed successfully!', 'success');
    }, 1500);
}

// Quick action functions
function markAttendance() {
    showNotification('Attendance marking feature coming soon!', 'info');
}

function generateReport() {
    showNotification('Generating comprehensive report...', 'info');
    
    setTimeout(() => {
        showNotification('Report generated successfully!', 'success');
    }, 2000);
}

function generatePayslips() {
    showNotification('Redirecting to employee management for payslip generation...', 'info');
    
    setTimeout(() => {
        showNotification('Select an employee to generate their payslip', 'info');
        window.location.href = 'employees/index.html';
    }, 1000);
}

// Utility function to show notifications
function showNotification(message, type = 'info') {
    const alertClass = type === 'success' ? 'alert-success' : 
                     type === 'error' ? 'alert-danger' : 
                     type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 80px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert">&times;</button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 4000);
}