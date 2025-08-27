# HRM (Human Resource Management) System

A web-based Human Resource Management system built with HTML, CSS, and JavaScript.

## Getting Started

This project uses shared HTML components (like the navigation bar) that require a local HTTP server to function properly due to browser CORS restrictions.

### Prerequisites

- Python 3.x (usually pre-installed on most systems)
- A modern web browser (Chrome, Firefox, Safari, Edge)

### Running the Application

1. **Start the Local Server**
   
   Open a terminal/command prompt in the project directory and run:
   ```bash
   python -m http.server 8000
   ```
   
   You should see output like:
   ```
   Serving HTTP on :: port 8000 (http://[::]:8000/) ...
   ```

2. **Access the Application**
   
   Open your web browser and navigate to:
   ```
   http://localhost:8000
   ```
   
   Or directly access specific pages:
   - Dashboard: `http://localhost:8000/dashboard.html`
   - Employees: `http://localhost:8000/employees/index.html`
   - Roles: `http://localhost:8000/roles/index.html`
   - Departments: `http://localhost:8000/departments/index.html`
   - Login: `http://localhost:8000/index.html`

3. **Stop the Server**
   
   Press `Ctrl+C` in the terminal to stop the server when you're done.

### Alternative Server Options

If Python is not available, you can use other simple HTTP servers:

**Node.js (if installed):**
```bash
npx http-server -p 8000
```

**PHP (if installed):**
```bash
php -S localhost:8000
```

**Live Server Extension (VS Code):**
- Install the "Live Server" extension in VS Code
- Right-click on any HTML file and select "Open with Live Server"

## Project Structure

```
HRM/
├── dashboard.html      # Main dashboard page
├── index.html         # Landing/login page
├── navbar.html        # Shared navigation component
├── employees/         # Employee management module
│   ├── index.html     # Employee listing page
│   ├── add.html       # Add employee page
│   ├── edit.html      # Edit employee page
│   ├── view.html      # View employee details
│   ├── js/            # Employee-related JavaScript files
│   └── README.md      # Employee module documentation
├── roles/             # Employee roles management module
│   ├── index.html     # Roles management page
│   ├── js/
│   │   └── roles.js   # Roles management functionality
│   └── README.md      # Roles module documentation
├── departments/       # Departments management module
│   ├── index.html     # Departments management page
│   ├── js/
│   │   └── departments.js # Departments management functionality
│   └── README.md      # Departments module documentation
├── js/                # Shared JavaScript files
│   ├── navbar.js      # Navigation functionality
│   └── dashboard.js   # Dashboard functionality
├── src/
│   └── style.css      # Main stylesheet
└── README.md          # This file
```

## Features

- **Dashboard**: Overview and quick stats with charts and analytics
- **Employee Management**: Complete CRUD operations for employee records
- **Roles Management**: Define and manage employee roles with levels and departments
- **Departments Management**: Organize departments with managers and budgets
- **Attendance Tracking**: Daily and monthly attendance views (planned)
- **Leave Management**: Handle leave requests and balances (planned)
- **Responsive Design**: Works on desktop and mobile devices
- **Modular Architecture**: Organized by feature modules for maintainability

## Technical Notes

- The application uses Bootstrap 4.5.2 for styling and responsive layout
- Navigation bar is loaded dynamically using JavaScript fetch API
- All pages share the same navigation component for consistency
- Custom styles are defined in `src/style.css`

## Troubleshooting

**Navigation bar not loading?**
- Make sure you're accessing the site via HTTP server (http://localhost:8000) and not opening files directly in the browser
- Check browser console for any error messages

**Server won't start?**
- Make sure port 8000 is not already in use
- Try a different port: `python -m http.server 3000`

**Page styling looks broken?**
- Ensure you have an internet connection (Bootstrap CSS is loaded from CDN)
- Check that `src/style.css` exists and is accessible

## Development

To modify the navigation bar, edit `navbar.html`. Changes will be reflected across all pages that include it.

For styling changes, modify `src/style.css`.

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+