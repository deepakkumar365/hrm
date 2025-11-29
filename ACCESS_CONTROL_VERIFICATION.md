# Access Control Form Verification & Testing Guide

## ✅ FIXES APPLIED

### Issue 1: User Selection Dropdown - Now Filters by Tenant
**Problem:** HR Manager could see ALL users in the system.  
**Solution:** Modified `manage_user_companies()` to filter users by tenant.

- ✅ Super Admin: Sees all users (except ID 1)
- ✅ HR Manager / Tenant Admin: Sees only users from their tenant
- ✅ Current user is excluded from the list

**Code:** `routes_access_control.py` lines 639-685

---

### Issue 2: Companies Dropdown - Now Filters by Tenant
**Problem:** All companies in the system were shown.  
**Solution:** Modified `get_available_companies()` to filter companies by tenant.

- ✅ Super Admin: Sees all available companies
- ✅ HR Manager / Tenant Admin: Sees only companies from their tenant
- ✅ Only shows companies NOT already assigned to the user
- ✅ Added tenant verification for security

**Code:** `routes_access_control.py` lines 851-897

---

### Issue 3: Security - Added Tenant Verification
**All API endpoints now verify tenant access:**

| Endpoint | Security Added |
|----------|----------------|
| `api/user-companies/<user_id>` | Verifies user is in same tenant |
| `api/get-available-companies/<user_id>` | Verifies user and companies are in same tenant |
| `api/add-company-to-user` | Verifies user and company are in same tenant |
| `api/remove-company-from-user` | Verifies user and company are in same tenant |

---

### Issue 4: Template - Added Visual Clarity
**Changes made:**
- Added "Tenant Users Only" badge on Select User field
- Added "Tenant Companies Only" badge on Add Company field
- Added help text explaining filtering behavior
- Added warning message when no users are available in tenant
- Updated section title to "Companies Assigned to Selected User (From your tenant)"

**Code:** `templates/access_control/manage_user_companies.html`

---

## 📋 STEP-BY-STEP VERIFICATION TEST

### **Test Case 1: HR Manager Access Control**

**Setup Required:**
- 1 Tenant (e.g., "ACME Corp")
- 2 Companies under Tenant (e.g., "ACME USA", "ACME UK")
- 1 Organization linked to Tenant
- 2+ Users in the Organization
- 1 HR Manager user

**Test Steps:**

1. **Login as HR Manager**
   ```
   - Username: [hr_manager_username]
   - Password: [password]
   ```

2. **Navigate to Masters > Access Control**
   ```
   Path: /access-control/manage-user-companies
   ```

3. **Verify User Selection Dropdown**
   ```
   ✓ EXPECTED: Only users from your tenant are listed
   ✓ EXPECTED: Current user (HR Manager) is excluded
   ✓ EXPECTED: Other roles from same tenant are shown
   ✓ INFO BADGE: "Tenant Users Only" is visible
   ```

4. **Select a User from Dropdown**
   ```
   - Choose any non-HR-Manager user
   - Observe the form updates
   ```

5. **Verify Companies Dropdown Populates**
   ```
   ✓ EXPECTED: Company Select field is now ENABLED
   ✓ EXPECTED: Shows only companies from your tenant
   ✓ EXPECTED: Shows only companies NOT already assigned to selected user
   ✓ INFO BADGE: "Tenant Companies Only" is visible
   ```

6. **Select a Company and Click "Add"**
   ```
   - Choose a company from dropdown
   - Click "Add" button
   ```

7. **Verify Success Message**
   ```
   ✓ EXPECTED: Success toast appears
   ✓ MESSAGE: "Company [name] added to [username] successfully"
   ```

8. **Verify Company Appears in List**
   ```
   ✓ EXPECTED: New company appears in "Companies Assigned to Selected User" table
   ✓ EXPECTED: Company shows with timestamp "Added On"
   ✓ EXPECTED: "Remove" button is available
   ✓ COUNTER: "Companies for Selected User" count increases
   ```

9. **Verify Available Count Updates**
   ```
   ✓ EXPECTED: "Available to Assign" count decreases
   ✓ EXPECTED: Company no longer appears in Company Select dropdown
   ```

10. **Test Remove Functionality**
    ```
    - Click "Remove" button on the company
    - Confirm removal in alert
    ```

11. **Verify Company is Removed**
    ```
    ✓ EXPECTED: Success message appears
    ✓ EXPECTED: Company removed from the list
    ✓ EXPECTED: "Available to Assign" count increases
    ✓ EXPECTED: Company reappears in Company Select dropdown
    ```

---

### **Test Case 2: Multi-Tenant Isolation**

**Setup Required:**
- 2 Tenants (e.g., "Tenant A", "Tenant B")
- Users in both tenants
- Companies in both tenants

**Test Steps:**

1. **Login as HR Manager from Tenant A**
2. **Navigate to Access Control**
3. **Verify Isolation:**
   ```
   ✓ User dropdown shows ONLY Tenant A users
   ✓ Company dropdown shows ONLY Tenant A companies
   ✓ Cannot see Tenant B users
   ✓ Cannot see Tenant B companies
   ```

4. **Logout and Login as HR Manager from Tenant B**
5. **Navigate to Access Control**
6. **Verify Different Data:**
   ```
   ✓ User dropdown shows ONLY Tenant B users
   ✓ Company dropdown shows ONLY Tenant B companies
   ✓ Different data than Tenant A
   ```

---

### **Test Case 3: Super Admin Access**

**Setup:** Already have 2+ Tenants with users and companies

**Test Steps:**

1. **Login as Super Admin**
2. **Navigate to Access Control**
3. **Verify Super Admin Permissions:**
   ```
   ✓ Can see users from ALL tenants
   ✓ Can see companies from ALL tenants
   ✓ Can add/remove companies for any user
   ✓ Can manage across all tenants
   ```

---

### **Test Case 4: Error Handling**

**Test Invalid Requests:**

1. **Test: User Without Tenant Assignment**
   ```
   Setup: Create user with organization that has no tenant_id
   Expected: Error message: "Your organization is not assigned to a tenant"
   ```

2. **Test: Cross-Tenant Manipulation (Manual API Call)**
   ```
   Setup: Try to add Tenant B company to Tenant A user via API
   Expected: Error 403: "Unauthorized: User and Company must be in your tenant"
   ```

3. **Test: Invalid User ID**
   ```
   API Call: GET /api/user-companies/99999
   Expected: Error 404: "User not found"
   ```

4. **Test: Duplicate Company Assignment**
   ```
   Setup: Try to add same company twice
   Expected: Error 409: "User already has access to [company]"
   ```

---

## 🔐 Security Verification Checklist

- [ ] HR Manager cannot see users from other tenants
- [ ] HR Manager cannot see companies from other tenants
- [ ] HR Manager cannot add company from another tenant to their user
- [ ] HR Manager cannot remove company from another tenant
- [ ] Cross-tenant API calls return 403 Unauthorized
- [ ] Tenant field is used instead of organization field for all filtering
- [ ] Super Admin can still access all data across all tenants

---

## 📊 Database Verification

**Run these queries to verify data structure:**

```sql
-- Verify User-Organization-Tenant relationship
SELECT u.username, u.id, o.name as organization, o.tenant_id
FROM hrm_users u
JOIN organization o ON u.organization_id = o.id
ORDER BY o.tenant_id, u.username;

-- Verify UserCompanyAccess mappings
SELECT u.username, c.name as company, c.tenant_id, uca.created_at
FROM hrm_user_company_access uca
JOIN hrm_users u ON uca.user_id = u.id
JOIN hrm_company c ON uca.company_id = c.id
ORDER BY c.tenant_id, u.username;

-- Verify companies per tenant
SELECT t.name as tenant, COUNT(c.id) as company_count
FROM hrm_tenant t
LEFT JOIN hrm_company c ON t.id = c.tenant_id
GROUP BY t.name
ORDER BY t.name;
```

---

## ✨ Expected Behavior Summary

| Role | Can See | Can Modify |
|------|---------|-----------|
| **Super Admin** | All users & companies | All mappings |
| **Tenant Admin** | Tenant users & companies | Tenant mappings |
| **HR Manager** | Tenant users & companies | Tenant mappings |
| **Employee** | Self only (if applicable) | None |

---

## 🆘 Troubleshooting

### Problem: "No users in dropdown"
- **Check:** Is the current user an HR Manager?
- **Check:** Are there other users in the same organization/tenant?
- **Check:** Is the organization linked to a tenant?
- **Solution:** Add users to the same organization and ensure tenant is linked

### Problem: "No companies in dropdown"
- **Check:** Does your tenant have any companies?
- **Solution:** Create companies in Masters > Company Configuration

### Problem: "Cross-tenant users can see each other's data"
- **Check:** Verify Organization → Tenant relationship
- **Check:** Verify both users have different tenant_ids
- **Solution:** Run database queries above to verify relationships

### Problem: API returns 403 Unauthorized
- **Expected:** This is correct if trying cross-tenant access
- **Check:** Verify tenant_ids match between user and company
- **Solution:** Add company to same tenant as user

---

## 📝 Code Changes Summary

**File: `routes_access_control.py`**

| Function | Changes | Lines |
|----------|---------|-------|
| `manage_user_companies()` | Added tenant filtering for users and companies | 639-685 |
| `get_user_companies()` | Added tenant verification | 691-701 |
| `add_company_to_user()` | Added tenant verification for user and company | 741-748 |
| `remove_company_from_user()` | Added tenant verification for user and company | 821-828 |
| `get_available_companies()` | Added tenant filtering and verification | 851-897 |

**File: `templates/access_control/manage_user_companies.html`**

| Section | Changes | Lines |
|---------|---------|-------|
| User Select Label | Added "Tenant Users Only" badge and help text | 46-68 |
| Company Select Label | Added "Tenant Companies Only" badge and help text | 71-90 |
| Companies List Title | Updated to show tenant context | 99-101 |

---

## ✅ Sign-Off Checklist

- [ ] All test cases pass
- [ ] No cross-tenant data leakage
- [ ] Security verification checks pass
- [ ] Database relationships verified
- [ ] Error messages are clear
- [ ] Help text is visible and accurate
- [ ] UI displays correct badges and context
- [ ] Performance is acceptable with large datasets
- [ ] All 5 API endpoints have tenant verification
- [ ] Super Admin functionality unchanged
