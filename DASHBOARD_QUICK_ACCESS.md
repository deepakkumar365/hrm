# 🚀 Quick Access Guide - HR Manager Dashboard

## ⚡ TL;DR - Quick Start (30 seconds)

```
1. Open browser
2. Go to: http://localhost:5000/dashboard/hr-manager
3. Log in as HR Manager
4. Select company
5. Click any metric card
6. View details
```

---

## 📍 Access URLs

### Main Dashboard
```
http://localhost:5000/dashboard/hr-manager
```
**Shows:** 5 metric cards, today's summary, quick actions

### Detail Views (Click cards to access)
```
Attendance:  /dashboard/hr-manager/detail/attendance
Leaves:      /dashboard/hr-manager/detail/leaves
Payroll:     /dashboard/hr-manager/detail/payroll
OT:          /dashboard/hr-manager/detail/ot
Employees:   /dashboard/hr-manager/detail/employees
```

---

## 👤 Who Can Access?

**Required Roles:**
- ✅ HR Manager
- ✅ Tenant Admin
- ✅ Super Admin

**NOT Allowed:**
- ❌ Regular Employee
- ❌ Finance (unless HR Manager role too)
- ❌ Unauthenticated users

**How to Access:**
1. Log in with your credentials
2. System automatically checks your role
3. If you're HR Manager or above → Access granted
4. If not → Redirected to home page with "Access Denied" message

---

## 🔧 Running the Application

### Development Environment

**Option 1: Using Python directly**
```bash
# Navigate to project directory
cd D:/DEV/HRM/hrm

# Install dependencies (if needed)
pip install -r requirements.txt

# Run the application
python main.py
```

**Option 2: Using Flask CLI**
```bash
# Set environment
set FLASK_APP=main.py
set FLASK_ENV=development

# Run
flask run
```

**Option 3: Using build script**
```bash
# On Windows
build.sh
```

**When it's running, you'll see:**
```
 * Serving Flask app 'main'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Production Environment (Render/Replit)

**Automatically deployed** when you push to your repository.
- Build command: `./build.sh`
- Start command: `gunicorn -c gunicorn.conf.py main:app`
- Access: `https://your-app.onrender.com/dashboard/hr-manager`

---

## 🌐 Browser Access

### Local Development
```
http://localhost:5000/dashboard/hr-manager
http://127.0.0.1:5000/dashboard/hr-manager
```

### Production (Render)
```
https://your-app-name.onrender.com/dashboard/hr-manager
```

### Production (Replit)
```
https://your-replit-username--your-project-name.replit.dev/dashboard/hr-manager
```

---

## 📋 Step-by-Step Access Instructions

### Step 1: Start the Application
```bash
cd D:/DEV/HRM/hrm
python main.py
```
Wait for: `Running on http://127.0.0.1:5000`

### Step 2: Open Browser
- **Chrome:** Open new tab → Type URL
- **Edge:** Open new tab → Type URL
- **Firefox:** Open new tab → Type URL

### Step 3: Navigate to Dashboard
```
http://localhost:5000
```

### Step 4: Log In
- Username: `admin@noltriton.com` (or your HR Manager username)
- Password: Your password
- Click "Login"

### Step 5: Go to Dashboard
- Click "HR Manager Dashboard" from menu
- OR directly type: `http://localhost:5000/dashboard/hr-manager`
- OR from home page, look for "Dashboard" section

### Step 6: Select Company (if multiple)
- Dropdown appears at top-right
- Choose your company
- Dashboard automatically updates

### Step 7: View Metrics
- 5 colored cards displayed
- Each card shows a key metric
- All data auto-loads

### Step 8: Click Any Card
- Click "Attendance" → See attendance details
- Click "Leaves" → See leave details
- Click "Payroll" → See payroll details
- Click "OT" → See OT details
- Click "Employees" → See employee directory

---

## 🎯 What Each Card Shows

### 1. Today's Attendance Card (Green)
**Main Display:**
- Number of employees with today's attendance recorded
- Example: "42 employees recorded"

**Sub-numbers:**
- ✅ Present: Green colored
- ❌ Absent: Red colored
- ⏰ Late: Orange colored
- 📅 Date: Today's date

**Click → Goes to:** Attendance Details page with filters

---

### 2. On Leave Today Card (Purple)
**Main Display:**
- Number of employees currently on approved leave
- Example: "8 employees on approved leave"

**Sub-numbers:**
- Month-to-date total leaves
- Pending approval count
- Approved count
- Rejected count

**Click → Goes to:** Leave Details page with filters

---

### 3. Payroll Card (Blue)
**Main Display:**
- Number of employees in current month's payroll
- Example: "45 employees in payroll"

**Sub-numbers:**
- MTD (Month-to-Date) days worked
- YTD OT hours
- Monthly attendance %
- Leave days taken

**Click → Goes to:** Payroll Details page with filters

---

### 4. OT Management Card (Cyan)
**Main Display:**
- Total overtime hours this month
- Example: "120 OT hours this month"

**Sub-numbers:**
- OT records count
- Pending approvals
- YTD OT hours
- YTD OT records

**Click → Goes to:** OT Details page with filters

---

### 5. Employee Base Card (Orange)
**Main Display:**
- Total number of employees in company
- Example: "256 total employees"

**Sub-numbers:**
- Active employees count
- Number of companies
- Average attendance %
- YTD OT records

**Click → Goes to:** Employee Directory with search & filters

---

## 🔍 Using Detail Views

### After Clicking Any Card

**You'll See:**
1. **Header** with title and back button
2. **Summary Cards** showing key stats
3. **Filter Section** to narrow down data
4. **Data Table** with all records

### Example: Attendance Details

**Summary Cards Show:**
- Total Present
- Total Absent
- Total Late
- Total Recorded

**Filters Available:**
- Date picker (choose which date)
- Status dropdown (Present/Absent/Late/All)
- Department dropdown (filter by department)
- Sort options (by name, time, department)

**Table Shows:**
- Employee Name
- Employee ID
- Department
- Time In
- Status (colored badge)
- Notes
- More...

**Back Button:**
- Returns to main dashboard
- Keeps your company selection

---

## 💡 Common Tasks

### I want to see today's attendance
1. Open Dashboard
2. Look at "Today's Attendance" card
3. Click it
4. Date is pre-selected to today
5. Click "Apply Filters"
6. View all attendance records

### I want to check pending leave requests
1. Open Dashboard
2. Click "On Leave Today" card
3. Use Status filter → Select "Pending"
4. Click "Apply Filters"
5. See all pending leave requests

### I want to review payroll for a specific month
1. Open Dashboard
2. Click "Payroll" card
3. Use Month/Year dropdowns
4. Select desired month and year
5. Click "Apply Filters"
6. View payroll for that period

### I want to approve OT requests
1. Open Dashboard
2. Click "Overtime Management" card
3. Filter by Status → "Pending"
4. Click "Apply Filters"
5. See pending OT requests
6. Click on each to approve/reject

### I want to export employee data
1. Open Dashboard
2. Click "Employee Base" card
3. Use filters to select employees
4. Look for "Export" button (if available)
5. Download as Excel/PDF

---

## ⚙️ Troubleshooting

### Dashboard Not Loading
**Problem:** Blank page or error message

**Solution:**
1. Check if app is running: `python main.py`
2. Check URL is correct: `localhost:5000`
3. Clear browser cache: Ctrl+Shift+Delete
4. Try in incognito/private mode
5. Check console for errors: F12 → Console tab

### "Access Denied" Message
**Problem:** See "Access Denied" message

**Solution:**
1. Verify you're logged in
2. Check your role: Should be "HR Manager" or higher
3. Contact administrator to assign correct role
4. Logout and login again

### No Companies in Dropdown
**Problem:** Company selector shows empty

**Solution:**
1. You need to be assigned to a company
2. Contact Super Admin or Tenant Admin
3. Ask them to assign you to a company
4. Logout and login again

### Metric Values Showing Zero
**Problem:** All metric cards show 0

**Solution:**
1. Check if there's data in the database
2. Selected company might have no employees
3. Try switching companies
4. Run database seeding if needed: `python seed.py`

### Table Shows No Records
**Problem:** Detail view table is empty

**Solution:**
1. Try removing filters
2. Change date range if date is selected
3. Make sure company is selected
4. Check if data exists for that period

### Slow Loading
**Problem:** Dashboard takes long to load

**Solution:**
1. Check internet connection
2. Clear browser cache
3. Try reloading: Ctrl+R
4. Check server is running: Check terminal
5. Try hard refresh: Ctrl+Shift+R

---

## 📊 Dashboard Features Summary

| Feature | What It Does |
|---------|-------------|
| **Metric Cards** | Show key HR metrics at a glance |
| **Click Cards** | Open detailed view for that metric |
| **Filters** | Narrow down data (date, status, dept) |
| **Sorting** | Sort data by different columns |
| **Summary Cards** | Show quick statistics |
| **Color Badges** | Status at a glance (green=good, red=bad) |
| **Back Button** | Return to dashboard |
| **Company Selector** | Switch between companies |
| **Quick Actions** | Direct links to common tasks |
| **Today's Summary** | 5 key metrics from today |

---

## 🔑 Key Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+R | Reload page |
| Ctrl+F | Search on page |
| F12 | Open developer tools |
| Esc | Close any popup |
| Tab | Move between fields |
| Enter | Apply filter |

---

## 📱 Mobile Access

**Dashboard is fully responsive!**

### On Mobile Phone
1. Open browser
2. Type: `your-app-url/dashboard/hr-manager`
3. All features work on mobile
4. Single card per row (easier to read)
5. Touch-friendly buttons

### On Tablet
1. Same URL as desktop
2. 2-3 cards per row
3. Larger touch targets
4. Scrollable tables

### Tips for Mobile
- Use portrait mode for best view
- Use landscape for tables
- Filters accessible via scroll
- Back button easy to reach

---

## 🔐 Account Requirements

**You Need:**
1. ✅ Active user account in system
2. ✅ HR Manager role (or higher)
3. ✅ Company assigned
4. ✅ Valid password
5. ✅ Access not revoked

**To Get Access:**
1. Ask your administrator
2. Provide your email
3. They create user with HR Manager role
4. They assign your company
5. You'll receive login credentials

**Default Credentials (if provided):**
- Email: admin@noltriton.com
- Password: Check setup documentation

---

## 📖 Additional Resources

### Documentation Files
- `DASHBOARD_PREVIEW.md` - Visual layout guide
- `ENHANCED_DASHBOARD_GUIDE.md` - Complete feature guide
- `DASHBOARD_QUICK_START.md` - User guide
- `DASHBOARD_IMPLEMENTATION_SUMMARY.md` - Technical details
- `DASHBOARD_DELIVERY.md` - Delivery report
- `DASHBOARD_VISUAL_GUIDE.md` - ASCII layout diagrams

### Getting Help
1. Check documentation
2. Review this guide
3. Contact administrator
4. Check error messages carefully

---

## ✨ Pro Tips

**Tip 1: Keyboard Navigation**
- Tab to move between fields
- Arrow keys to select options
- Enter to apply filters

**Tip 2: Batch Operations**
- Open detail view
- Select multiple employees
- Apply action to all selected

**Tip 3: Export Data**
- Some views have export buttons
- Export to Excel for analysis
- Share reports with management

**Tip 4: Filter Combinations**
- Use multiple filters together
- Example: Status=Pending + Department=HR
- Narrows down results effectively

**Tip 5: Bookmark Dashboard**
- Ctrl+D to bookmark
- Quick access next time
- Remember to log in first

---

## 🎯 Next Steps

**You're ready to use the dashboard!**

1. ✅ Open the application
2. ✅ Log in with your credentials
3. ✅ Navigate to `/dashboard/hr-manager`
4. ✅ Select your company
5. ✅ Click any metric card
6. ✅ Use filters to view specific data
7. ✅ Make informed HR decisions

**Start using the dashboard now! 🚀**

---

## 📞 Need Help?

- **For Access Issues:** Contact your System Administrator
- **For Feature Questions:** Check the documentation files
- **For Technical Issues:** Check troubleshooting section above
- **For Enhancement Requests:** Contact development team

---

**Enjoy using your new HR Manager Dashboard! 📊**

Questions? Check the documentation or contact support! 📞