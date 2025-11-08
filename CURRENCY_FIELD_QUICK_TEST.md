# 🧪 Quick Testing Guide - Currency Code Field

## ✅ What Was Added

Currency code field is now available in all company forms:
- ✅ **Add Company** form
- ✅ **Edit Company** form  
- ✅ **Company Details** view (edit modal)

---

## 🚀 Quick Test (5 minutes)

### Test 1: Add New Company with Currency ⭐
**File:** `templates/masters/companies.html`

1. Open browser and go to: `http://localhost:5000/companies`
2. Click **"Add Company"** button
3. Fill in form:
   - Company Code: `TEST-SGD`
   - Company Name: `Test Company`
   - **Currency Code:** ← **Select "SGD - Singapore Dollar"**
   - Other fields: Optional
4. Click **"Save Company"**
5. ✅ Company should appear in the list

**Expected Result:** Company saved with SGD currency

---

### Test 2: Edit Company Currency ⭐
**File:** `templates/masters/companies.html`

1. In the companies list, click the **Edit** button (pencil icon)
2. The modal should open
3. **Verify:** Currency Code dropdown shows current currency (SGD or whatever was set)
4. Change currency: **Select "USD - US Dollar"**
5. Click **"Update Company"**
6. ✅ Page reloads with updated data

**Expected Result:** Currency updates to USD

---

### Test 3: View Tenant Companies with Currency
**File:** `templates/masters/tenant_view.html`

1. Go to: `http://localhost:5000/tenants`
2. Click on any tenant
3. In the **Companies** section, click **"Add Company"** button
4. Fill form and **select a currency**
5. Click **"Save Company"**
6. ✅ Company appears in the list

**Expected Result:** Currency field works in tenant view

---

### Test 4: Company Details Page ⭐
**File:** `templates/masters/company_view.html`

1. Go to: `http://localhost:5000/companies`
2. Click **View** button (eye icon) on any company
3. In Company Information card, look for **"Currency Code (Payroll)"** row
4. ✅ Should show the currency code (e.g., SGD)
5. Click **"Edit"** button
6. Currency dropdown should open with current value selected
7. Change currency and click **"Update Company"**
8. ✅ Currency updates and shows in details

**Expected Result:** Currency displays and can be edited

---

## 📋 Verification Checklist

### UI Elements Present ✓
- [ ] Add Company modal has Currency Code field
- [ ] Edit Company modal has Currency Code field  
- [ ] Currency field is a dropdown with options
- [ ] All 10 currencies visible: SGD, USD, EUR, GBP, INR, MYR, THB, IDR, PHP, VND
- [ ] Currency field is marked as required (*)

### Functionality Works ✓
- [ ] Can add company with currency selection
- [ ] Currency saves to database
- [ ] Can edit company and change currency
- [ ] Updated currency displays correctly
- [ ] Default value is SGD when not selected
- [ ] Tenant Admin can manage currencies

### Data Displays Correctly ✓
- [ ] Company view shows currency code
- [ ] Currency displays in badge format
- [ ] Edit form pre-fills with current currency
- [ ] Dropdown maintains selection after edit

---

## 🎯 Expected Behavior

### When Adding Company:
```
1. User fills form
2. Selects currency from dropdown
3. Clicks "Save Company"
4. API creates company with currency_code
5. Company appears in list
6. Currency saved in database ✓
```

### When Editing Company:
```
1. User clicks Edit button
2. Form loads with current currency selected
3. User can change currency
4. Clicks "Update Company"
5. API updates company with new currency_code
6. List refreshes with updated data ✓
```

---

## 🐛 Troubleshooting

### Problem: Currency dropdown not showing
**Solution:** 
- Clear browser cache (Ctrl+Shift+Del)
- Refresh page (Ctrl+F5)
- Restart Flask application

### Problem: Currency field missing in form
**Solution:**
- Check if file was saved: Look for `companyCurrencyCode` in HTML
- Verify all three files updated:
  - ✅ companies.html
  - ✅ tenant_view.html (already had it)
  - ✅ company_view.html

### Problem: Currency not saving
**Solution:**
- Check browser console for errors (F12)
- Verify database has currency_code column:
  ```sql
  SELECT * FROM information_schema.columns 
  WHERE table_name='hrm_company' 
  AND column_name='currency_code';
  ```
- Check Flask logs for API errors

---

## ✅ Success Criteria

You'll know it's working when:

1. ✅ Add company form shows currency dropdown
2. ✅ Can select currency and save company
3. ✅ Company displays with selected currency
4. ✅ Can edit company and change currency
5. ✅ Currency persists after page reload
6. ✅ Tenant Admin can manage all of the above

---

## 📊 Files Modified

| File | Changes | Type |
|------|---------|------|
| companies.html | Added currency fields + JS | Template |
| company_view.html | Added currency field + JS | Template |
| tenant_view.html | Already had currency field | Template |
| routes_tenant_company.py | Already supports currency | Backend |

---

## 🎨 UI Preview

### Add/Edit Form Layout:
```
Address          [Text area for address...]
┌─────────────────────────────────────┐
│ Currency Code * │                   │
│ ┌─────────────────────────────────┐ │
│ │ Select Currency                 │ │
│ │ ✓ SGD - Singapore Dollar        │ │
│ │ - USD - US Dollar               │ │
│ │ - EUR - Euro                    │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
Active [✓]
[Cancel] [Save/Update]
```

---

## 🚀 Next Steps

After confirming everything works:

1. Test with different currencies
2. Test Tenant Admin access
3. Verify currency reflects in payroll calculations
4. Test API responses (F12 → Network tab)
5. Deploy to production

---

## 📞 Support

If currency field doesn't appear:
1. Verify files saved correctly
2. Clear browser cache
3. Restart Flask app
4. Check browser console (F12) for errors
5. Look at Flask logs for API issues

**Files to check:**
- ✅ D:/Projects/HRMS/hrm/templates/masters/companies.html
- ✅ D:/Projects/HRMS/hrm/templates/masters/company_view.html  
- ✅ D:/Projects/HRMS/hrm/templates/masters/tenant_view.html
