// Employee View with Comprehensive Salary Management
let currentEmployee = null;

// Tax brackets and rates (simplified US tax system)
const TAX_BRACKETS = [
    { min: 0, max: 10275, rate: 0.10 },
    { min: 10275, max: 41775, rate: 0.12 },
    { min: 41775, max: 89450, rate: 0.22 },
    { min: 89450, max: 190750, rate: 0.24 },
    { min: 190750, max: 364200, rate: 0.32 },
    { min: 364200, max: 462500, rate: 0.35 },
    { min: 462500, max: Infinity, rate: 0.37 }
];

// Social Security rate (6.2% up to wage base)
const SOCIAL_SECURITY_RATE = 0.062;
const SOCIAL_SECURITY_WAGE_BASE = 160200; // 2023 limit

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadEmployeeData();
    setupEventListeners();
});

// Load employee data
function loadEmployeeData() {
    // Get employee ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const employeeId = urlParams.get('id') || '1'; // Default to employee 1 for demo
    
    console.log('Loading employee data for ID:', employeeId);
    
    // Enhanced sample data with comprehensive salary information
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
            status: "Active",
            manager: "Jane Smith",
            address: "123 Main St, City, State 12345",
            notes: "Excellent performance in Q1 2024",
            lastUpdated: "2024-01-15",
            currentSalary: {
                basicSalary: 60000,
                houseAllowance: 8000,
                transportAllowance: 2400,
                medicalAllowance: 1200,
                overtimePay: 3000,
                performanceBonus: 4000,
                incomeTax: 0,
                socialSecurity: 0,
                healthInsurance: 2400,
                loanDeduction: 500,
                effectiveDate: "2024-01-01",
                reason: "annual_increment"
            },
            salaryHistory: [
                {
                    effectiveDate: "2024-01-01",
                    basicSalary: 60000,
                    houseAllowance: 8000,
                    transportAllowance: 2400,
                    medicalAllowance: 1200,
                    overtimePay: 3000,
                    performanceBonus: 4000,
                    incomeTax: 12500,
                    socialSecurity: 4876,
                    healthInsurance: 2400,
                    loanDeduction: 500,
                    grossSalary: 78600,
                    netSalary: 58324,
                    reason: "annual_increment",
                    changedBy: "HR Admin",
                    changeDate: "2023-12-15"
                },
                {
                    effectiveDate: "2023-01-15",
                    basicSalary: 55000,
                    houseAllowance: 7000,
                    transportAllowance: 2000,
                    medicalAllowance: 1000,
                    overtimePay: 2000,
                    performanceBonus: 3000,
                    incomeTax: 10500,
                    socialSecurity: 4340,
                    healthInsurance: 2000,
                    loanDeduction: 0,
                    grossSalary: 70000,
                    netSalary: 53160,
                    reason: "initial_hire",
                    changedBy: "HR Admin",
                    changeDate: "2023-01-10"
                }
            ],
            payslips: []
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
            status: "Active",
            manager: "",
            address: "456 Oak Ave, City, State 12345",
            notes: "Team lead for HR initiatives",
            lastUpdated: "2024-01-10",
            currentSalary: {
                basicSalary: 70000,
                houseAllowance: 10000,
                transportAllowance: 3000,
                medicalAllowance: 1500,
                overtimePay: 2000,
                performanceBonus: 5000,
                incomeTax: 0,
                socialSecurity: 0,
                healthInsurance: 3000,
                loanDeduction: 0,
                effectiveDate: "2024-01-01",
                reason: "annual_increment"
            },
            salaryHistory: [
                {
                    effectiveDate: "2024-01-01",
                    basicSalary: 70000,
                    houseAllowance: 10000,
                    transportAllowance: 3000,
                    medicalAllowance: 1500,
                    overtimePay: 2000,
                    performanceBonus: 5000,
                    incomeTax: 15500,
                    socialSecurity: 5673,
                    healthInsurance: 3000,
                    loanDeduction: 0,
                    grossSalary: 91500,
                    netSalary: 67327,
                    reason: "annual_increment",
                    changedBy: "HR Admin",
                    changeDate: "2023-12-15"
                }
            ],
            payslips: []
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
            status: "Active",
            manager: "Sarah Wilson",
            address: "789 Pine St, City, State 12345",
            notes: "Recently completed CPA certification",
            lastUpdated: "2024-01-12",
            currentSalary: {
                basicSalary: 55000,
                houseAllowance: 5000,
                transportAllowance: 2000,
                medicalAllowance: 1000,
                overtimePay: 1500,
                performanceBonus: 3000,
                incomeTax: 0,
                socialSecurity: 0,
                healthInsurance: 2000,
                loanDeduction: 200,
                effectiveDate: "2024-01-01",
                reason: "annual_increment"
            },
            salaryHistory: [
                {
                    effectiveDate: "2024-01-01",
                    basicSalary: 55000,
                    houseAllowance: 5000,
                    transportAllowance: 2000,
                    medicalAllowance: 1000,
                    overtimePay: 1500,
                    performanceBonus: 3000,
                    incomeTax: 10800,
                    socialSecurity: 4185,
                    healthInsurance: 2000,
                    loanDeduction: 200,
                    grossSalary: 67500,
                    netSalary: 50315,
                    reason: "annual_increment",
                    changedBy: "HR Admin",
                    changeDate: "2023-12-15"
                }
            ],
            payslips: []
        }
    ];

    // Find the current employee
    currentEmployee = sampleEmployees.find(emp => emp.id == employeeId);
    
    console.log('Found employee:', currentEmployee);
    
    if (!currentEmployee) {
        console.error('Employee not found for ID:', employeeId);
        showNotification('Employee not found', 'error');
        return;
    }

    // Calculate taxes for current employee
    calculateEmployeeTaxes(currentEmployee);
    
    // Display employee data
    displayEmployeeData();
}

// Display employee data
function displayEmployeeData() {
    if (!currentEmployee) {
        console.error('No current employee data to display');
        return;
    }

    console.log('Displaying employee data:', currentEmployee);

    // Basic information
    document.getElementById('fullName').textContent = `${currentEmployee.firstName} ${currentEmployee.lastName}`;
    document.getElementById('employeeId').textContent = currentEmployee.id;
    document.getElementById('email').textContent = currentEmployee.email;
    document.getElementById('phone').textContent = currentEmployee.phone;
    document.getElementById('department').textContent = currentEmployee.department;
    document.getElementById('position').textContent = currentEmployee.position;
    const statusElement = document.getElementById('status');
    statusElement.textContent = currentEmployee.status;
    // Add appropriate badge class based on status
    statusElement.className = 'badge ' + (currentEmployee.status === 'Active' ? 'badge-success' : 'badge-secondary');
    document.getElementById('manager').textContent = currentEmployee.manager || 'N/A';
    document.getElementById('address').textContent = currentEmployee.address;
    
    // Employment details
    document.getElementById('hireDate').textContent = formatDate(currentEmployee.hireDate);
    document.getElementById('yearsOfService').textContent = calculateYearsOfService(currentEmployee.hireDate);
    document.getElementById('lastUpdated').textContent = formatDate(currentEmployee.lastUpdated);
    
    // Salary information - commented out as HTML elements don't exist
    // displaySalaryInformation();
    
    // Notes
    document.getElementById('notes').textContent = currentEmployee.notes || 'No notes available';
}

// Display salary information
function displaySalaryInformation() {
    if (!currentEmployee || !currentEmployee.currentSalary) return;
    
    const salary = currentEmployee.currentSalary;
    
    // Display individual components
    document.getElementById('basicSalary').textContent = formatCurrency(salary.basicSalary);
    document.getElementById('houseAllowance').textContent = formatCurrency(salary.houseAllowance);
    document.getElementById('transportAllowance').textContent = formatCurrency(salary.transportAllowance);
    document.getElementById('medicalAllowance').textContent = formatCurrency(salary.medicalAllowance);
    document.getElementById('overtimePay').textContent = formatCurrency(salary.overtimePay);
    document.getElementById('performanceBonus').textContent = formatCurrency(salary.performanceBonus);
    document.getElementById('incomeTax').textContent = formatCurrency(salary.incomeTax);
    
    // Calculate other deductions
    const otherDeductions = salary.socialSecurity + salary.healthInsurance + salary.loanDeduction;
    document.getElementById('otherDeductions').textContent = formatCurrency(otherDeductions);
    
    // Calculate gross and net salary
    const grossSalary = calculateGrossSalary(salary);
    const netSalary = calculateNetSalary(salary);
    
    document.getElementById('grossSalary').textContent = formatCurrency(grossSalary);
    document.getElementById('netSalary').textContent = formatCurrency(netSalary);
    document.getElementById('salaryEffectiveDate').textContent = formatDate(salary.effectiveDate);
}

// Calculate gross salary
function calculateGrossSalary(salary) {
    return salary.basicSalary + 
           salary.houseAllowance + 
           salary.transportAllowance + 
           salary.medicalAllowance + 
           salary.overtimePay + 
           salary.performanceBonus;
}

// Calculate net salary
function calculateNetSalary(salary) {
    const gross = calculateGrossSalary(salary);
    const totalDeductions = salary.incomeTax + 
                           salary.socialSecurity + 
                           salary.healthInsurance + 
                           salary.loanDeduction;
    return gross - totalDeductions;
}

// Calculate employee taxes and social security
function calculateEmployeeTaxes(employee) {
    const grossAnnual = calculateGrossSalary(employee.currentSalary) * 12;
    
    // Calculate income tax
    let tax = 0;
    let remainingIncome = grossAnnual;
    
    for (const bracket of TAX_BRACKETS) {
        if (remainingIncome <= 0) break;
        
        const taxableInThisBracket = Math.min(remainingIncome, bracket.max - bracket.min);
        tax += taxableInThisBracket * bracket.rate;
        remainingIncome -= taxableInThisBracket;
    }
    
    // Monthly tax
    employee.currentSalary.incomeTax = Math.round(tax / 12);
    
    // Calculate Social Security (6.2% up to wage base)
    const socialSecurityWages = Math.min(grossAnnual, SOCIAL_SECURITY_WAGE_BASE);
    employee.currentSalary.socialSecurity = Math.round((socialSecurityWages * SOCIAL_SECURITY_RATE) / 12);
}

// Setup event listeners
function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Salary management modal event listeners - only if element exists
    const saveSalaryBtn = document.getElementById('saveSalaryChanges');
    if (saveSalaryBtn) {
        saveSalaryBtn.addEventListener('click', saveSalaryChanges);
    }
    
    // Real-time salary calculation in modal
    const salaryInputs = document.querySelectorAll('.salary-input');
    salaryInputs.forEach(input => {
        input.addEventListener('input', updateSalaryPreview);
    });
    
    // Delete confirmation - only if element exists
    const confirmDeleteBtn = document.getElementById('confirmDelete');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', confirmDeleteEmployee);
    }
    
    console.log('Event listeners setup complete');
}

// Edit employee salary
function editEmployeeSalary() {
    if (!currentEmployee) return;
    
    // Populate modal with employee name
    document.getElementById('modalEmployeeName').textContent = `${currentEmployee.firstName} ${currentEmployee.lastName}`;
    
    // Set default effective date to first of next month
    const today = new Date();
    const firstOfNextMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1);
    document.getElementById('effectiveDate').value = firstOfNextMonth.toISOString().split('T')[0];
    
    // Populate form with current salary data
    const salary = currentEmployee.currentSalary;
    document.getElementById('editBasicSalary').value = salary.basicSalary;
    document.getElementById('editHouseAllowance').value = salary.houseAllowance;
    document.getElementById('editTransportAllowance').value = salary.transportAllowance;
    document.getElementById('editMedicalAllowance').value = salary.medicalAllowance;
    document.getElementById('editOvertimePay').value = salary.overtimePay;
    document.getElementById('editPerformanceBonus').value = salary.performanceBonus;
    document.getElementById('editIncomeTax').value = salary.incomeTax;
    document.getElementById('editSocialSecurity').value = salary.socialSecurity;
    document.getElementById('editHealthInsurance').value = salary.healthInsurance;
    document.getElementById('editLoanDeduction').value = salary.loanDeduction;
    
    // Display salary history
    displaySalaryHistory();
    
    // Update preview
    updateSalaryPreview();
    
    // Show modal
    $('#salaryManagementModal').modal('show');
}

// Display salary history in modal
function displaySalaryHistory() {
    if (!currentEmployee || !currentEmployee.salaryHistory) return;
    
    const container = document.getElementById('salaryHistoryContainer');
    container.innerHTML = '';
    
    currentEmployee.salaryHistory.forEach((record, index) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'salary-history-item mb-3 p-3 border-left border-primary';
        historyItem.innerHTML = `
            <div class="d-flex justify-content-between align-items-start mb-2">
                <strong>${formatDate(record.effectiveDate)}</strong>
                <span class="badge badge-info">${record.reason.replace('_', ' ')}</span>
            </div>
            <div class="salary-details">
                <div class="row">
                    <div class="col-6">
                        <small class="text-muted">Basic: ${formatCurrency(record.basicSalary)}</small><br>
                        <small class="text-muted">Gross: ${formatCurrency(record.grossSalary)}</small>
                    </div>
                    <div class="col-6">
                        <small class="text-success">Net: ${formatCurrency(record.netSalary)}</small><br>
                        <small class="text-danger">Tax: ${formatCurrency(record.incomeTax)}</small>
                    </div>
                </div>
            </div>
            <div class="mt-2">
                <small class="text-muted">
                    Changed by: ${record.changedBy} on ${formatDate(record.changeDate)}
                </small>
            </div>
        `;
        container.appendChild(historyItem);
    });
}

// Update salary preview in modal
function updateSalaryPreview() {
    const basicSalary = parseFloat(document.getElementById('editBasicSalary').value) || 0;
    const houseAllowance = parseFloat(document.getElementById('editHouseAllowance').value) || 0;
    const transportAllowance = parseFloat(document.getElementById('editTransportAllowance').value) || 0;
    const medicalAllowance = parseFloat(document.getElementById('editMedicalAllowance').value) || 0;
    const overtimePay = parseFloat(document.getElementById('editOvertimePay').value) || 0;
    const performanceBonus = parseFloat(document.getElementById('editPerformanceBonus').value) || 0;
    
    const incomeTax = parseFloat(document.getElementById('editIncomeTax').value) || 0;
    const socialSecurity = parseFloat(document.getElementById('editSocialSecurity').value) || 0;
    const healthInsurance = parseFloat(document.getElementById('editHealthInsurance').value) || 0;
    const loanDeduction = parseFloat(document.getElementById('editLoanDeduction').value) || 0;
    
    const grossSalary = basicSalary + houseAllowance + transportAllowance + medicalAllowance + overtimePay + performanceBonus;
    const totalDeductions = incomeTax + socialSecurity + healthInsurance + loanDeduction;
    const netSalary = grossSalary - totalDeductions;
    
    document.getElementById('grossSalaryPreview').textContent = formatCurrency(grossSalary);
    document.getElementById('totalDeductionsPreview').textContent = formatCurrency(totalDeductions);
    document.getElementById('netSalaryPreview').textContent = formatCurrency(netSalary);
}

// Calculate tax automatically
function calculateTax() {
    if (!currentEmployee) return;
    
    const tempSalary = {
        basicSalary: parseFloat(document.getElementById('editBasicSalary').value) || 0,
        houseAllowance: parseFloat(document.getElementById('editHouseAllowance').value) || 0,
        transportAllowance: parseFloat(document.getElementById('editTransportAllowance').value) || 0,
        medicalAllowance: parseFloat(document.getElementById('editMedicalAllowance').value) || 0,
        overtimePay: parseFloat(document.getElementById('editOvertimePay').value) || 0,
        performanceBonus: parseFloat(document.getElementById('editPerformanceBonus').value) || 0
    };
    
    const grossAnnual = calculateGrossSalary(tempSalary) * 12;
    
    // Calculate income tax
    let tax = 0;
    let remainingIncome = grossAnnual;
    
    for (const bracket of TAX_BRACKETS) {
        if (remainingIncome <= 0) break;
        
        const taxableInThisBracket = Math.min(remainingIncome, bracket.max - bracket.min);
        tax += taxableInThisBracket * bracket.rate;
        remainingIncome -= taxableInThisBracket;
    }
    
    // Update tax fields
    document.getElementById('editIncomeTax').value = Math.round(tax / 12);
    
    // Calculate Social Security
    const socialSecurityWages = Math.min(grossAnnual, SOCIAL_SECURITY_WAGE_BASE);
    document.getElementById('editSocialSecurity').value = Math.round((socialSecurityWages * SOCIAL_SECURITY_RATE) / 12);
    
    // Update preview
    updateSalaryPreview();
    
    showNotification('Tax calculations updated automatically', 'success');
}

// Update salary preview in modal
function updateSalaryPreview() {
    try {
        const basicSalary = parseFloat(document.getElementById('editBasicSalary').value) || 0;
        const houseAllowance = parseFloat(document.getElementById('editHouseAllowance').value) || 0;
        const transportAllowance = parseFloat(document.getElementById('editTransportAllowance').value) || 0;
        const medicalAllowance = parseFloat(document.getElementById('editMedicalAllowance').value) || 0;
        const overtimePay = parseFloat(document.getElementById('editOvertimePay').value) || 0;
        const performanceBonus = parseFloat(document.getElementById('editPerformanceBonus').value) || 0;
        
        const incomeTax = parseFloat(document.getElementById('editIncomeTax').value) || 0;
        const socialSecurity = parseFloat(document.getElementById('editSocialSecurity').value) || 0;
        const healthInsurance = parseFloat(document.getElementById('editHealthInsurance').value) || 0;
        const loanDeduction = parseFloat(document.getElementById('editLoanDeduction').value) || 0;
        
        const grossSalary = basicSalary + houseAllowance + transportAllowance + medicalAllowance + overtimePay + performanceBonus;
        const totalDeductions = incomeTax + socialSecurity + healthInsurance + loanDeduction;
        const netSalary = grossSalary - totalDeductions;
        
        // Update preview elements if they exist
        const grossPreview = document.getElementById('previewGrossSalary');
        const netPreview = document.getElementById('previewNetSalary');
        const deductionsPreview = document.getElementById('previewTotalDeductions');
        
        if (grossPreview) grossPreview.textContent = formatCurrency(grossSalary);
        if (netPreview) netPreview.textContent = formatCurrency(netSalary);
        if (deductionsPreview) deductionsPreview.textContent = formatCurrency(totalDeductions);
        
    } catch (error) {
        console.error('Error updating salary preview:', error);
    }
}

// Save salary changes
function saveSalaryChanges() {
    if (!currentEmployee) return;
    
    const effectiveDate = document.getElementById('effectiveDate').value;
    const changeReason = document.getElementById('changeReason').value;
    
    if (!effectiveDate) {
        showNotification('Please select an effective date', 'error');
        return;
    }
    
    const basicSalary = parseFloat(document.getElementById('editBasicSalary').value) || 0;
    if (basicSalary <= 0) {
        showNotification('Basic salary must be greater than 0', 'error');
        return;
    }
    
    // Show loading state
    const saveBtn = document.getElementById('saveSalaryChanges');
    const originalText = saveBtn.innerHTML;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    saveBtn.disabled = true;
    
    setTimeout(() => {
        try {
            // Create new salary record
            const newSalary = {
                basicSalary: basicSalary,
                houseAllowance: parseFloat(document.getElementById('editHouseAllowance').value) || 0,
                transportAllowance: parseFloat(document.getElementById('editTransportAllowance').value) || 0,
                medicalAllowance: parseFloat(document.getElementById('editMedicalAllowance').value) || 0,
                overtimePay: parseFloat(document.getElementById('editOvertimePay').value) || 0,
                performanceBonus: parseFloat(document.getElementById('editPerformanceBonus').value) || 0,
                incomeTax: parseFloat(document.getElementById('editIncomeTax').value) || 0,
                socialSecurity: parseFloat(document.getElementById('editSocialSecurity').value) || 0,
                healthInsurance: parseFloat(document.getElementById('editHealthInsurance').value) || 0,
                loanDeduction: parseFloat(document.getElementById('editLoanDeduction').value) || 0,
                effectiveDate: effectiveDate,
                reason: changeReason
            };
            
            // Add to salary history
            const historyRecord = {
                effectiveDate: effectiveDate,
                basicSalary: newSalary.basicSalary,
                houseAllowance: newSalary.houseAllowance,
                transportAllowance: newSalary.transportAllowance,
                medicalAllowance: newSalary.medicalAllowance,
                overtimePay: newSalary.overtimePay,
                performanceBonus: newSalary.performanceBonus,
                incomeTax: newSalary.incomeTax,
                socialSecurity: newSalary.socialSecurity,
                healthInsurance: newSalary.healthInsurance,
                loanDeduction: newSalary.loanDeduction,
                grossSalary: calculateGrossSalary(newSalary),
                netSalary: calculateNetSalary(newSalary),
                reason: changeReason,
                changedBy: "HR Admin", // In real app, this would be the logged-in user
                changeDate: new Date().toISOString().split('T')[0]
            };
            
            currentEmployee.salaryHistory.unshift(historyRecord);
            currentEmployee.currentSalary = newSalary;
            currentEmployee.lastUpdated = new Date().toISOString().split('T')[0];
            
            // Update display
            displaySalaryInformation();
            document.getElementById('lastUpdated').textContent = formatDate(currentEmployee.lastUpdated);
            
            // Hide modal
            $('#salaryManagementModal').modal('hide');
            
            showNotification(`Salary updated successfully for ${currentEmployee.firstName} ${currentEmployee.lastName}`, 'success');
            
        } catch (error) {
            console.error('Error saving salary changes:', error);
            showNotification('Error saving salary changes. Please try again.', 'error');
        } finally {
            // Reset button
            saveBtn.innerHTML = originalText;
            saveBtn.disabled = false;
        }
    }, 1000);
}

// View salary history
function viewSalaryHistory() {
    if (!currentEmployee) return;
    
    document.getElementById('historyEmployeeName').textContent = `${currentEmployee.firstName} ${currentEmployee.lastName}`;
    
    const timeline = document.getElementById('salaryHistoryTimeline');
    timeline.innerHTML = '';
    
    currentEmployee.salaryHistory.forEach((record, index) => {
        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item mb-4';
        timelineItem.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">${formatDate(record.effectiveDate)}</h6>
                        <span class="badge badge-primary">${record.reason.replace('_', ' ')}</span>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Earnings</h6>
                            <table class="table table-sm">
                                <tr><td>Basic Salary:</td><td class="text-right">${formatCurrency(record.basicSalary)}</td></tr>
                                <tr><td>House Allowance:</td><td class="text-right">${formatCurrency(record.houseAllowance)}</td></tr>
                                <tr><td>Transport Allowance:</td><td class="text-right">${formatCurrency(record.transportAllowance)}</td></tr>
                                <tr><td>Medical Allowance:</td><td class="text-right">${formatCurrency(record.medicalAllowance)}</td></tr>
                                <tr><td>Overtime Pay:</td><td class="text-right">${formatCurrency(record.overtimePay)}</td></tr>
                                <tr><td>Performance Bonus:</td><td class="text-right">${formatCurrency(record.performanceBonus)}</td></tr>
                                <tr class="table-info"><td><strong>Gross Total:</strong></td><td class="text-right"><strong>${formatCurrency(record.grossSalary)}</strong></td></tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <h6>Deductions</h6>
                            <table class="table table-sm">
                                <tr><td>Income Tax:</td><td class="text-right">${formatCurrency(record.incomeTax)}</td></tr>
                                <tr><td>Social Security:</td><td class="text-right">${formatCurrency(record.socialSecurity)}</td></tr>
                                <tr><td>Health Insurance:</td><td class="text-right">${formatCurrency(record.healthInsurance)}</td></tr>
                                <tr><td>Loan Deduction:</td><td class="text-right">${formatCurrency(record.loanDeduction)}</td></tr>
                                <tr class="table-danger"><td><strong>Total Deductions:</strong></td><td class="text-right"><strong>${formatCurrency(record.incomeTax + record.socialSecurity + record.healthInsurance + record.loanDeduction)}</strong></td></tr>
                                <tr class="table-success"><td><strong>Net Salary:</strong></td><td class="text-right"><strong>${formatCurrency(record.netSalary)}</strong></td></tr>
                            </table>
                        </div>
                    </div>
                    <div class="mt-2">
                        <small class="text-muted">
                            Changed by: ${record.changedBy} on ${formatDate(record.changeDate)}
                        </small>
                    </div>
                </div>
            </div>
        `;
        timeline.appendChild(timelineItem);
    });
    
    $('#salaryHistoryModal').modal('show');
}

// Generate employee payslip
function generateEmployeePayslip() {
    if (!currentEmployee) return;
    
    const payslip = generatePayslipData(currentEmployee);
    displayPayslipPreview(payslip);
}

// Generate payslip data
function generatePayslipData(employee, month = null, year = null) {
    const currentDate = new Date();
    const payMonth = month || currentDate.getMonth() + 1;
    const payYear = year || currentDate.getFullYear();
    
    const salary = employee.currentSalary;
    const grossSalary = calculateGrossSalary(salary);
    const netSalary = calculateNetSalary(salary);
    
    return {
        employee: employee,
        payPeriod: {
            month: payMonth,
            year: payYear,
            monthName: new Date(payYear, payMonth - 1).toLocaleString('default', { month: 'long' })
        },
        earnings: {
            basicSalary: salary.basicSalary,
            houseAllowance: salary.houseAllowance,
            transportAllowance: salary.transportAllowance,
            medicalAllowance: salary.medicalAllowance,
            overtimePay: salary.overtimePay,
            performanceBonus: salary.performanceBonus,
            total: grossSalary
        },
        deductions: {
            incomeTax: salary.incomeTax,
            socialSecurity: salary.socialSecurity,
            healthInsurance: salary.healthInsurance,
            loanDeduction: salary.loanDeduction,
            total: salary.incomeTax + salary.socialSecurity + salary.healthInsurance + salary.loanDeduction
        },
        netPay: netSalary,
        generatedDate: new Date().toISOString().split('T')[0],
        payslipId: `PAY-${employee.id}-${payYear}${payMonth.toString().padStart(2, '0')}`
    };
}

// Display payslip preview
function displayPayslipPreview(payslip) {
    const content = document.getElementById('payslipContent');
    if (!content) return;
    
    content.innerHTML = `
        <div class="payslip-document">
            <div class="text-center mb-4">
                <h4>COMPANY NAME</h4>
                <p class="text-muted">123 Business Street, City, State 12345</p>
                <h5>PAYSLIP</h5>
            </div>
            
            <div class="row mb-3">
                <div class="col-6">
                    <strong>Employee Details:</strong><br>
                    Name: ${payslip.employee.firstName} ${payslip.employee.lastName}<br>
                    ID: ${payslip.employee.id}<br>
                    Department: ${payslip.employee.department}<br>
                    Position: ${payslip.employee.position}<br>
                    Email: ${payslip.employee.email}
                </div>
                <div class="col-6 text-right">
                    <strong>Pay Period:</strong><br>
                    ${payslip.payPeriod.monthName} ${payslip.payPeriod.year}<br>
                    <strong>Payslip ID:</strong> ${payslip.payslipId}<br>
                    <strong>Generated:</strong> ${formatDate(payslip.generatedDate)}
                </div>
            </div>
            
            <table class="table table-bordered">
                <thead class="thead-light">
                    <tr>
                        <th>EARNINGS</th>
                        <th class="text-right">AMOUNT</th>
                        <th>DEDUCTIONS</th>
                        <th class="text-right">AMOUNT</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Basic Salary</td>
                        <td class="text-right">${formatCurrency(payslip.earnings.basicSalary)}</td>
                        <td>Income Tax</td>
                        <td class="text-right">${formatCurrency(payslip.deductions.incomeTax)}</td>
                    </tr>
                    <tr>
                        <td>House Allowance</td>
                        <td class="text-right">${formatCurrency(payslip.earnings.houseAllowance)}</td>
                        <td>Social Security</td>
                        <td class="text-right">${formatCurrency(payslip.deductions.socialSecurity)}</td>
                    </tr>
                    <tr>
                        <td>Transport Allowance</td>
                        <td class="text-right">${formatCurrency(payslip.earnings.transportAllowance)}</td>
                        <td>Health Insurance</td>
                        <td class="text-right">${formatCurrency(payslip.deductions.healthInsurance)}</td>
                    </tr>
                    <tr>
                        <td>Medical Allowance</td>
                        <td class="text-right">${formatCurrency(payslip.earnings.medicalAllowance)}</td>
                        <td>Loan Deduction</td>
                        <td class="text-right">${formatCurrency(payslip.deductions.loanDeduction)}</td>
                    </tr>
                    <tr>
                        <td>Overtime Pay</td>
                        <td class="text-right">${formatCurrency(payslip.earnings.overtimePay)}</td>
                        <td></td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>Performance Bonus</td>
                        <td class="text-right">${formatCurrency(payslip.earnings.performanceBonus)}</td>
                        <td></td>
                        <td></td>
                    </tr>
                    <tr class="table-info">
                        <td><strong>TOTAL EARNINGS</strong></td>
                        <td class="text-right"><strong>${formatCurrency(payslip.earnings.total)}</strong></td>
                        <td><strong>TOTAL DEDUCTIONS</strong></td>
                        <td class="text-right"><strong>${formatCurrency(payslip.deductions.total)}</strong></td>
                    </tr>
                </tbody>
            </table>
            
            <div class="row">
                <div class="col-12 text-center">
                    <div class="alert alert-success">
                        <h5><strong>NET PAY: ${formatCurrency(payslip.netPay)}</strong></h5>
                    </div>
                </div>
            </div>
            
            <div class="mt-4 text-center">
                <small class="text-muted">
                    This is a computer-generated payslip and does not require a signature.<br>
                    For any queries, please contact HR Department.
                </small>
            </div>
        </div>
    `;
    
    // Store current payslip for download/email
    window.currentPayslip = payslip;
    
    // Show modal
    $('#payslipPreviewModal').modal('show');
}

// Preview payslip from salary edit modal
function previewPayslip() {
    if (!currentEmployee) return;
    
    // Create temporary salary object with current form values
    const tempSalary = {
        basicSalary: parseFloat(document.getElementById('editBasicSalary').value) || 0,
        houseAllowance: parseFloat(document.getElementById('editHouseAllowance').value) || 0,
        transportAllowance: parseFloat(document.getElementById('editTransportAllowance').value) || 0,
        medicalAllowance: parseFloat(document.getElementById('editMedicalAllowance').value) || 0,
        overtimePay: parseFloat(document.getElementById('editOvertimePay').value) || 0,
        performanceBonus: parseFloat(document.getElementById('editPerformanceBonus').value) || 0,
        incomeTax: parseFloat(document.getElementById('editIncomeTax').value) || 0,
        socialSecurity: parseFloat(document.getElementById('editSocialSecurity').value) || 0,
        healthInsurance: parseFloat(document.getElementById('editHealthInsurance').value) || 0,
        loanDeduction: parseFloat(document.getElementById('editLoanDeduction').value) || 0
    };
    
    // Create temporary employee object
    const tempEmployee = {
        ...currentEmployee,
        currentSalary: tempSalary
    };
    
    const payslip = generatePayslipData(tempEmployee);
    displayPayslipPreview(payslip);
}

// Download payslip as PDF
function downloadPayslipPDF() {
    if (!window.currentPayslip) return;
    
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    const payslip = window.currentPayslip;
    
    // Add content to PDF
    doc.setFontSize(16);
    doc.text('COMPANY NAME', 105, 20, { align: 'center' });
    doc.setFontSize(12);
    doc.text('123 Business Street, City, State 12345', 105, 30, { align: 'center' });
    doc.setFontSize(14);
    doc.text('PAYSLIP', 105, 45, { align: 'center' });
    
    // Employee details
    doc.setFontSize(10);
    doc.text(`Employee: ${payslip.employee.firstName} ${payslip.employee.lastName}`, 20, 65);
    doc.text(`ID: ${payslip.employee.id}`, 20, 75);
    doc.text(`Department: ${payslip.employee.department}`, 20, 85);
    doc.text(`Position: ${payslip.employee.position}`, 20, 95);
    
    // Pay period
    doc.text(`Pay Period: ${payslip.payPeriod.monthName} ${payslip.payPeriod.year}`, 120, 65);
    doc.text(`Payslip ID: ${payslip.payslipId}`, 120, 75);
    doc.text(`Generated: ${formatDate(payslip.generatedDate)}`, 120, 85);
    
    // Earnings and deductions table
    let yPos = 110;
    doc.text('EARNINGS', 20, yPos);
    doc.text('AMOUNT', 80, yPos);
    doc.text('DEDUCTIONS', 120, yPos);
    doc.text('AMOUNT', 180, yPos);
    
    yPos += 10;
    doc.text(`Basic Salary`, 20, yPos);
    doc.text(formatCurrency(payslip.earnings.basicSalary), 80, yPos);
    doc.text('Income Tax', 120, yPos);
    doc.text(formatCurrency(payslip.deductions.incomeTax), 180, yPos);
    
    yPos += 10;
    doc.text('House Allowance', 20, yPos);
    doc.text(formatCurrency(payslip.earnings.houseAllowance), 80, yPos);
    doc.text('Social Security', 120, yPos);
    doc.text(formatCurrency(payslip.deductions.socialSecurity), 180, yPos);
    
    yPos += 10;
    doc.text('Transport Allowance', 20, yPos);
    doc.text(formatCurrency(payslip.earnings.transportAllowance), 80, yPos);
    doc.text('Health Insurance', 120, yPos);
    doc.text(formatCurrency(payslip.deductions.healthInsurance), 180, yPos);
    
    yPos += 10;
    doc.text('Medical Allowance', 20, yPos);
    doc.text(formatCurrency(payslip.earnings.medicalAllowance), 80, yPos);
    doc.text('Loan Deduction', 120, yPos);
    doc.text(formatCurrency(payslip.deductions.loanDeduction), 180, yPos);
    
    yPos += 10;
    doc.text('Overtime Pay', 20, yPos);
    doc.text(formatCurrency(payslip.earnings.overtimePay), 80, yPos);
    
    yPos += 10;
    doc.text('Performance Bonus', 20, yPos);
    doc.text(formatCurrency(payslip.earnings.performanceBonus), 80, yPos);
    
    yPos += 20;
    doc.setFontSize(12);
    doc.text('TOTAL EARNINGS', 20, yPos);
    doc.text(formatCurrency(payslip.earnings.total), 80, yPos);
    doc.text('TOTAL DEDUCTIONS', 120, yPos);
    doc.text(formatCurrency(payslip.deductions.total), 180, yPos);
    
    yPos += 20;
    doc.setFontSize(14);
    doc.text(`NET PAY: ${formatCurrency(payslip.netPay)}`, 105, yPos, { align: 'center' });
    
    // Save PDF
    doc.save(`payslip-${payslip.employee.firstName}-${payslip.employee.lastName}-${payslip.payPeriod.year}-${payslip.payPeriod.month}.pdf`);
    
    showNotification('Payslip PDF downloaded successfully', 'success');
}

// Email payslip to employee
function emailPayslip() {
    if (!window.currentPayslip) return;
    
    const payslip = window.currentPayslip;
    
    // Simulate email sending
    showNotification('Sending payslip via email...', 'info');
    
    setTimeout(() => {
        // Store payslip in employee record
        if (currentEmployee) {
            currentEmployee.payslips.push({
                ...payslip,
                emailSent: true,
                emailSentDate: new Date().toISOString()
            });
        }
        
        showNotification(`Payslip emailed successfully to ${payslip.employee.email}`, 'success');
    }, 2000);
}

// Export salary history
function exportSalaryHistory() {
    if (!currentEmployee) return;
    
    const historyData = currentEmployee.salaryHistory.map(record => ({
        'Effective Date': record.effectiveDate,
        'Basic Salary': record.basicSalary,
        'House Allowance': record.houseAllowance,
        'Transport Allowance': record.transportAllowance,
        'Medical Allowance': record.medicalAllowance,
        'Overtime Pay': record.overtimePay,
        'Performance Bonus': record.performanceBonus,
        'Gross Salary': record.grossSalary,
        'Income Tax': record.incomeTax,
        'Social Security': record.socialSecurity,
        'Health Insurance': record.healthInsurance,
        'Loan Deduction': record.loanDeduction,
        'Net Salary': record.netSalary,
        'Reason': record.reason,
        'Changed By': record.changedBy,
        'Change Date': record.changeDate
    }));
    
    // Convert to CSV
    const headers = Object.keys(historyData[0]);
    const csvContent = [
        headers.join(','),
        ...historyData.map(row => headers.map(header => row[header]).join(','))
    ].join('\n');
    
    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `salary-history-${currentEmployee.firstName}-${currentEmployee.lastName}-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    showNotification('Salary history exported successfully', 'success');
}

// Delete employee function
function deleteEmployee() {
    if (!currentEmployee) return;
    
    document.getElementById('deleteEmployeeName').textContent = `${currentEmployee.firstName} ${currentEmployee.lastName}`;
    $('#deleteModal').modal('show');
}

// Confirm delete employee
function confirmDeleteEmployee() {
    showNotification('Employee deletion functionality would be implemented here', 'info');
    $('#deleteModal').modal('hide');
}

// Quick action functions
function viewAttendance() {
    showNotification('Attendance view functionality coming soon!', 'info');
}

function viewLeaves() {
    showNotification('Leave management functionality coming soon!', 'info');
}

function generateReport() {
    showNotification('Generating employee report...', 'info');
    
    setTimeout(() => {
        showNotification('Employee report generated successfully!', 'success');
    }, 2000);
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return 'Not available';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function calculateYearsOfService(hireDate) {
    if (!hireDate) return 'Not available';
    const hire = new Date(hireDate);
    const now = new Date();
    const years = now.getFullYear() - hire.getFullYear();
    const months = now.getMonth() - hire.getMonth();
    
    if (months < 0 || (months === 0 && now.getDate() < hire.getDate())) {
        return years - 1 + ' years';
    }
    return years + ' years';
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