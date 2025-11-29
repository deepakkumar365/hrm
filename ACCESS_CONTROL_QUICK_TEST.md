# Access Control Form - Quick Test Checklist

## ⏱️ 5-Minute Verification Test

### Step 1: Login
```
□ Login as: HR Manager
□ Go to: Masters → Access Control
□ Expected: Page loads successfully
```

### Step 2: Verify User Dropdown
```
□ Check: "Tenant Users Only" badge visible ✓
□ Check: Help text says "from your tenant only" ✓
□ Check: Only users from your tenant listed
□ Check: Your own username is NOT in the list
□ Check: If no users → warning message shows ✓
```

### Step 3: Select a User
```
□ Click dropdown and select any user
□ Wait for page to update
□ Company dropdown should become ENABLED
```

### Step 4: Verify Company Dropdown
```
□ Check: "Tenant Companies Only" badge visible ✓
□ Check: Help text mentions tenant companies ✓
□ Check: Only companies from your tenant listed
□ Check: Only shows companies NOT assigned to selected user
```

### Step 5: Add a Company
```
□ Select a company from dropdown
□ Click "Add" button
□ Observe: Success message appears ✓
□ Observe: Company appears in table below ✓
□ Observe: Counter increases by 1 ✓
```

### Step 6: Verify in Table
```
□ Company name visible
□ Timestamp (Added On) visible
□ Remove button present
□ Only shows companies from your tenant
```

### Step 7: Remove Company
```
□ Click "Remove" button
□ Observe: Success message
□ Company disappears from table
□ Counter decreases by 1
□ Company reappears in dropdown
```

## ✅ What Should Happen

| Action | Result |
|--------|--------|
| Load page as HR Manager | Show only tenant users + companies |
| Select user | Populate available companies from tenant |
| Click Add | Add company to user with timestamp |
| Click Remove | Remove company from user |
| Check badges | "Tenant Users Only" and "Tenant Companies Only" visible |
| Check help text | Mentions tenant filtering scope |

## ❌ What Should NOT Happen

| Issue | Status |
|-------|--------|
| Users from other tenants visible | ❌ BLOCKED |
| Companies from other tenants visible | ❌ BLOCKED |
| Can add company from wrong tenant | ❌ BLOCKED |
| API returns cross-tenant data | ❌ BLOCKED |
| Error 403 on cross-tenant access | ✓ EXPECTED |

## 🆘 If Something Goes Wrong

| Problem | Fix |
|---------|-----|
| Empty user dropdown | Check if organization has tenant assigned |
| Empty company dropdown | Create companies in your tenant first |
| See users from other tenants | Verify organization.tenant_id is set |
| See companies from other tenants | Verify company.tenant_id matches your tenant |
| API returns 403 | This is CORRECT - tenant validation working |

## 📊 Verification Results

| Item | Pass/Fail |
|------|-----------|
| Tenant users only shown | ☐ PASS ☐ FAIL |
| Tenant companies only shown | ☐ PASS ☐ FAIL |
| Badges visible | ☐ PASS ☐ FAIL |
| Help text visible | ☐ PASS ☐ FAIL |
| Add company works | ☐ PASS ☐ FAIL |
| Remove company works | ☐ PASS ☐ FAIL |
| Cannot add from wrong tenant | ☐ PASS ☐ FAIL |
| API returns 403 on cross-tenant | ☐ PASS ☐ FAIL |

## 🎬 Expected Flow

```
1. HR Manager logs in
        ↓
2. Opens Access Control page
        ↓
3. Sees "Tenant Users Only" badge ✓
        ↓
4. Selects user from dropdown (tenant-filtered)
        ↓
5. Sees "Tenant Companies Only" badge ✓
        ↓
6. Company dropdown populated (tenant-filtered)
        ↓
7. Selects company and clicks "Add"
        ↓
8. Company appears in table with timestamp
        ↓
9. Can remove company if needed
```

## 🔐 Security Checks

```
✓ HR Manager sees only their tenant's users
✓ HR Manager sees only their tenant's companies
✓ Cannot add company from another tenant
✓ Cannot remove company from another tenant
✓ API calls verify tenant (return 403 if unauthorized)
✓ Cross-tenant access is prevented
```

---

**Test Complete! All checks pass = ✅ Fixed**
