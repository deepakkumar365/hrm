# Company Currency Code - Quick Start Guide

## 🎯 What's New?
Each company now has its own **currency code** for payroll calculations.

- **Before:** All companies used the same currency
- **After:** Each company can have SGD, USD, INR, EUR, etc.

## 📋 Quick Steps

### Step 1: Apply Migration
```bash
flask db upgrade
```
✅ This adds the currency_code column to your database

### Step 2: Create/Edit Companies
- Go to **Tenants** → Select Tenant → **Add Company**
- Fill in company details
- **Select Currency Code** from dropdown (SGD, USD, EUR, INR, etc.)
- Click **Save**

### Step 3: Verify
- Go to company details to see the currency badge
- It will show next to UEN field

## 💰 Supported Currencies

| Code | Currency | Region |
|------|----------|--------|
| SGD | Singapore Dollar | Default |
| USD | US Dollar | |
| EUR | Euro | Europe |
| GBP | British Pound | UK |
| INR | Indian Rupee | India |
| MYR | Malaysian Ringgit | Malaysia |
| THB | Thai Baht | Thailand |
| IDR | Indonesian Rupiah | Indonesia |
| PHP | Philippine Peso | Philippines |
| VND | Vietnamese Dong | Vietnam |

## 🔧 How It Works

```
Company Created
    ↓
Currency Code Set (e.g., USD)
    ↓
Employee Salary Set in USD
    ↓
Payroll Calculated in USD
    ↓
Payslip Shows USD Currency
```

## ✅ Key Features

✅ **Create** - Set currency when creating company  
✅ **Edit** - Change currency anytime  
✅ **View** - See currency in company details  
✅ **Default** - Defaults to SGD if not specified  
✅ **API** - Available in all API endpoints  

## 🔗 API Usage

### Create Company with Currency
```json
POST /api/companies
{
    "tenant_id": "uuid",
    "name": "US Office",
    "code": "USOFF",
    "currency_code": "USD"
}
```

### Update Company Currency
```json
PUT /api/companies/{company_id}
{
    "currency_code": "USD"
}
```

### Response
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "code": "USOFF",
        "currency_code": "USD",
        ...
    }
}
```

## 📝 Database View

Check which companies have which currencies:
```sql
SELECT code, name, currency_code FROM hrm_company;
```

**Output:**
```
code    | name              | currency_code
--------|-------------------|---------------
ACME    | ACME Singapore    | SGD
ACME-US | ACME USA Office   | USD
ACME-IN | ACME India Office | INR
```

## ⚠️ Important Notes

1. **Default:** If no currency specified → defaults to SGD
2. **Payroll:** Currency is used for ALL payroll calculations
3. **Backward Compatible:** Existing companies work as before
4. **Case Insensitive:** You can use "sgd" or "SGD" → both work
5. **Changing:** You can change currency anytime (be careful with existing payroll!)

## 🐛 Troubleshooting

### Currency not showing after creation?
- Clear browser cache and refresh
- Check if migration was applied: `flask db current`

### Can't select currency in form?
- Make sure dropdown is visible on form
- Check browser console for JavaScript errors

### Migration failed?
- Check database connection
- Verify you're in development environment
- Run: `flask db history` to see applied migrations

## 📞 Related Features

- **Employee ID Configuration:** See `COMPANY_EMPLOYEE_ID_CONFIG.md`
- **Payroll Calculation:** Uses company currency for all amounts
- **Payslips:** Show currency in salary components
- **Reports:** Multi-currency support in payroll reports

## 🚀 Next Steps

1. ✅ Apply migration: `flask db upgrade`
2. ✅ Create test company with different currency
3. ✅ Add employees to that company
4. ✅ Generate payroll and check currency display
5. ✅ Verify payslip shows correct currency

---

**Need Help?** See `COMPANY_CURRENCY_CODE_IMPLEMENTATION.md` for detailed documentation.