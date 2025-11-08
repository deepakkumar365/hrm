# Company Currency Code - UI Visual Guide

## 📱 User Interface Changes

### 1. Add Company Modal

**Before:**
```
┌─────────────────────────────────────────┐
│ Add New Company                    [×]  │
├─────────────────────────────────────────┤
│ Company Code *        │ Company Name *  │
│ [___________]         │ [____________]  │
│                                         │
│ Description                             │
│ [_____________________]                 │
│                                         │
│ UEN (Singapore) [___] │ Phone [____]    │
│ Email [____________]   │ Website [...] │
│                                         │
│ Address                                 │
│ [_____________________]                 │
│                                         │
│ ☑ Active                                │
├─────────────────────────────────────────┤
│ [Cancel]                       [Save]  │
└─────────────────────────────────────────┘
```

**After (NEW):**
```
┌─────────────────────────────────────────┐
│ Add New Company                    [×]  │
├─────────────────────────────────────────┤
│ Company Code *        │ Company Name *  │
│ [___________]         │ [____________]  │
│                                         │
│ Description                             │
│ [_____________________]                 │
│                                         │
│ UEN (Singapore) [___] │ Phone [____]    │
│ Email [____________]   │ Website [...] │
│                                         │
│ 🆕 Currency Code * (for Payroll)       │
│ [▼ -- Select Currency --]              │
│     SGD (Singapore Dollar)              │
│     USD (US Dollar)                     │
│     EUR (Euro)                          │
│     GBP (British Pound)                 │
│     INR (Indian Rupee)                  │
│     MYR (Malaysian Ringgit)             │
│     THB (Thai Baht)                     │
│     IDR (Indonesian Rupiah)             │
│     PHP (Philippine Peso)               │
│     VND (Vietnamese Dong)               │
│ Used for all payroll calculations       │
│                                         │
│ Address                                 │
│ [_____________________]                 │
│                                         │
│ ☑ Active                                │
├─────────────────────────────────────────┤
│ [Cancel]                       [Save]  │
└─────────────────────────────────────────┘
```

---

### 2. Edit Company Modal

**New Section Added:**
```
┌─────────────────────────────────────────┐
│ Edit Company                       [×]  │
├─────────────────────────────────────────┤
│ [Existing fields...]                    │
│                                         │
│ 🆕 Currency Code * (for Payroll)       │
│ [▼ USD (US Dollar)]                    │
│ Used for all payroll calculations       │
│                                         │
│ [Rest of form...]                       │
├─────────────────────────────────────────┤
│ [Cancel]                      [Update] │
└─────────────────────────────────────────┘
```

---

### 3. Company View / Details Page

**Company Information Section:**
```
┌─────────────────────────────────┐
│ Company Information      [Edit] │
├─────────────────────────────────┤
│ Company Name:      ACME USA     │
│ Company Code:      [ACME-US]    │
│ Tenant:            Multi Corp   │
│ Description:       USA Office   │
│ UEN (Singapore):   N/A          │
│ 🆕 Currency Code:  [USD]        │ ← NEW DISPLAY
│ Status:            [Active]     │
│                                 │
│ Phone:             +1-234-567   │
│ Email:             usa@acme.com │
│ Website:           www.acme.com │
│ Address:           123 Main St  │
│ Created:           23 Jan 2025  │
│ Created By:        admin        │
└─────────────────────────────────┘
```

---

### 4. Companies Table (In Tenant View)

**Table now displays currency info:**

**Before:**
```
Code | Name                | UEN      | Location    | Status  | Emp.
-----|---------------------|----------|-------------|---------|-----
ACME | ACME Singapore      | ABC1234  | Singapore   | Active  | 45
US   | ACME USA           | N/A      | New York    | Active  | 23
IN   | ACME India         | N/A      | Bangalore   | Active  | 67
```

**After (Companies table shows currency in modal form):**
```
Code | Name                | UEN      | Location    | Status  | Emp.
-----|---------------------|----------|-------------|---------|-----
ACME | ACME Singapore      | ABC1234  | Singapore   | Active  | 45
US   | ACME USA           | N/A      | New York    | Active  | 23
IN   | ACME India         | N/A      | Bangalore   | Active  | 67

[Edit Company shows currency selector]
```

---

## 🔄 Step-by-Step User Workflow

### Creating a Multi-Currency Company

#### Step 1: Click "Add Company"
```
Tenants → Select Tenant → [Add Company Button]
```

#### Step 2: Fill Form with Currency Selection
```
┌─────────────────────────┐
│ Company Code: ACME-JP   │
│ Company Name: ACME JP   │
│ ...other fields...      │
│                         │
│ Currency: [▼ JPY]       │ ← SELECT HERE
│                         │
│ [Save Company]          │
└─────────────────────────┘
```

#### Step 3: View Company Details
```
Company View shows:
- Code: ACME-JP
- Currency: [JPY] ← DISPLAYS HERE
```

---

## 💡 Dropdown Options

**When user clicks currency dropdown:**

```
Select Currency
──────────────────────────────────────
⟨ -- Select Currency --              (required)
─────────────────────────────────────
  SGD (Singapore Dollar)              ← Default
  USD (US Dollar)
  EUR (Euro)
  GBP (British Pound)
  INR (Indian Rupee)
  MYR (Malaysian Ringgit)
  THB (Thai Baht)
  IDR (Indonesian Rupiah)
  PHP (Philippine Peso)
  VND (Vietnamese Dong)
```

---

## 🎨 Visual Elements

### Currency Badge in Company View
```
Currency Code (Payroll): [SGD]  ← Blue badge
                         ^^^^^
                    Shows currency clearly
```

### Required Field Indicator
```
Currency Code * (for Payroll)  ← Red asterisk (*) = required
                ↑
         Visual indicator
```

### Help Text
```
Currency Code * (for Payroll)
[Select from dropdown]
Used for all payroll calculations    ← Helper text in gray
```

---

## ✨ Enhanced Information Display

### In Tenant's Company List
When users view a tenant, they see:
- Company Code
- Company Name  
- UEN
- Location
- Status (Active/Inactive)
- Employee Count
- **Currency** (in edit modal when clicked)

### In Company Details Page
```
┌──────────────────────────────┐
│ Company Information          │
├──────────────────────────────┤
│ Name:     ACME Pte Ltd       │
│ Code:     [ACME]             │
│ Currency: [SGD] ← HERE!      │
│ Tenant:   XYZ Group          │
│ Status:   [Active]           │
│ ...more details...           │
└──────────────────────────────┘
```

---

## 🔌 Integration with Payroll

Once currency is set in company:

### Payroll Module Uses It:
```
Company: ACME-US
Currency: USD

Employee Salary Setup:
- Base Salary: 5000 USD
- Allowances: 1000 USD
- Deductions: 500 USD

Payslip Shows:
┌────────────────────┐
│ Salary Component   │ USD
├────────────────────┤
│ Base Salary        │ 5000.00
│ Allowances         │ 1000.00
│ Deductions         │-500.00
├────────────────────┤
│ NET PAY            │ 5500.00
│                    │ (USD)    ← Currency shown
└────────────────────┘
```

---

## 🛡️ Validation & Error Handling

### If Currency Not Selected:
```
✗ Currency Code is required
  [Please select a currency from the dropdown]
```

### If Form Submitted Successfully:
```
✓ Company created successfully!
  [Automatic page reload]
```

### If Currency Change on Existing Company:
```
Company: ACME-SG
Previous Currency: SGD
New Currency: USD

✓ Currency updated successfully!
  Note: Affects future payroll only
```

---

## 📊 Data Display Examples

### Example 1: Singapore Company
```
Company Code: ACME
Name: ACME Singapore Pte Ltd
Currency: [SGD] ← Singapore Dollar
Status: Active
Employees: 45
```

### Example 2: US Company
```
Company Code: ACME-US
Name: ACME USA Inc
Currency: [USD] ← US Dollar
Status: Active
Employees: 23
```

### Example 3: India Company
```
Company Code: ACME-IND
Name: ACME India Pvt Ltd
Currency: [INR] ← Indian Rupee
Status: Active
Employees: 67
```

---

## ⌨️ Keyboard Navigation

Users can:
1. Tab to currency field
2. Press Space or Down Arrow to open dropdown
3. Use Arrow Keys to select currency
4. Press Enter to confirm selection
5. Tab to next field

---

## 🖱️ Mouse Interaction

Users can:
1. Click on dropdown to open options
2. Hover over option to highlight
3. Click option to select
4. Click outside to close dropdown

---

## 📱 Responsive Design

**Desktop (>768px):**
```
Currency field takes 50% width in row:
[Currency Code (50%)] [Empty (50%)]
```

**Tablet (768px):**
```
Currency field still in row:
[Currency Code (50%)] [Empty (50%)]
```

**Mobile (<576px):**
```
Currency field full width:
[Currency Code (100%)]
```

---

## ♿ Accessibility Features

- ✅ Form label for currency field
- ✅ Required field indicator (*)
- ✅ Helper text describes usage
- ✅ Keyboard accessible dropdown
- ✅ Screen reader friendly
- ✅ Proper ARIA labels

---

## 🎯 Summary of UI Changes

| Element | Location | Change |
|---------|----------|--------|
| Add Company Form | Modal | + Currency dropdown (required) |
| Edit Company Form | Modal | + Currency dropdown (required) |
| Company View | Details Page | + Currency badge display |
| Dropdown Options | Both Forms | 10 common currencies |
| Helper Text | Forms | "Used for all payroll calculations" |
| Badge Style | Details | Blue background, clear display |

---

## ✅ Test Scenarios

### Scenario 1: Create Company with Currency
1. Open Tenant View
2. Click "Add Company"
3. Fill in: Code, Name
4. **Select Currency: USD**
5. Click "Save Company"
6. ✓ Currency displays as [USD] in company view

### Scenario 2: Change Company Currency
1. Open Tenant View
2. Click Edit (pencil icon)
3. **Change Currency: SGD → EUR**
4. Click "Update Company"
5. ✓ Currency updates to [EUR]

### Scenario 3: View Company Currency
1. Open Tenant View
2. Click company name (view)
3. ✓ Currency Code displayed with badge

---

**All UI changes are backward compatible and intuitive for end users!**