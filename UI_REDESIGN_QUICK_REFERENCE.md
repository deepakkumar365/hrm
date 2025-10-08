# UI Redesign Quick Reference Guide

## Files Modified

### HTML Templates
1. `templates/dashboard.html` - Enhanced dashboard with quick stats
2. `templates/team/team_list.html` - Redesigned team member cards
3. `templates/attendance/list.html` - Single-view attendance with filters
4. `templates/leave/form.html` - Clean single-page leave request form

### CSS Styles
1. `static/css/styles.css` - Added 800+ lines of new styles

---

## New CSS Classes Reference

### Dashboard Components

```css
/* Enhanced Stat Cards */
.stat-card-enhanced          /* Improved stat card container */
.stat-card-header            /* Card header with icon and badge */
.stat-card-content           /* Card content area */
.stat-card-badge             /* Small badge labels */

/* Quick Stats */
.quick-stats-container       /* Grid container for quick stats */
.quick-stat-item             /* Individual stat item */
.quick-stat-icon             /* Icon container */
.quick-stat-content          /* Text content area */
.quick-stat-label            /* Label text */
.quick-stat-value            /* Value text */
.quick-stat-action           /* Action button */
```

### Team Page Components

```css
/* Team Layout */
.team-stats-mini             /* Header stats badge */
.team-stat-badge             /* Individual stat badge */
.team-grid                   /* Team members grid */

/* Team Cards */
.team-member-card            /* Card container */
.team-card-header            /* Gradient header with avatar */
.team-card-body              /* Card content */
.team-card-footer            /* Card footer with actions */

/* Avatar */
.team-member-avatar          /* Avatar container */
.avatar-image                /* Profile image */
.avatar-placeholder          /* Initials placeholder */
.avatar-status-indicator     /* Online status dot */

/* Content */
.team-member-name            /* Member name */
.team-member-role            /* Role/position */
.team-member-info            /* Additional info */
.team-contact-actions        /* Contact buttons group */
.team-contact-btn            /* Individual contact button */
```

### Attendance Page Components

```css
/* Filter Section */
.attendance-filter-section   /* Filter container */
.attendance-filter-form      /* Form wrapper */
.filter-tabs                 /* Tab buttons container */
.filter-tab                  /* Individual tab button */
.filter-tab.active           /* Active tab state */
.filter-inputs               /* Input fields container */
.filter-input-group          /* Individual input group */
.filter-actions              /* Action buttons */

/* Attendance Records */
.attendance-records-container /* Records list container */
.attendance-record-card      /* Individual record card */
.attendance-card-header      /* Card header */
.attendance-card-body        /* Card content */

/* Date & Status */
.attendance-date-info        /* Date information */
.employee-name               /* Employee name */
.employee-id                 /* Employee ID */
.record-date                 /* Date display */
.attendance-status-badge     /* Status badge container */

/* Status Badges */
.status-badge                /* Base status badge */
.status-badge.status-present /* Present status (green) */
.status-badge.status-absent  /* Absent status (red) */
.status-badge.status-late    /* Late status (yellow) */
.overtime-badge              /* Overtime indicator */

/* Time Grid */
.attendance-time-grid        /* Time items grid */
.time-item                   /* Individual time item */
.time-item.clock-in          /* Clock in (green) */
.time-item.clock-out         /* Clock out (red) */
.time-item.break-time        /* Break time (yellow) */
.time-item.total-hours       /* Total hours (blue) */
.time-icon                   /* Time icon container */
.time-details                /* Time text container */
.time-label                  /* Time label */
.time-value                  /* Time value */
.time-value.highlight        /* Highlighted value */

/* Remarks */
.attendance-remarks          /* Remarks section */
```

### Leave Request Form Components

```css
/* Form Layout */
.leave-request-form          /* Form wrapper */
.leave-form-container        /* Two-column container */
.leave-form-main             /* Main form column */
.leave-form-sidebar          /* Sidebar column */

/* Form Sections */
.leave-form-section          /* Section card */
.section-heading             /* Section heading with icon */

/* Summary Sidebar */
.leave-summary-card          /* Summary card */
.summary-header              /* Summary header */
.summary-title               /* Summary title */

/* Balance Display */
.summary-balance-card        /* Balance card */
.balance-icon                /* Balance icon */
.balance-info                /* Balance text */
.balance-value               /* Balance number */
.balance-label               /* Balance label */

/* Summary Details */
.summary-details             /* Details container */
.summary-item                /* Individual detail item */
.summary-label               /* Detail label */
.summary-value               /* Detail value */

/* Info Box */
.summary-info-box            /* Info box container */
.info-icon                   /* Info icon */
.info-content                /* Info text */
.info-title                  /* Info title */
.info-text                   /* Info description */

/* Actions */
.summary-actions             /* Actions container */
.btn-block                   /* Full-width button */
```

### Common Components

```css
/* Empty States */
.empty-state-container       /* Empty state wrapper */
.empty-state-icon            /* Large icon */
.empty-state-title           /* Title text */
.empty-state-text            /* Description text */

/* Utility Classes */
.dashboard-wrapper           /* Page wrapper */
.dashboard-header            /* Page header */
.dashboard-title             /* Page title */
.dashboard-subtitle          /* Page subtitle */
.dashboard-grid              /* Grid layout */
```

---

## Color Scheme

### Status Colors
- **Present/Success**: Green (`#74C69D`, `#2D6A4F`)
- **Absent/Danger**: Red (`#EF4444`, `#991B1B`)
- **Late/Warning**: Yellow (`#F59E0B`, `#92400E`)
- **Info**: Blue (`#3B82F6`, `#1E40AF`)

### Background Colors
- **Primary**: `#2D6A4F` (Dark Green)
- **Light**: `#F8FAFC` (Light Grey)
- **White**: `#FFFFFF`
- **Grey**: `#E2E8F0` (Border Grey)

---

## Icon Usage

### Dashboard Icons
- `fa-calendar-check` - Attendance Rate
- `fa-leaf` - Leave Balance
- `fa-calendar-times` - Leaves Taken
- `fa-clock` - Working Hours
- `fa-file-invoice` - Payslip
- `fa-umbrella-beach` - Holiday
- `fa-tasks` - Pending Requests

### Team Icons
- `fa-users` - Team Count
- `fa-briefcase` - Role/Position
- `fa-building` - Department
- `fa-map-marker-alt` - Location
- `fa-envelope` - Email
- `fa-phone` - Phone
- `fa-user` - Profile

### Attendance Icons
- `fa-calendar-day` - Today
- `fa-calendar-week` - This Week
- `fa-calendar-alt` - This Month
- `fa-calendar` - Custom
- `fa-sign-in-alt` - Clock In
- `fa-sign-out-alt` - Clock Out
- `fa-coffee` - Break Time
- `fa-hourglass-half` - Total Hours
- `fa-check-circle` - Present
- `fa-times-circle` - Absent
- `fa-clock` - Late

### Leave Request Icons
- `fa-info-circle` - Leave Details
- `fa-calendar-alt` - Leave Period
- `fa-file-alt` - Reason
- `fa-phone-alt` - Contact
- `fa-leaf` - Leave Balance
- `fa-paper-plane` - Submit

---

## Responsive Breakpoints

```css
/* Desktop */
@media (min-width: 1024px) {
    /* Full layout */
}

/* Tablet */
@media (max-width: 1024px) {
    /* Adjusted layout */
    .leave-form-container { grid-template-columns: 1fr; }
}

/* Mobile */
@media (max-width: 768px) {
    /* Single column */
    .dashboard-grid .col-span-* { grid-column: span 12; }
    .team-grid { grid-template-columns: 1fr; }
    .attendance-time-grid { grid-template-columns: 1fr; }
}
```

---

## JavaScript Functions

### Attendance Page
```javascript
setDateFilter(type)  // Set filter: 'today', 'week', 'month', 'custom'
```

### Team Page
```javascript
showMemberDetails(memberId)  // Show member details (placeholder)
```

---

## Usage Examples

### Adding a Quick Stat
```html
<div class="quick-stat-item">
    <div class="quick-stat-icon">
        <i class="fas fa-icon-name"></i>
    </div>
    <div class="quick-stat-content">
        <span class="quick-stat-label">Label</span>
        <span class="quick-stat-value">Value</span>
    </div>
    <a href="#" class="quick-stat-action">
        <i class="fas fa-arrow-right"></i>
    </a>
</div>
```

### Adding a Team Member Card
```html
<div class="team-member-card">
    <div class="team-card-header">
        <div class="team-member-avatar">
            <div class="avatar-placeholder">JD</div>
            <div class="avatar-status-indicator"></div>
        </div>
    </div>
    <div class="team-card-body">
        <h3 class="team-member-name">John Doe</h3>
        <div class="team-member-role">
            <i class="fas fa-briefcase"></i>
            <span>Developer</span>
        </div>
    </div>
    <div class="team-card-footer">
        <div class="team-contact-actions">
            <a href="mailto:john@example.com" class="team-contact-btn">
                <i class="fas fa-envelope"></i>
            </a>
        </div>
    </div>
</div>
```

### Adding an Attendance Record
```html
<div class="attendance-record-card">
    <div class="attendance-card-header">
        <div class="attendance-date-info">
            <div class="record-date">
                <i class="fas fa-calendar"></i>
                <span>Monday, January 1, 2024</span>
            </div>
        </div>
        <div class="attendance-status-badge">
            <span class="status-badge status-present">
                <i class="fas fa-check-circle"></i>
                Present
            </span>
        </div>
    </div>
    <div class="attendance-card-body">
        <div class="attendance-time-grid">
            <!-- Time items here -->
        </div>
    </div>
</div>
```

---

## Tips & Best Practices

1. **Always use the dashboard-wrapper** for consistent page layout
2. **Use icon classes** from Font Awesome for consistency
3. **Follow the color scheme** for status indicators
4. **Test responsive layouts** on mobile devices
5. **Use hover effects** for interactive elements
6. **Maintain spacing** using CSS variables (--spacing-*)
7. **Keep accessibility** in mind (color contrast, labels)

---

## Support

For questions or issues with the UI redesign:
1. Check this reference guide
2. Review the UI_REDESIGN_SUMMARY.md
3. Inspect existing implementations in the templates
4. Test changes in multiple browsers

---

Last Updated: 2024
Version: 1.0