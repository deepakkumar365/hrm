# Payroll Salary Slip - Testing Guide

## 🧪 Quick Test (5 Minutes)

### **Step 1: Start Application**
```bash
python main.py
```

### **Step 2: Navigate to Payslip**
1. Login as Admin/HR/Manager
2. Go to **Payroll** → **Payroll List**
3. Click **View Payslip** for any employee

### **Step 3: Visual Verification**
Check these elements appear correctly:

✅ **Company Header**
- Teal gradient background
- White text
- Company name, address, UEN visible

✅ **Title Section**
- "PAYROLL SALARY SLIP" in brown
- "Professional Template" in blue
- Teal background

✅ **Content Area**
- Soft pink background
- White cards with teal borders
- Rounded corners

✅ **Employee Info**
- Labels in teal color
- Values in gray color
- All fields populated

✅ **Pay Table**
- Teal gradient header
- White text in header
- Earnings and deductions aligned
- Totals row highlighted

✅ **Summary Section**
- Net pay row with teal gradient
- White text on net pay
- Values right-aligned

✅ **Footer**
- Wave pattern visible
- Light teal background
- Footer text centered

---

## 🔍 Detailed Testing (30 Minutes)

### **Test 1: Color Accuracy**

| Element | Expected Color | Status |
|---------|---------------|--------|
| Body background | Gradient pink/blue | [ ] |
| Company header | Gradient teal (#7BA6AA → #A5C2C4) | [ ] |
| Title text | Brown (#8A4F24) | [ ] |
| Subtitle text | Blue (#7A7CCF) | [ ] |
| Content area | Soft pink (#FBEFF1) | [ ] |
| Info card border | Teal (#A5C2C4) | [ ] |
| Table header | Gradient teal | [ ] |
| Labels | Teal (#7BA6AA) | [ ] |
| Body text | Gray (#4A4A4A) | [ ] |
| Net pay row | Gradient teal | [ ] |
| Footer wave | Light teal (#C7E3E6) | [ ] |

**Pass Criteria:** All colors match specification exactly

---

### **Test 2: Typography**

| Element | Expected Font | Size | Weight | Status |
|---------|--------------|------|--------|--------|
| Company name | Poppins | 24px | 700 | [ ] |
| Title | Poppins | 28px | 600 | [ ] |
| Subtitle | Poppins | 12px | 400 | [ ] |
| Labels | Poppins | 13px | 600 | [ ] |
| Values | Open Sans | 13px | 400 | [ ] |
| Table header | Poppins | 13px | 600 | [ ] |
| Table data | Open Sans | 13px | 400 | [ ] |
| Net pay | Poppins | 16px | 700 | [ ] |

**Pass Criteria:** Fonts load correctly, sizes and weights match

---

### **Test 3: Layout & Spacing**

| Element | Expected | Status |
|---------|----------|--------|
| Container width | 800px (desktop) | [ ] |
| Container centered | Yes | [ ] |
| Border radius | 12px (container), 8px (cards) | [ ] |
| Content padding | 30px | [ ] |
| Card padding | 20px | [ ] |
| Section margins | 20px bottom | [ ] |
| Box shadow | Visible on container | [ ] |

**Pass Criteria:** All spacing matches specification

---

### **Test 4: Data Display**

| Field | Displays Correctly | Status |
|-------|-------------------|--------|
| Company name | [ ] |
| Company address | [ ] |
| Company UEN | [ ] |
| Employee name | [ ] |
| NRIC/FIN | [ ] |
| Nationality | [ ] |
| Pay date | [ ] |
| Designation | [ ] |
| Department | [ ] |
| Regular pay | [ ] |
| Overtime pay | [ ] |
| Holiday pay | [ ] |
| Vacation pay | [ ] |
| Other earnings | [ ] |
| Income tax | [ ] |
| Medical deduction | [ ] |
| Life insurance | [ ] |
| Provident fund | [ ] |
| Other deductions | [ ] |
| Total earnings | [ ] |
| Total deductions | [ ] |
| Net pay | [ ] |

**Pass Criteria:** All data displays correctly, no missing values

---

### **Test 5: Responsive Design**

#### **Desktop (1920x1080)**
- [ ] Container is 800px wide
- [ ] All sections visible
- [ ] Proper spacing maintained
- [ ] Fonts are readable

#### **Laptop (1366x768)**
- [ ] Container is 800px wide
- [ ] Layout intact
- [ ] No horizontal scroll
- [ ] All content visible

#### **Tablet (768x1024)**
- [ ] Container is 100% width
- [ ] Font sizes reduced appropriately
- [ ] Table remains readable
- [ ] No overflow

#### **Mobile (375x667)**
- [ ] Container is 100% width
- [ ] Compact layout active
- [ ] Font sizes: Title 22px, Company 20px
- [ ] Table padding reduced to 6px
- [ ] All content accessible

**Pass Criteria:** Layout adapts correctly to all screen sizes

---

### **Test 6: Print Functionality**

#### **Print Preview (Ctrl+P / Cmd+P)**
- [ ] Background colors visible (enable "Background graphics")
- [ ] No box shadow in print
- [ ] No border radius in print
- [ ] Full width layout
- [ ] All content fits on one page
- [ ] Colors print correctly
- [ ] Fonts render properly
- [ ] No elements cut off

#### **PDF Export**
- [ ] Generate PDF from print dialog
- [ ] Colors preserved in PDF
- [ ] Fonts embedded correctly
- [ ] Layout intact
- [ ] File size reasonable (<500KB)
- [ ] PDF opens in all viewers

**Pass Criteria:** Print and PDF export work perfectly

---

### **Test 7: Browser Compatibility**

#### **Chrome (Latest)**
- [ ] All colors display correctly
- [ ] Gradients render smoothly
- [ ] Fonts load properly
- [ ] SVG wave visible
- [ ] Hover effects work
- [ ] Print preview correct

#### **Firefox (Latest)**
- [ ] All colors display correctly
- [ ] Gradients render smoothly
- [ ] Fonts load properly
- [ ] SVG wave visible
- [ ] Hover effects work
- [ ] Print preview correct

#### **Safari (Latest)**
- [ ] All colors display correctly
- [ ] Gradients render smoothly
- [ ] Fonts load properly
- [ ] SVG wave visible
- [ ] Hover effects work
- [ ] Print preview correct

#### **Edge (Latest)**
- [ ] All colors display correctly
- [ ] Gradients render smoothly
- [ ] Fonts load properly
- [ ] SVG wave visible
- [ ] Hover effects work
- [ ] Print preview correct

**Pass Criteria:** Works identically in all modern browsers

---

### **Test 8: Visual Effects**

| Effect | Expected Behavior | Status |
|--------|------------------|--------|
| Container shadow | 0 8px 24px rgba(0,0,0,0.12) | [ ] |
| Table row hover | Background changes to #F9F9F9 | [ ] |
| Hover transition | Smooth 0.2s ease | [ ] |
| SVG wave | Displays at top of footer | [ ] |
| Gradients | Smooth 135deg angle | [ ] |
| Border radius | Rounded corners visible | [ ] |

**Pass Criteria:** All visual effects work as expected

---

### **Test 9: Edge Cases**

#### **Missing Data**
- [ ] Empty overtime hours shows "-"
- [ ] Missing department shows "N/A"
- [ ] Zero values display as "0.00"
- [ ] Null values handled gracefully

#### **Long Text**
- [ ] Long company name wraps correctly
- [ ] Long address doesn't overflow
- [ ] Long employee name fits
- [ ] Long designation fits

#### **Large Numbers**
- [ ] Large salary amounts display correctly
- [ ] Decimal places preserved (2 digits)
- [ ] Right alignment maintained
- [ ] No number overflow

**Pass Criteria:** All edge cases handled properly

---

### **Test 10: Performance**

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Page load time | < 2 seconds | | [ ] |
| Font load time | < 1 second | | [ ] |
| Render time | < 500ms | | [ ] |
| Print dialog | < 1 second | | [ ] |
| PDF generation | < 3 seconds | | [ ] |

**Pass Criteria:** All performance metrics met

---

## 🐛 Common Issues & Solutions

### **Issue 1: Fonts Not Loading**
**Symptom:** Arial font displays instead of Poppins/Open Sans  
**Cause:** Google Fonts CDN blocked or slow  
**Solution:** 
- Check internet connection
- Verify Google Fonts CDN is accessible
- Clear browser cache

### **Issue 2: Colors Look Different**
**Symptom:** Colors don't match specification  
**Cause:** Monitor calibration or browser color profile  
**Solution:**
- Use color picker to verify hex codes
- Test on different monitor
- Check browser color settings

### **Issue 3: Layout Breaks on Mobile**
**Symptom:** Horizontal scroll or overflow  
**Cause:** Responsive CSS not applied  
**Solution:**
- Clear browser cache
- Check viewport meta tag
- Verify media queries active

### **Issue 4: Print Background Missing**
**Symptom:** White background in print preview  
**Cause:** Browser setting disabled  
**Solution:**
- Enable "Background graphics" in print dialog
- Use "Print backgrounds" option
- Try different browser

### **Issue 5: SVG Wave Not Visible**
**Symptom:** No wave pattern in footer  
**Cause:** SVG encoding issue or browser compatibility  
**Solution:**
- Check browser console for errors
- Verify SVG data URI is correct
- Test in different browser

### **Issue 6: Gradients Not Smooth**
**Symptom:** Banding or harsh color transitions  
**Cause:** Monitor color depth or browser rendering  
**Solution:**
- Check monitor settings (24-bit color)
- Update graphics drivers
- Try different browser

---

## ✅ Final Acceptance Checklist

### **Visual Design**
- [ ] All colors match specification exactly
- [ ] Typography is correct (fonts, sizes, weights)
- [ ] Layout matches visual guide
- [ ] Spacing and padding correct
- [ ] Border radius applied properly
- [ ] Gradients render smoothly
- [ ] SVG wave displays correctly

### **Functionality**
- [ ] All employee data displays
- [ ] Earnings calculate correctly
- [ ] Deductions calculate correctly
- [ ] Net pay is accurate
- [ ] Empty values handled properly
- [ ] Long text doesn't break layout

### **Responsive**
- [ ] Desktop layout perfect
- [ ] Tablet layout adapts
- [ ] Mobile layout compact
- [ ] No horizontal scroll
- [ ] All content accessible

### **Print/Export**
- [ ] Print preview correct
- [ ] PDF export works
- [ ] Colors preserved
- [ ] Fonts embedded
- [ ] Single page layout

### **Browser Support**
- [ ] Chrome works perfectly
- [ ] Firefox works perfectly
- [ ] Safari works perfectly
- [ ] Edge works perfectly

### **Performance**
- [ ] Page loads quickly
- [ ] Fonts load fast
- [ ] No lag or delays
- [ ] Print dialog responsive

---

## 📊 Test Results Summary

### **Test Execution**
- **Date:** _______________
- **Tester:** _______________
- **Environment:** _______________

### **Results**
- **Total Tests:** 10
- **Passed:** ___ / 10
- **Failed:** ___ / 10
- **Blocked:** ___ / 10

### **Critical Issues Found**
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

### **Minor Issues Found**
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

### **Overall Status**
- [ ] ✅ **PASS** - Ready for production
- [ ] ⚠️ **CONDITIONAL PASS** - Minor issues, can deploy
- [ ] ❌ **FAIL** - Critical issues, cannot deploy

### **Sign-Off**
- **Tester:** _______________  **Date:** _______________
- **Reviewer:** _______________  **Date:** _______________
- **Approver:** _______________  **Date:** _______________

---

## 🚀 Quick Verification Commands

### **Visual Inspection**
```bash
# 1. Start app
python main.py

# 2. Open browser
http://localhost:5000

# 3. Navigate to payslip
Payroll → Payroll List → View Payslip

# 4. Check colors with browser DevTools
Right-click → Inspect → Computed styles
```

### **Print Test**
```bash
# 1. Open payslip
# 2. Press Ctrl+P (Windows) or Cmd+P (Mac)
# 3. Enable "Background graphics"
# 4. Preview → Should show all colors
# 5. Save as PDF → Test PDF opens correctly
```

### **Responsive Test**
```bash
# 1. Open payslip
# 2. Press F12 (DevTools)
# 3. Click device toolbar icon
# 4. Test these sizes:
#    - Desktop: 1920x1080
#    - Laptop: 1366x768
#    - Tablet: 768x1024
#    - Mobile: 375x667
```

---

## 📝 Test Notes Template

```
Test Date: _______________
Browser: _______________
OS: _______________
Screen Resolution: _______________

Visual Appearance:
- Company Header: _______________
- Title Section: _______________
- Content Area: _______________
- Pay Table: _______________
- Summary: _______________
- Footer: _______________

Data Accuracy:
- Employee Info: _______________
- Earnings: _______________
- Deductions: _______________
- Totals: _______________

Responsive:
- Desktop: _______________
- Tablet: _______________
- Mobile: _______________

Print:
- Preview: _______________
- PDF: _______________

Issues Found:
1. _______________
2. _______________
3. _______________

Overall Rating: ___ / 10
```

---

**✅ Testing Complete! Ready for Production Deployment**