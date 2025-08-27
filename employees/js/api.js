// Employee API Simulation
// This file simulates backend API calls using localStorage for demo purposes
// In a real application, these would be actual HTTP requests to your backend

class EmployeeAPI {
    constructor() {
        this.storageKey = 'hrm_employees';
        this.initializeSampleData();
    }

    // Initialize with sample data if no data exists
    initializeSampleData() {
        const existingData = localStorage.getItem(this.storageKey);
        if (!existingData) {
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
                    notes: "Excellent performance in Q1 2024",
                    createdAt: "2023-01-15T09:00:00Z",
                    updatedAt: "2024-01-15T10:30:00Z"
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
                    notes: "Team lead for HR initiatives",
                    createdAt: "2022-03-10T09:00:00Z",
                    updatedAt: "2024-01-10T14:20:00Z"
                },
                {
                    id: 3,
                    firstName: "Mike",
                    lastName: "Johnson",
                    email: "mike.johnson@company.com",
                    phone: "(555) 012-5678",
                    department: "Finance",
                    position: "Financial Analyst",
                    hireDate: "2023-06-20",
                    salary: 65000,
                    status: "Active",
                    manager: "Sarah Wilson",
                    address: "789 Pine St, City, State 12345",
                    notes: "Recently completed CPA certification",
                    createdAt: "2023-06-20T09:00:00Z",
                    updatedAt: "2024-01-12T11:15:00Z"
                },
                {
                    id: 4,
                    firstName: "Sarah",
                    lastName: "Wilson",
                    email: "sarah.wilson@company.com",
                    phone: "(555) 012-6789",
                    department: "Finance",
                    position: "Finance Director",
                    hireDate: "2021-09-05",
                    salary: 95000,
                    status: "Active",
                    manager: "",
                    address: "321 Elm St, City, State 12345",
                    notes: "Leading digital transformation in finance",
                    createdAt: "2021-09-05T09:00:00Z",
                    updatedAt: "2024-01-08T16:45:00Z"
                },
                {
                    id: 5,
                    firstName: "Tom",
                    lastName: "Brown",
                    email: "tom.brown@company.com",
                    phone: "(555) 012-7890",
                    department: "Marketing",
                    position: "Marketing Specialist",
                    hireDate: "2023-11-12",
                    salary: 55000,
                    status: "On Leave",
                    manager: "Lisa Davis",
                    address: "654 Maple Ave, City, State 12345",
                    notes: "Currently on paternity leave",
                    createdAt: "2023-11-12T09:00:00Z",
                    updatedAt: "2024-01-05T13:30:00Z"
                }
            ];
            
            localStorage.setItem(this.storageKey, JSON.stringify(sampleEmployees));
        }
    }

    // Get all employees
    async getAllEmployees() {
        return new Promise((resolve) => {
            setTimeout(() => {
                const employees = JSON.parse(localStorage.getItem(this.storageKey) || '[]');
                resolve({
                    success: true,
                    data: employees,
                    total: employees.length
                });
            }, 300); // Simulate network delay
        });
    }

    // Get employee by ID
    async getEmployeeById(id) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                const employees = JSON.parse(localStorage.getItem(this.storageKey) || '[]');
                const employee = employees.find(emp => emp.id == id);
                
                if (employee) {
                    resolve({
                        success: true,
                        data: employee
                    });
                } else {
                    reject({
                        success: false,
                        error: 'Employee not found'
                    });
                }
            }, 200);
        });
    }

    // Create new employee
    async createEmployee(employeeData) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                try {
                    const employees = JSON.parse(localStorage.getItem(this.storageKey) || '[]');
                    
                    // Generate new ID
                    const newId = Math.max(...employees.map(emp => emp.id), 0) + 1;
                    
                    // Create new employee object
                    const newEmployee = {
                        ...employeeData,
                        id: newId,
                        createdAt: new Date().toISOString(),
                        updatedAt: new Date().toISOString()
                    };
                    
                    // Validate required fields
                    const requiredFields = ['firstName', 'lastName', 'email', 'department', 'position', 'hireDate', 'status'];
                    const missingFields = requiredFields.filter(field => !newEmployee[field]);
                    
                    if (missingFields.length > 0) {
                        reject({
                            success: false,
                            error: `Missing required fields: ${missingFields.join(', ')}`
                        });
                        return;
                    }
                    
                    // Check for duplicate email
                    const existingEmployee = employees.find(emp => emp.email === newEmployee.email);
                    if (existingEmployee) {
                        reject({
                            success: false,
                            error: 'Employee with this email already exists'
                        });
                        return;
                    }
                    
                    employees.push(newEmployee);
                    localStorage.setItem(this.storageKey, JSON.stringify(employees));
                    
                    resolve({
                        success: true,
                        data: newEmployee,
                        message: 'Employee created successfully'
                    });
                } catch (error) {
                    reject({
                        success: false,
                        error: 'Failed to create employee'
                    });
                }
            }, 500);
        });
    }

    // Update employee
    async updateEmployee(id, employeeData) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                try {
                    const employees = JSON.parse(localStorage.getItem(this.storageKey) || '[]');
                    const index = employees.findIndex(emp => emp.id == id);
                    
                    if (index === -1) {
                        reject({
                            success: false,
                            error: 'Employee not found'
                        });
                        return;
                    }
                    
                    // Check for duplicate email (excluding current employee)
                    const existingEmployee = employees.find(emp => emp.email === employeeData.email && emp.id != id);
                    if (existingEmployee) {
                        reject({
                            success: false,
                            error: 'Another employee with this email already exists'
                        });
                        return;
                    }
                    
                    // Update employee
                    employees[index] = {
                        ...employees[index],
                        ...employeeData,
                        id: parseInt(id), // Ensure ID remains the same
                        updatedAt: new Date().toISOString()
                    };
                    
                    localStorage.setItem(this.storageKey, JSON.stringify(employees));
                    
                    resolve({
                        success: true,
                        data: employees[index],
                        message: 'Employee updated successfully'
                    });
                } catch (error) {
                    reject({
                        success: false,
                        error: 'Failed to update employee'
                    });
                }
            }, 400);
        });
    }

    // Delete employee
    async deleteEmployee(id) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                try {
                    const employees = JSON.parse(localStorage.getItem(this.storageKey) || '[]');
                    const index = employees.findIndex(emp => emp.id == id);
                    
                    if (index === -1) {
                        reject({
                            success: false,
                            error: 'Employee not found'
                        });
                        return;
                    }
                    
                    const deletedEmployee = employees[index];
                    employees.splice(index, 1);
                    localStorage.setItem(this.storageKey, JSON.stringify(employees));
                    
                    resolve({
                        success: true,
                        data: deletedEmployee,
                        message: 'Employee deleted successfully'
                    });
                } catch (error) {
                    reject({
                        success: false,
                        error: 'Failed to delete employee'
                    });
                }
            }, 300);
        });
    }

    // Search employees
    async searchEmployees(searchParams) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const employees = JSON.parse(localStorage.getItem(this.storageKey) || '[]');
                let filteredEmployees = [...employees];
                
                // Apply search filters
                if (searchParams.search) {
                    const searchTerm = searchParams.search.toLowerCase();
                    filteredEmployees = filteredEmployees.filter(emp =>
                        emp.firstName.toLowerCase().includes(searchTerm) ||
                        emp.lastName.toLowerCase().includes(searchTerm) ||
                        emp.email.toLowerCase().includes(searchTerm) ||
                        emp.position.toLowerCase().includes(searchTerm)
                    );
                }
                
                if (searchParams.department) {
                    filteredEmployees = filteredEmployees.filter(emp =>
                        emp.department === searchParams.department
                    );
                }
                
                if (searchParams.status) {
                    filteredEmployees = filteredEmployees.filter(emp =>
                        emp.status === searchParams.status
                    );
                }
                
                // Apply pagination
                const page = parseInt(searchParams.page) || 1;
                const limit = parseInt(searchParams.limit) || 10;
                const startIndex = (page - 1) * limit;
                const endIndex = startIndex + limit;
                
                const paginatedEmployees = filteredEmployees.slice(startIndex, endIndex);
                
                resolve({
                    success: true,
                    data: paginatedEmployees,
                    total: filteredEmployees.length,
                    page: page,
                    limit: limit,
                    totalPages: Math.ceil(filteredEmployees.length / limit)
                });
            }, 250);
        });
    }

    // Get departments
    async getDepartments() {
        return new Promise((resolve) => {
            setTimeout(() => {
                const employees = JSON.parse(localStorage.getItem(this.storageKey) || '[]');
                const departments = [...new Set(employees.map(emp => emp.department))].sort();
                
                resolve({
                    success: true,
                    data: departments
                });
            }, 100);
        });
    }

    // Get managers (employees who can be managers)
    async getManagers() {
        return new Promise((resolve) => {
            setTimeout(() => {
                const employees = JSON.parse(localStorage.getItem(this.storageKey) || '[]');
                const managers = employees
                    .filter(emp => emp.status === 'Active')
                    .map(emp => ({
                        id: emp.id,
                        name: `${emp.firstName} ${emp.lastName}`,
                        department: emp.department,
                        position: emp.position
                    }))
                    .sort((a, b) => a.name.localeCompare(b.name));
                
                resolve({
                    success: true,
                    data: managers
                });
            }, 150);
        });
    }
}

// Export for use in other files
window.EmployeeAPI = EmployeeAPI;