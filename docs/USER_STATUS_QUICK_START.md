# Quick Start: User Status Toggle

## ⚡ 30-Second Setup

✅ **Location:** `Masters → User Status Toggle`  
✅ **Roles:** HR Manager, Tenant Admin, Super Admin  
✅ **URL:** `/masters/user-status-toggle`

---

## 🎯 Activate User AKSL093

1. Click **Masters** in menu
2. Click **User Status Toggle**
3. Search for **AKSL093** (or scroll to find)
4. Click **Activate** button (if status is Inactive)
5. Confirm in popup
6. ✅ Done! User is now active

---

## 📊 What You'll See

```
┌─────────────────────────────────────┐
│  Total: 53 | Active: 45 | Inactive: 8 │
└─────────────────────────────────────┘

[Search box]

┌─ Users Table ────────────────────────┐
│ Name  │ Email │ Role │ Status │ Action│
├───────┼───────┼──────┼────────┼───────┤
│ AKSL  │ aksl@ │ User │  ◉ Act │ Deact │
│ EMP2  │ emp2@ │ Mgr  │  ◯ Inact│ Act   │
└───────┴───────┴──────┴────────┴───────┘
```

---

## 🔄 Status Options

| Status | Badge | Action Button | Meaning |
|--------|-------|---------------|---------|
| Active | 🟢 | Deactivate | User can login |
| Inactive | 🔴 | Activate | User cannot login |

---

## 🚫 Limitations

- ❌ Cannot deactivate yourself
- ❌ Tenant Admin can only see own tenant users
- ✅ Super Admin can see all users

---

## 📋 Statistics Explained

- **Total Users:** All users in your organization
- **Active Users:** Can login and use system (green)
- **Inactive Users:** Cannot login (red)

---

## 🔐 Features

✅ Search by name, email, username
✅ Real-time status updates
✅ Responsive (works on mobile)
✅ Audit trail logging
✅ One-click toggle
✅ Tenant isolation

---

## 💬 Need Help?

**Problem:** Menu not visible  
**Fix:** Check if you're logged in as HR Manager, Tenant Admin, or Super Admin

**Problem:** Toggle not working  
**Fix:** Refresh page, check browser console (F12)

**Problem:** Only seeing some users  
**Fix:** You may only see users from your tenant

---

**That's it! You're ready to manage user status.** 🎉