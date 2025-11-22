# 🎨 HR Manager Dashboard - Visual Preview

## How to Access the Dashboard

**URL:** `http://localhost:5000/dashboard/hr-manager` (or your deployed URL)

**Requirements:**
- ✅ Logged in as HR Manager, Tenant Admin, or Super Admin
- ✅ At least one company assigned to your account

---

## 📊 Dashboard Layout Structure

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  📈 HR Manager Dashboard          [Select Company ▼ NolTrion Ltd]  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌─────────────────────────────────────────────────────────────────────┐
│                    METRIC CARDS (5 Cards - Clickable)               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │🟢 ATTENDANCE │  │🟣 LEAVES     │  │🔵 PAYROLL    │              │
│  │──────────────│  │──────────────│  │──────────────│              │
│  │   42 emp     │  │   8 on leave │  │  45 emp in   │              │
│  │   recorded   │  │   on leave   │  │   payroll    │              │
│  │              │  │              │  │              │              │
│  │ ✓42  ✗5  ⏰3 │  │ ✓5   ⏳2  ✗1  │  │ MTD: 45 Days │              │
│  │              │  │              │  │ YTD OT: 120h │              │
│  │ View → │  │ View → │  │ View → │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐                                │
│  │🔷 OT MANAGE  │  │👥 EMPLOYEES  │                                │
│  │──────────────│  │──────────────│                                │
│  │  120 OT hrs  │  │  256 emp     │                                │
│  │  this month  │  │  total       │                                │
│  │              │  │              │                                │
│  │ OT: 25   ⏳8 │  │ Active: 245  │                                │
│  │ ✓15   ✗2     │  │ Avg Att:92%  │                                │
│  │ YTD: 320h    │  │ YTD OT: 15   │                                │
│  │ View → │  │ View → │                                │
│  └──────────────┘  └──────────────┘                                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  📅 TODAY'S SUMMARY - Monday, January 15, 2024                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │ PRESENT │  │ ABSENT  │  │  LATE   │  │ ON LEAVE│  │OT HOURS │ │
│  │   42    │  │    5    │  │    3    │  │    2    │  │  8.5    │ │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  ⚡ QUICK ACTIONS                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │ ✓ Mark          │  │ 💰 Generate     │  │ 👥 Manage       │    │
│  │   Attendance    │  │    Payroll      │  │    Employees    │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│                                                                      │
│  ┌─────────────────┐                                               │
│  │ 🔔 Payroll      │                                               │
│  │    Reminder     │                                               │
│  └─────────────────┘                                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Metric Cards Details

### 1️⃣ **TODAY'S ATTENDANCE CARD** (Green Gradient)
**Color:** Green (#10b981 to #059669)

Displays:
- **Main Number:** 42 (total employees recorded today)
- **Sub-text:** "employees recorded"
- **4 Stats:**
  - ✅ **Present:** 42 (green color)
  - ❌ **Absent:** 5 (red color)
  - ⏰ **Late:** 3 (amber color)
  - 📅 **Date:** Today's date shortened
- **Action:** Click to see detailed attendance list with filters

---

### 2️⃣ **ON LEAVE TODAY CARD** (Purple Gradient)
**Color:** Purple (#8b5cf6 to #6d28d9)

Displays:
- **Main Number:** 8 (employees on approved leave)
- **Sub-text:** "employees on approved leave"
- **4 Stats:**
  - 📊 **MTD Leaves:** 8 total this month
  - ⏳ **Pending Approval:** 2 awaiting decision
  - ✅ **Approved:** 5 approved leaves
  - ❌ **Rejected:** 1 rejected request
- **Action:** Click to see leave details with filters

---

### 3️⃣ **PAYROLL CARD** (Blue Gradient)
**Color:** Blue (#3b82f6 to #1d4ed8)

Displays:
- **Main Number:** 45 (employees in payroll)
- **Sub-text:** "employees in payroll" (e.g., "January 2024 Payroll")
- **4 Stats:**
  - 📅 **MTD Days:** 22 days worked this month
  - 📈 **YTD OT Hours:** 120+ hours overtime YTD
  - 📊 **Attendance:** 98% this month
  - 🏖️ **Leave Days:** 5 days taken this month
- **Action:** Click to see payroll breakdown and salary details

---

### 4️⃣ **OVERTIME MANAGEMENT CARD** (Cyan Gradient)
**Color:** Cyan (#06b6d4 to #0891b2)

Displays:
- **Main Number:** 120 (total OT hours this month)
- **Sub-text:** "OT hours this month"
- **4 Stats:**
  - 📝 **OT Records:** 25 OT entries
  - ⏳ **Pending Approval:** 8 awaiting manager approval
  - ✅ **YTD Hours:** 320 hours YTD
  - 📊 **YTD Records:** 95 OT records YTD
- **Action:** Click to manage OT requests with approval status

---

### 5️⃣ **EMPLOYEE BASE CARD** (Orange Gradient)
**Color:** Orange (#f59e0b to #d97706)

Displays:
- **Main Number:** 256 (total employees)
- **Sub-text:** "total employees"
- **4 Stats:**
  - ✅ **Active:** 245 active employees
  - 🏢 **Companies:** 3 companies managed
  - 📊 **Avg Attendance:** 92% average attendance
  - ⏳ **YTD OT:** 15 OT records this year
- **Action:** Click to browse employee directory

---

## 🎨 Color Scheme Used

| Component | Color | Usage |
|-----------|-------|-------|
| **Success** | #10b981 (Green) | Present, Approved, Active |
| **Danger** | #ef4444 (Red) | Absent, Rejected, Inactive |
| **Warning** | #f59e0b (Amber) | Late, Pending, Awaiting |
| **Info** | #06b6d4 (Cyan) | OT, Additional Info |
| **Primary** | #4f46e5 (Indigo) | Main UI Elements |
| **Attendance** | Green (#10b981) | Attendance Card |
| **Leave** | Purple (#8b5cf6) | Leave Card |
| **Payroll** | Blue (#3b82f6) | Payroll Card |
| **OT** | Cyan (#06b6d4) | OT Card |
| **Employee** | Orange (#f59e0b) | Employee Card |

---

## 📱 Responsive Behavior

### Desktop (1400px+)
- ✅ All 5 cards displayed in 2 rows
- ✅ Full width for text and details
- ✅ Large metric values (36px)
- ✅ 4 stat boxes per card in 2x2 grid

### Tablet (768-1399px)
- ✅ Cards wrap to fit screen
- ✅ Usually 2-3 cards per row
- ✅ Medium metric values
- ✅ Responsive stat boxes

### Mobile (<768px)
- ✅ Single card per row
- ✅ Full width cards
- ✅ Summary grid shows 2 columns
- ✅ Company selector takes full width
- ✅ Action buttons stack vertically

---

## 🔗 What Happens When You Click?

### Click Attendance Card
→ Goes to: `/dashboard/hr-manager/detail/attendance?company_id=<id>`
- Shows all employees with today's attendance status
- Filters: By date, status (Present/Absent/Late), department
- Sorting: By name, time in, department
- Shows: Employee ID, Name, Department, Time In, Status, Notes

### Click Leave Card
→ Goes to: `/dashboard/hr-manager/detail/leaves?company_id=<id>`
- Shows current/ongoing leave requests
- Filters: By status (Approved/Pending/Rejected), department, leave type
- Sorting: By name, start date, department
- Shows: Employee, Department, Leave Type, Start/End dates, Days, Reason

### Click Payroll Card
→ Goes to: `/dashboard/hr-manager/detail/payroll?company_id=<id>`
- Shows monthly payroll details
- Filters: By month, year, department
- Sorting: By name, salary amount
- Shows: Name, ID, Department, Basic, Allowances, Deductions, Net Pay

### Click OT Card
→ Goes to: `/dashboard/hr-manager/detail/ot?company_id=<id>`
- Shows OT requests and approvals
- Filters: By status (Pending/Approved/Rejected), department
- Sorting: By name, date, hours
- Shows: Employee, Department, OT Date, Hours, Status, Reason

### Click Employee Card
→ Goes to: `/dashboard/hr-manager/detail/employees?company_id=<id>`
- Shows employee directory
- Filters: By status (Active/Inactive), department, search by name/ID
- Sorting: By name, join date, department
- Shows: ID, Name, Email, Department, Designation, Join Date, Status

---

## 👆 Interactive Elements

### Header
- **Title:** "HR Manager Dashboard" with chart icon
- **Company Selector:** Dropdown to switch between companies
  - Only shows companies accessible to current user
  - Auto-refreshes dashboard on selection change

### Metric Cards
- **Hover Effect:** Cards lift up (translateY -6px) with enhanced shadow
- **Cursor:** Changes to pointer on hover
- **Transition:** Smooth 0.3s animation
- **Click:** Navigates to detailed view

### Today's Summary
- **Color-Coded Items:** Each item has colored left border
- **Large Numbers:** Easy to read at a glance
- **5 Key Metrics:** Present, Absent, Late, On Leave, OT Hours

### Quick Actions
- **4 Gradient Buttons:** Different colors for each action
- **Hover:** Buttons lift up with shadow effect
- **Icons:** Font Awesome icons for visual clarity
- **Links:** Direct to frequently used features

---

## 📊 Data Displayed on Dashboard

### Today's Attendance Summary
```
Date: Monday, January 15, 2024
Total Recorded: 42 employees
├─ Present: 42
├─ Absent: 5
└─ Late: 3
```

### Leave Statistics (This Month)
```
Total Leaves: 8
├─ Approved: 5
├─ Pending: 2
└─ Rejected: 1
```

### Payroll Information
```
Month: January 2024
├─ Employees in Payroll: 45
├─ MTD Days: 22
├─ MTD Attendance: 98%
└─ Leave Days: 5
```

### OT Management
```
This Month:
├─ Total OT Hours: 120
├─ OT Records: 25
├─ Pending Approvals: 8
└─ Approved: 15
Year-to-Date:
├─ Total OT Hours: 320
└─ OT Records: 95
```

### Employee Base
```
Total Employees: 256
├─ Active: 245
├─ Inactive: 11
├─ Average Attendance: 92%
└─ YTD OT Records: 15
```

---

## 🔐 Access Control

**Who Can See This Dashboard?**
- ✅ HR Manager
- ✅ Tenant Admin
- ✅ Super Admin

**Who CANNOT See This?**
- ❌ Regular Employee
- ❌ Finance Team (unless they are HR Manager)
- ❌ Unauthorized users

**Company Isolation:**
- HR Managers can only see their assigned company's data
- Tenant Admins can see all companies in their tenant
- Super Admins can see all companies in the system

---

## ⚙️ Technical Features

✅ **Real-Time Data:** Dashboard loads fresh data every time (not cached)
✅ **Company Switching:** Instantly shows data for selected company
✅ **Responsive Design:** Works on all devices (mobile, tablet, desktop)
✅ **Modern Styling:** Gradients, shadows, smooth animations
✅ **Fast Loading:** Optimized database queries
✅ **Error Handling:** Graceful handling of missing data
✅ **Permission Checking:** Validates user access before showing data

---

## 🚀 How to Start Using

1. **Open your browser** and navigate to:
   ```
   http://your-app-url/dashboard/hr-manager
   ```

2. **Log in** with HR Manager or Tenant Admin credentials

3. **Select company** from the dropdown (if you manage multiple)

4. **View metrics** - All data loads automatically

5. **Click any card** to see detailed information:
   - Use filters to narrow down data
   - Sort by different columns
   - Apply custom date ranges

6. **Use Quick Actions** for common tasks:
   - Mark Attendance
   - Generate Payroll
   - Manage Employees
   - Payroll Reminder

---

## 📈 Example Workflow

### Morning Routine
1. Log in → Dashboard loads with today's data
2. Check "Today's Summary" → See who's present/absent/late
3. Click "Attendance" card → View attendance details
4. Click "On Leave" card → See who's on leave today
5. Use "Mark Attendance" quick action for any missing entries

### End of Month
1. Dashboard shows "January 2024 Payroll"
2. Click "Payroll" card → Review salary details
3. Click "Manage Employees" → Verify employee data
4. Use "Generate Payroll" action → Run payroll process

### For Overtime Management
1. Dashboard shows "120 OT hours this month"
2. Click "OT Management" card → Review pending OT requests
3. Filter by "Pending" status → See requests awaiting approval
4. Approve/Reject OT requests
5. Track YTD OT hours for compliance

---

## 💡 Tips & Tricks

**Quick Company Switch:**
- Use the company selector dropdown at top-right
- Dashboard automatically refreshes with new company's data

**Filter by Department:**
- Click on any detail card
- Use department filter to focus on specific departments

**Track Trends:**
- Compare "MTD" vs "YTD" numbers
- Monitor overtime trends
- Watch attendance patterns

**Monthly Review:**
- Dashboard automatically shows current month data
- MTD sections update daily
- YTD sections cumulative from January 1st

**Mobile Access:**
- Dashboard is fully responsive
- Works great on phones and tablets
- Single card per row on mobile

---

## 🎓 For More Information

📖 **Complete Guide:** See `ENHANCED_DASHBOARD_GUIDE.md`
🚀 **Quick Start:** See `DASHBOARD_QUICK_START.md`
💻 **Technical Details:** See `DASHBOARD_IMPLEMENTATION_SUMMARY.md`
🎨 **Visual Layout:** See `DASHBOARD_VISUAL_GUIDE.md`

---

**Your HR Manager Dashboard is now ready to use! 🎉**

Start exploring the data and making informed HR decisions today! 📊