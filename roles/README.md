# Employee Roles Management

This module handles the management of employee roles within the HRM system.

## Features

- **Role Management**: Create, view, edit, and delete employee roles
- **Search & Filter**: Search roles by name, description, department, or level
- **Status Management**: Activate or deactivate roles
- **Employee Tracking**: Track how many employees are assigned to each role

## Files

- `index.html` - Main roles management page
- `js/roles.js` - JavaScript functionality for roles management

## Role Properties

- **Name**: The title of the role (e.g., "Software Developer", "HR Manager")
- **Description**: Detailed description of the role responsibilities
- **Department**: Which department the role belongs to
- **Level**: Career level (Entry, Junior, Mid, Senior, Lead, Manager, Director)
- **Employee Count**: Number of employees currently assigned to this role
- **Status**: Active or Inactive

## Usage

1. Navigate to the Roles page from the Employees dropdown menu
2. Use the search and filter options to find specific roles
3. Click "Add New Role" to create a new role
4. Use the action buttons to view, edit, or delete existing roles

## Sample Data

The system includes sample roles for demonstration:
- Software Developer (IT Department)
- HR Manager (HR Department)
- Financial Analyst (Finance Department)
- Marketing Specialist (Marketing Department)
- And more...

## Integration

This module integrates with:
- Employee management system (for role assignments)
- Department management system (for department filtering)
- Navigation system (accessible via navbar)