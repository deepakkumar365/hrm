// Dynamic Navbar JavaScript
// This script dynamically adjusts navbar paths based on current location

function loadNavbar() {
    // Determine the base path based on current location
    const currentPath = window.location.pathname;
    
    // Check if we're in a subfolder (employees, attendance, etc.)
    const pathSegments = currentPath.split('/').filter(segment => segment);
    const isInSubfolder = pathSegments.length > 1 && pathSegments[pathSegments.length - 2] !== 'HRM';
    const basePath = isInSubfolder ? '../' : '';
    
    // Determine active page for highlighting
    const currentPage = pathSegments[pathSegments.length - 1] || 'dashboard.html';
    const isEmployeePage = currentPath.includes('/employees/') || currentPath.includes('/roles/') || currentPath.includes('/departments/');
    const isAttendancePage = currentPath.includes('attendance');
    const isLeavePage = currentPath.includes('leave');
    
    const navbarHTML = `
        <div class="navbar-container">
            <nav class="win-toolbar navbar navbar-expand-lg navbar-light">
                <div class="container-fluid">
                    <a class="navbar-brand" href="${basePath}dashboard.html">HRM</a>
                    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav mr-auto">
                            <li class="nav-item ${currentPage === 'dashboard.html' ? 'active' : ''}">
                                <a class="nav-link" href="${basePath}dashboard.html">Dashboard</a>
                            </li>
                            
                            <li class="nav-item dropdown ${isEmployeePage ? 'active' : ''}">
                                <a class="nav-link dropdown-toggle" href="#" data-toggle="dropdown">Employees</a>
                                <div class="dropdown-menu">
                                    <a class="dropdown-item" href="${basePath}employees/index.html">Manage Employees</a>
                                    <a class="dropdown-item" href="${basePath}employees/add.html">Add Employee</a>
                                    <a class="dropdown-item" href="${basePath}roles/index.html">Roles</a>
                                    <a class="dropdown-item" href="${basePath}departments/index.html">Departments</a>
                                </div>
                            </li>
                            
                            <li class="nav-item dropdown ${isAttendancePage ? 'active' : ''}">
                                <a class="nav-link dropdown-toggle" href="#" data-toggle="dropdown">Attendance</a>
                                <div class="dropdown-menu">
                                    <a class="dropdown-item" href="${basePath}attendance/daily.html">Daily</a>
                                    <a class="dropdown-item" href="${basePath}attendance/monthly.html">Monthly</a>
                                    <a class="dropdown-item" href="${basePath}attendance/overtime.html">Overtime</a>
                                </div>
                            </li>
                            
                            <li class="nav-item dropdown ${isLeavePage ? 'active' : ''}">
                                <a class="nav-link dropdown-toggle" href="#" data-toggle="dropdown">Leaves</a>
                                <div class="dropdown-menu">
                                    <a class="dropdown-item" href="${basePath}leaves/requests.html">Requests</a>
                                    <a class="dropdown-item" href="${basePath}leaves/balances.html">Balances</a>
                                </div>
                            </li>
                        </ul>
                        <a href="${basePath}login.html" class="btn btn-outline-primary btn-xs">Logout</a>
                    </div>
                </div>
            </nav>
        </div>
    `;
    
    const navbarElement = document.getElementById('navbar');
    if (navbarElement) {
        navbarElement.innerHTML = navbarHTML;
    }
}

// Load navbar when DOM is ready
document.addEventListener('DOMContentLoaded', loadNavbar);