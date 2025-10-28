# HRMS CSS Spacing - Quick Reference Guide

## Color Theme (DO NOT CHANGE)
```css
Primary Teal:      #008080
Secondary Teal:    #66b2b2
Accent Dark Teal:  #004d4d
Text Primary:      #1a1a1a
Background:        #ffffff
```

## Spacing Standards (Use These Values)

### Primary Spacing
| Use Case | Value | Pixels | CSS |
|----------|-------|--------|-----|
| Component padding | `1rem` | 16px | `padding: 1rem;` |
| Grid/flex gaps | `0.75rem` | 12px | `gap: 0.75rem;` |
| Section margins | `1.25rem` | 20px | `margin-bottom: 1.25rem;` |
| Small spacing | `0.5rem` | 8px | `padding: 0.5rem;` |

### Recommended Patterns

**Dashboard Cards:**
```css
.card {
    padding: 1rem;           /* 16px internal padding */
    margin-bottom: 1rem;     /* 16px vertical gap */
}

.dashboard-grid {
    gap: 1rem;               /* 16px between items */
}
```

**Forms:**
```css
.form-section {
    gap: 0.75rem;            /* 12px between form rows */
    padding: 1rem;           /* 16px section padding */
    margin-bottom: 1rem;     /* 16px before next section */
}
```

**Filters:**
```css
.filter-section {
    padding: 1rem;           /* 16px filter padding */
    margin-bottom: 0.75rem;  /* 12px gap to data table */
}
```

**Lists & Tables:**
```css
.list-item {
    padding: 0.75rem;        /* 12px row padding */
}

.list-container {
    gap: 0.5rem;             /* 8px between rows */
}
```

## Responsive Breakpoints

**Desktop:** 1024px+ 
- Use full width
- Standard spacing values

**Tablet:** 768px - 1023px
- Responsive columns (auto-fit/auto-fill)
- Scale spacing proportionally

**Mobile:** < 768px
- Single column layout
- Stack vertically
- Maintain minimum spacing

## CSS Custom Properties (Available)

```css
:root {
    --spacing-1: 0.25rem;   /* 4px */
    --spacing-2: 0.5rem;    /* 8px */
    --spacing-3: 0.75rem;   /* 12px */  ← Use this for gaps
    --spacing-4: 1rem;      /* 16px */  ← Use this for padding
    --spacing-5: 1.25rem;   /* 20px */  ← Use for section margins
    --spacing-6: 1.5rem;    /* 24px */  ← Use sparingly
    --spacing-8: 2rem;      /* 32px */  ← Empty states only
}
```

## Common Components

### Dashboard Grid
```css
.dashboard-wrapper {
    padding: 1rem 1.25rem;   /* 16px vertical, 20px horizontal */
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;               /* 16px between cards */
    margin-bottom: 1.25rem;  /* 20px before next section */
}
```

### Stat Cards
```css
.stat-card {
    padding: 1rem;           /* 16px all around */
    background: var(--white);
    border-radius: var(--radius-lg);
    margin-bottom: 0.75rem;  /* 12px vertical spacing */
}
```

### Filter Section
```css
.filter-card {
    padding: 1rem;           /* 16px filter padding */
    margin-bottom: 0.75rem;  /* 12px gap to table */
    background: var(--grey-50);
    border-radius: var(--radius-lg);
}
```

### Form Groups
```css
.form-group {
    margin-bottom: 1rem;     /* 16px between form groups */
}

.form-label {
    margin-bottom: 0.5rem;   /* 8px label to input */
}
```

### Alert Messages
```css
.alert {
    padding: 0.75rem 1rem;   /* 12px vertical, 16px horizontal */
    margin-bottom: 0.75rem;  /* 12px before next element */
}
```

## DO's and DON'Ts

### ✅ DO:
- Use `1rem` for card/component padding
- Use `0.75rem` for gaps between grid items
- Use `1.25rem` for section margin-bottom
- Use CSS custom properties (--spacing-*)
- Keep spacing consistent within component types
- Test responsive breakpoints

### ❌ DON'T:
- Use hardcoded pixel values (24px, 32px)
- Mix spacing units (combine px and rem)
- Create new spacing values
- Use old spacing values (--spacing-6, --spacing-8 for new components)
- Override spacing without good reason
- Change color theme values

## Migration Guide for Old Code

### Before (Too Much Space)
```css
.card {
    padding: 24px;           /* ❌ 24px is too much */
    margin-bottom: 32px;     /* ❌ 32px is way too much */
}

.grid {
    gap: 24px;               /* ❌ 24px gap creates sparse layout */
}
```

### After (Optimized)
```css
.card {
    padding: 1rem;           /* ✅ 16px is standard */
    margin-bottom: 1rem;     /* ✅ 16px maintains consistency */
}

.grid {
    gap: 1rem;               /* ✅ 16px creates professional density */
}
```

## Performance Tips

1. **Use CSS Custom Properties**: Easier to maintain, update in one place
2. **Leverage rem units**: Scales with root font-size, responsive by default
3. **Group related spacing**: `margin-bottom` instead of individual margins
4. **Use gap for layouts**: Better than margin workarounds

## Browser Compatibility

All spacing values use standard CSS that works in:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers

No special prefixes needed.

## File Reference

- **Main CSS:** `E:/Gobi/Pro/HRMS/hrm/static/css/styles.css`
- **Documentation:** `E:/Gobi/Pro/HRMS/hrm/docs/CSS_OPTIMIZATION_FINAL_COMPLETION.md`
- **Summary:** `E:/Gobi/Pro/HRMS/hrm/CSS_OPTIMIZATION_COMPLETE.txt`

## Quick Contact

For spacing questions, refer to:
1. This quick reference first
2. The final completion report for detailed analysis
3. Existing component examples in styles.css
4. The testing checklist for validation

---

**Last Updated:** December 2024
**Status:** ✅ Production Ready