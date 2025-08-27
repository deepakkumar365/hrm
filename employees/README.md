# Employee Management Module

This module provides comprehensive employee management functionality for the HRM system.

## Features

### 1. Employee List (`index.html`)
- View all employees in a paginated table
- Search employees by name, email, or position
- Filter employees by department
- Quick actions: View, Edit, Delete
- Responsive design with Bootstrap

### 2. Add Employee (`add.html`)
- Complete form for adding new employees
- Form validation (client-side)
- Required fields: First Name, Last Name, Email, Department, Position, Hire Date, Status
- Optional fields: Phone, Salary, Manager, Address, Notes
- Real-time validation feedback

### 3. Edit Employee (`edit.html`)
- Pre-populated form with existing employee data
- Same validation as add form
- Ability to reset changes
- Link to view employee details

### 4. View Employee (`view.html`)
- Detailed employee information display
- Employment statistics (years of service)
- Quick action buttons
- Delete confirmation modal
- Links to related modules (attendance, leaves)

## File Structure

```
employees/
├── index.html          # Employee list page
├── add.html           # Add employee form
├── edit.html          # Edit employee form
├── view.html          # Employee details view
├── js/
│   ├── employees.js   # Main employee list functionality
│   ├── add-employee.js # Add employee form handling
│   ├── edit-employee.js # Edit employee form handling
│   ├── view-employee.js # Employee details display
│   └── api.js         # API simulation (localStorage)
└── README.md          # This file
```

## JavaScript Files

### `employees.js`
- Handles employee list display
- Implements search and filtering
- Manages pagination
- Handles delete operations

### `add-employee.js`
- Form validation for new employees
- Handles form submission
- Phone number formatting
- Manager dropdown population

### `edit-employee.js`
- Pre-populates form with existing data
- Form validation and submission
- Reset functionality
- Links to view page

### `view-employee.js`
- Displays employee details
- Calculates years of service
- Handles delete operations
- Quick action buttons

### `api.js`
- Simulates backend API using localStorage
- CRUD operations for employees
- Search and filtering
- Data validation

## Data Structure

Each employee object contains:

```javascript
{
    id: number,
    firstName: string,
    lastName: string,
    email: string,
    phone: string,
    department: string,
    position: string,
    hireDate: string (YYYY-MM-DD),
    salary: number,
    status: string ('Active', 'Inactive', 'On Leave'),
    manager: string,
    address: string,
    notes: string,
    createdAt: string (ISO date),
    updatedAt: string (ISO date)
}
```

## Usage

1. **Viewing Employees**: Navigate to `employees/index.html`
2. **Adding Employee**: Click "Add New Employee" or navigate to `employees/add.html`
3. **Editing Employee**: Click "Edit" button in employee list or navigate to `employees/edit.html?id=X`
4. **Viewing Details**: Click "View" button in employee list or navigate to `employees/view.html?id=X`

## Navigation

The module is integrated with the main HRM navigation:
- "Manage Employees" → `employees/index.html`
- "Add Employee" → `employees/add.html`

## Features to Implement

For a production system, consider adding:

1. **Backend Integration**
   - Replace localStorage with actual API calls
   - Server-side validation
   - Database storage

2. **Advanced Features**
   - Employee photo upload
   - Document management
   - Bulk operations
   - Export functionality
   - Advanced reporting

3. **Security**
   - Authentication
   - Authorization
   - Input sanitization
   - CSRF protection

4. **Performance**
   - Virtual scrolling for large datasets
   - Caching
   - Lazy loading

## Dependencies

- Bootstrap 4.5.2 (CSS framework)
- jQuery 3.5.1 (for Bootstrap components)
- Custom CSS (`../src/style.css`)

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ features used (arrow functions, template literals, etc.)
- LocalStorage API required for demo functionality