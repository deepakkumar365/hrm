# 📊 HRM Database Export Summary

**Exported:** 2025-10-29 01:20:58  
**Total Tables:** 24 HRM tables  
**Total Rows:** 426 rows  
**File:** `EXPORTED_DATA.sql`

---

## 📋 Tables & Data Summary

| Table Name | Rows | Description |
|---|---|---|
| **role** | 4 | User roles (Super Admin, Tenant Admin, HR Manager, User) |
| **hrm_tenant** | 1 | Tenant: AKS Group of Companies (Singapore) |
| **hrm_company** | 2 | Companies: AKS BUSINESS SOLUTIONS, AKS LOGISTICS |
| **organization** | 1 | Organization: AKS LOGISTICS PTE LTD |
| **hrm_users** | 8 | Users including admin, tenant admin, manager, employees |
| **hrm_employee** | 14 | Employee records with salary, designation, position |
| **hrm_designation** | 25 | Job designations (Director, Manager, Driver, etc.) |
| **hrm_working_hours** | 4 | Working hour configurations |
| **hrm_work_schedules** | 4 | Work schedules (Morning, Evening, Night shifts) |
| **hrm_employee_bank_info** | 0 | (Empty) |
| **hrm_employee_documents** | 0 | (Empty) |
| **hrm_payroll** | 8 | Payroll records |
| **hrm_payroll_configuration** | 14 | Payroll configuration settings |
| **hrm_attendance** | 270 | Attendance records |
| **hrm_leave** | 9 | Leave applications |
| **hrm_claim** | 0 | (Empty) |
| **hrm_appraisal** | 0 | (Empty) |
| **hrm_roles** | 8 | Additional role configurations |
| **hrm_departments** | 6 | Departments (Operations, Administration, etc.) |
| **hrm_compliance_report** | 0 | (Empty) |
| **hrm_tenant_payment_config** | 1 | Tenant payment configuration |
| **hrm_role_access_control** | 47 | Role-based access control matrix |
| **hrm_user_role_mapping** | 0 | (Empty) |
| **hrm_tenant_documents** | 0 | (Empty) |

---

## 👥 Key Data

### Users (8 total)
- **superadmin** - superadmin@hrm.com (Super Admin role)
- **tenantadmin** - tenantadmin@hrm.com (Tenant Admin role)
- **manager** - manager@hrm.com (HR Manager role)
- **employee** - employee@hrm.com (Regular Employee role)
- Plus 4 additional employees

### Employees (14 total)
- Sashikumar Asogan (Manager, Operations)
- Shalini Suraesh (Manager, Administration)
- Ram Kumar Murugasu (Manager, Administration)
- Neelakanan Suparamaniam (User, Operations)
- Muhammad Hafiz Bin Kamsan (User, Operations)
- Ang Chye Hock Andrew (Admin, Administration)
- Plus 8 more employees with various positions

### Attendance Records (270 total)
- Complete attendance tracking with clock-in/clock-out times
- Regular hours, overtime, and total hours recorded

### Payroll (8 records)
- Payroll processing with salary, allowances, deductions
- Employee CPF contributions (20% employee, 17% employer)

---

## 🔑 Test Login Credentials

From the exported data, you can use:
- **Username:** superadmin
- **Email:** superadmin@hrm.com
- **Password:** (check the scrypt hash in exported file)

Or:
- **Username:** tenantadmin
- **Email:** tenantadmin@hrm.com

Or:
- **Username:** manager
- **Email:** manager@hrm.com

---

## 📁 File Location

```
c:\Repo\hrm\EXPORTED_DATA.sql
```

---

## ✅ How to Use

### Option 1: Import in pgAdmin
1. Create a new database: `hrm_db`
2. Open Query Tool
3. Copy & paste content of `EXPORTED_DATA.sql`
4. Execute (F5)

### Option 2: Command Line
```bash
psql -U your_user -d hrm_db -f c:\Repo\hrm\EXPORTED_DATA.sql
```

### Option 3: Restore to Production
```bash
psql -h your_host -U your_user -d your_database -f EXPORTED_DATA.sql
```

---

## 📊 Organization Hierarchy

```
Tenant: AKS Group of Companies (SG)
  ├── Company 1: AKS BUSINESS SOLUTIONS PTE LTD
  ├── Company 2: AKS LOGISTICS PTE LTD
  └── Organization: AKS LOGISTICS PTE LTD
        ├── Users (8)
        ├── Employees (14)
        └── Records (payroll, attendance, leave, etc.)
```

---

## 🔐 Data Privacy Notes

- Password hashes are scrypt encrypted (secure)
- All personal identifiable information is included
- Sensitive data: NRIC, DOB, bank details, CPF rates
- This data should be handled as confidential

---

## 📝 Next Steps

1. **Backup** - Keep `EXPORTED_DATA.sql` as a safe backup
2. **Import** - Run this into your development/test database
3. **Verify** - Check all tables imported successfully
4. **Test** - Log in with exported user accounts
5. **Deploy** - Use for production migration if needed

---

Generated: 2025-10-29 01:20:58 UTC