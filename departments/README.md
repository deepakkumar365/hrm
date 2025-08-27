# Departments Management

This module handles the management of organizational departments within the HRM system.

## Features

- **Department Management**: Create, view, edit, and delete departments
- **Search & Filter**: Search departments by name, description, manager, or location
- **Manager Assignment**: Assign managers to departments
- **Budget Tracking**: Track annual budgets for each department
- **Employee Tracking**: Monitor employee count per department
- **Status Management**: Activate or deactivate departments

## Files

- `index.html` - Main departments management page
- `js/departments.js` - JavaScript functionality for departments management

## Department Properties

- **Name**: The name of the department (e.g., "Information Technology", "Human Resources")
- **Description**: Detailed description of the department's purpose and responsibilities
- **Manager**: The assigned department manager
- **Employee Count**: Number of employees in the department
- **Budget**: Annual budget allocation
- **Location**: Physical location of the department
- **Status**: Active or Inactive

## Usage

1. Navigate to the Departments page from the Employees dropdown menu
2. Use the search and filter options to find specific departments
3. Click "Add New Department" to create a new department
4. Use the action buttons to view, edit, or delete existing departments

## Sample Data

The system includes sample departments for demonstration:
- Information Technology (12 employees, $500,000 budget)
- Human Resources (5 employees, $200,000 budget)
- Finance (8 employees, $300,000 budget)
- Marketing (6 employees, $250,000 budget)
- Operations (10 employees, $400,000 budget)
- Research & Development (Inactive department)

## Manager Assignment

- Managers can be selected from a dropdown list of available employees
- Each department can have only one manager
- Managers are displayed in the department listing

## Budget Management

- Budgets are displayed in a formatted currency format
- Budget information is used for financial planning and reporting
- Departments without assigned budgets show $0

## Integration

This module integrates with:
- Employee management system (for manager assignments and employee counts)
- Role management system (for department-based role filtering)
- Navigation system (accessible via navbar)
- Financial reporting systems (for budget tracking)