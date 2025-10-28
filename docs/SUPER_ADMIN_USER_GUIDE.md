# Super Admin User Guide - HRMS Application

**Version:** 1.0  
**Last Updated:** 2024  
**For:** Super Admin Users

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Tenant Management](#tenant-management)
4. [Payment Configuration](#payment-configuration)
5. [Document Management](#document-management)
6. [Employee Management](#employee-management)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Logging In
1. Navigate to the HRMS application URL
2. Enter your Super Admin credentials
3. Click "Login"

### What You'll See
After logging in as Super Admin, you will see:
- **Dashboard** - Your main control center
- **Masters** - Contains all management options
  - All Employees
  - Tenant Management
  - Company Management

---

## Dashboard Overview

### Statistics Cards

#### 1. Total Tenants
- Shows total number of tenants in the system
- Displays count of active tenants
- Click to view tenant list

#### 2. Total Companies
- Shows all companies across all tenants
- Useful for understanding system scale

#### 3. Total Users
- Count of all users in the system
- Includes all roles across all tenants

#### 4. Active Employees
- Currently active employees
- Excludes inactive/terminated employees

### Charts

#### Users by Company Chart
- **Type:** Bar Chart
- **Shows:** Number of users in each company
- **Use:** Identify which companies have most users
- **Hover:** See exact count for each company

#### Payslips Generated Trend
- **Type:** Line Chart
- **Shows:** Monthly payslip generation trend
- **Use:** Track payroll processing activity
- **Hover:** See exact count for each month

### Financial Summary

#### Monthly Revenue
- Expected revenue for current month
- Based on tenant payment configurations
- Calculated from monthly charges

#### Quarterly Revenue
- Expected revenue for current quarter
- Sum of 3 months of charges

#### Yearly Revenue
- Expected annual revenue
- Sum of 12 months of charges

### Recent Tenants Table
- Shows last 5 tenants created
- Displays: Code, Name, Companies Count, Status
- Quick access to tenant details

---

## Tenant Management

### Accessing Tenant Management
1. Click **Masters** in the menu
2. Select **Tenant Management**

### Creating a New Tenant

#### Step 1: Open Create Form
- Click the **"Add Tenant"** button (top right)

#### Step 2: Fill in Details
1. **Tenant Name*** (Required)
   - Enter the full name of the tenant organization
   - Example: "Acme Corporation"

2. **Tenant Code*** (Required)
   - Enter a unique identifier
   - Use uppercase letters
   - Example: "ACME"

3. **Description** (Optional)
   - Add any relevant notes about the tenant
   - Example: "Manufacturing company based in Singapore"

4. **Country*** (Required)
   - Select from dropdown:
     - Singapore (SG)
     - Malaysia (MY)
     - India (IN)
     - United States (US)
     - United Kingdom (GB)
     - Australia (AU)
     - Canada (CA)
     - United Arab Emirates (AE)
     - Japan (JP)
     - China (CN)

5. **Currency** (Auto-filled)
   - Automatically populated based on country selection
   - Read-only field
   - Examples:
     - Singapore → SGD
     - Malaysia → MYR
     - India → INR

6. **Active** (Checkbox)
   - Check to make tenant active immediately
   - Uncheck to create as inactive

#### Step 3: Save
- Click **"Save Tenant"** button
- Wait for confirmation message
- Page will reload showing new tenant

### Viewing Tenant Details
1. Find the tenant in the table
2. Click the **eye icon** (👁️) in Actions column
3. View tenant information and associated companies

### Editing a Tenant
1. Find the tenant in the table
2. Click the **edit icon** (✏️) in Actions column
3. Modify the required fields
4. Save changes

### Deleting a Tenant
⚠️ **Warning:** This action cannot be undone!

1. Find the tenant in the table
2. Click the **delete icon** (🗑️) in Actions column
3. Confirm deletion in the popup
4. **Note:** This will also delete:
   - All companies under this tenant
   - All employees in those companies
   - All associated data

---

## Payment Configuration

### Understanding Payment Types

#### 1. Fixed Payment
- Tenant pays a fixed amount regardless of user count
- Suitable for small organizations with predictable costs
- Components:
  - **Implementation Charges:** One-time setup fee
  - **Monthly Charges:** Recurring monthly fee
  - **Other Charges:** Additional fees (support, maintenance, etc.)

#### 2. User-Based Payment
- Tenant pays based on number of active users
- Suitable for growing organizations
- Charges scale with user count

### Payment Frequency Options
- **Monthly:** Billed every month
- **Quarterly:** Billed every 3 months
- **Half-Yearly:** Billed every 6 months
- **Yearly:** Billed annually (often with discount)

### Creating Payment Configuration

#### Step 1: Access Payment Config
1. Navigate to **Masters** → **Tenant Management**
2. Select the tenant
3. Go to Payment Configuration section

#### Step 2: Set Payment Type
- Choose **Fixed** or **User-Based**

#### Step 3: Enter Charges (for Fixed)
1. **Implementation Charges**
   - One-time setup cost
   - Example: $5,000

2. **Monthly Charges**
   - Recurring monthly fee
   - Example: $500/month

3. **Other Charges**
   - Additional fees
   - Example: $100/month for support

#### Step 4: Select Frequency
- Choose billing cycle
- Consider offering discounts for longer commitments

#### Step 5: Save Configuration
- Click **Save**
- Configuration will be used in financial calculations

### Viewing Payment Configurations
- Access via API: `GET /api/tenant-payment-configs`
- View in dashboard financial summary
- See impact on revenue projections

---

## Document Management

### Supported Document Types
- Contracts
- Agreements
- Licenses
- Certificates
- Any relevant tenant documentation

### Uploading Documents

#### Step 1: Access Tenant
1. Go to **Masters** → **Tenant Management**
2. Click on the tenant name

#### Step 2: Upload Document
1. Find the **Documents** section
2. Click **"Upload Document"** button
3. Select file from your computer
4. Click **"Upload"**
5. Wait for confirmation

### Document Information Stored
- **File Name:** Original filename
- **File Path:** Server storage location
- **Uploaded By:** Your user ID
- **Upload Date:** Timestamp of upload

### Downloading Documents
1. Navigate to tenant documents
2. Find the document in the list
3. Click **"Download"** button
4. File will download to your computer

### Deleting Documents
⚠️ **Warning:** This action cannot be undone!

1. Navigate to tenant documents
2. Find the document in the list
3. Click **"Delete"** button
4. Confirm deletion
5. File will be removed from server and database

### Best Practices
- Use descriptive filenames
- Keep documents organized by type
- Regularly review and remove outdated documents
- Ensure sensitive documents are properly secured

---

## Employee Management

### Viewing All Employees

#### Step 1: Access Employee List
1. Click **Masters** in the menu
2. Select **All Employees**

#### Step 2: Understanding the View

**Desktop View (Table)**
Columns displayed:
- **Employee ID:** Unique identifier
- **Name:** Full name (clickable to view details)
- **Tenant Name:** Which tenant the employee belongs to
- **Company Name:** Which company within the tenant
- **Position:** Job title
- **Department:** Department name
- **Email:** Contact email
- **Type:** Employment type (Full-time, Part-time, etc.)
- **Actions:** View, Edit, Reset Password buttons

**Mobile View (Cards)**
Shows:
- Employee name and ID
- Tenant and Company names
- Position and department
- Email address
- Action menu (three dots)

### Searching Employees

#### Search Box
- Located at the top of the page
- Searches across:
  - Employee name
  - Employee ID
  - Email
  - **Tenant name** (NEW!)
  - **Company name** (NEW!)

#### Example Searches
- "John" - Finds all Johns
- "ACME" - Finds all employees in ACME tenant
- "john@example.com" - Finds by email
- "Tech Corp" - Finds all employees in Tech Corp company

### Filtering Employees

#### Department Filter
1. Use the **Department** dropdown
2. Select a specific department
3. Click **"Filter"** button
4. View filtered results

### Sorting Employees

#### How to Sort
1. Click on any column header
2. First click: Sort ascending (A→Z)
3. Second click: Sort descending (Z→A)
4. Arrow icon shows current sort direction

#### Sortable Columns
- Employee ID
- Name
- **Tenant Name** (NEW!)
- **Company Name** (NEW!)
- Position
- Department

#### Example Use Cases
- Sort by Tenant Name to group employees by tenant
- Sort by Company Name to see company distribution
- Sort by Name for alphabetical listing

### Viewing Employee Details
1. Click on employee name (or eye icon)
2. View complete employee profile
3. See employment history, documents, etc.

### Editing Employee Information
1. Click the **edit icon** (✏️)
2. Modify required fields
3. Save changes
4. Changes are logged with your user ID

### Resetting Employee Password
1. Click the **key icon** (🔑)
2. Confirm password reset
3. Temporary password is generated
4. Employee must change password on next login

### Pagination
- **20 employees per page**
- Use navigation at bottom:
  - ◀️ Previous page
  - Page numbers (click to jump)
  - ▶️ Next page

---

## Troubleshooting

### Common Issues

#### Issue: Currency not auto-populating
**Solution:**
1. Ensure you've selected a country first
2. Refresh the page if needed
3. Check that JavaScript is enabled in your browser

#### Issue: Cannot see Tenant/Company columns
**Solution:**
1. Verify you're logged in as Super Admin
2. These columns are only visible to Super Admin role
3. Log out and log back in if needed

#### Issue: Document upload fails
**Solution:**
1. Check file size (should be reasonable)
2. Ensure file name doesn't contain special characters
3. Try renaming the file
4. Check your internet connection

#### Issue: Dashboard charts not loading
**Solution:**
1. Refresh the page
2. Clear browser cache
3. Check if there's data to display
4. Try a different browser

#### Issue: Search not finding results
**Solution:**
1. Check spelling
2. Try partial search (e.g., "Acme" instead of "Acme Corporation")
3. Clear filters and try again
4. Ensure the data exists in the system

#### Issue: Cannot delete tenant
**Solution:**
1. Check if tenant has associated companies
2. You may need to delete companies first
3. Ensure you have Super Admin permissions
4. Check for any error messages

### Getting Help

#### Error Messages
- Read error messages carefully
- Note the exact error text
- Check if there are validation issues

#### Contact Support
If issues persist:
1. Note the exact steps you took
2. Take a screenshot of any errors
3. Record the date and time
4. Contact your system administrator

---

## Best Practices

### Tenant Management
1. **Use Clear Naming**
   - Use full company names for tenants
   - Use short, uppercase codes
   - Be consistent with naming conventions

2. **Regular Reviews**
   - Review tenant list monthly
   - Deactivate unused tenants
   - Update tenant information as needed

3. **Documentation**
   - Upload all relevant documents
   - Keep documents up to date
   - Remove outdated documents

### Payment Configuration
1. **Set Up Early**
   - Configure payment before tenant goes live
   - Review and confirm with finance team
   - Document any special arrangements

2. **Regular Audits**
   - Review payment configs quarterly
   - Update charges as needed
   - Ensure configurations match contracts

### Employee Management
1. **Use Search Effectively**
   - Use tenant/company filters for large datasets
   - Combine search with filters
   - Use sorting to organize results

2. **Data Accuracy**
   - Verify employee information regularly
   - Update when employees change companies
   - Deactivate terminated employees

3. **Security**
   - Reset passwords when needed
   - Monitor employee access
   - Review permissions regularly

---

## Keyboard Shortcuts

### General
- **Ctrl + F** - Search on page
- **Ctrl + R** - Refresh page
- **Esc** - Close modal/popup

### Navigation
- **Tab** - Move to next field
- **Shift + Tab** - Move to previous field
- **Enter** - Submit form

---

## Quick Reference

### Menu Structure
```
Dashboard
└── Super Admin Dashboard

Masters
├── All Employees (with Tenant & Company columns)
├── Tenant Management
│   ├── Create Tenant
│   ├── Edit Tenant
│   ├── Payment Configuration
│   └── Document Management
└── Company Management
```

### Key Features
- ✅ View all tenants, companies, and employees
- ✅ Create and manage tenants with country/currency
- ✅ Configure payment plans per tenant
- ✅ Upload and manage tenant documents
- ✅ View employees with tenant and company context
- ✅ Sort and filter across all data
- ✅ Comprehensive dashboard with charts and metrics

---

## Glossary

**Tenant:** A top-level organization in the system (e.g., a client company)

**Company:** A sub-organization within a tenant (e.g., a subsidiary or branch)

**Employee:** A user associated with a specific company

**Payment Configuration:** Billing setup for a tenant

**Implementation Charges:** One-time setup fee

**Monthly Charges:** Recurring monthly subscription fee

**Frequency:** How often the tenant is billed

**Super Admin:** Highest level of access, manages all tenants

**Active Status:** Whether a tenant/employee is currently operational

---

## Support Information

**Application:** HRMS (Human Resource Management System)  
**Module:** Super Admin  
**Version:** 1.0  

For technical support or questions:
- Contact your system administrator
- Refer to the technical documentation
- Check the troubleshooting section above

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Prepared For:** Super Admin Users