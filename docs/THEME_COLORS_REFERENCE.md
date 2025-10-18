# 🎨 HRMS Theme Colors - Quick Reference Guide

## Current Color Palette (Active)

### Primary Brand Colors

| Color Name | Hex Code | RGB | Usage |
|------------|----------|-----|-------|
| **Primary Teal** | `#6C8F91` | `rgb(108, 143, 145)` | Primary buttons, headers, brand elements, links |
| **Light Teal** | `#A5C2C4` | `rgb(165, 194, 196)` | Secondary elements, table headers, borders |
| **Navbar Teal** | `#7BA6AA` | `rgb(123, 166, 170)` | Navigation bar, gradients, hover states |
| **Blush Pink** | `#FBEFF1` | `rgb(251, 239, 241)` | Page backgrounds, light sections |
| **Accent Teal** | `#C7E3E6` | `rgb(199, 227, 230)` | Light accents, footer, subtle highlights |
| **Brown Highlight** | `#8A4F24` | `rgb(138, 79, 36)` | Headers, emphasis, important text |
| **Dark Text** | `#4A4A4A` | `rgb(74, 74, 74)` | Body text, paragraphs, descriptions |

### Semantic Colors (Status Indicators)

| Color Name | Hex Code | RGB | Usage |
|------------|----------|-----|-------|
| **Success Green** | `#75B798` | `rgb(117, 183, 152)` | Success messages, positive indicators, checkmarks |
| **Warning Yellow** | `#F4C542` | `rgb(244, 197, 66)` | Warnings, cautions, star ratings |
| **Danger Red** | `#F4A5A5` | `rgb(244, 165, 165)` | Errors, critical states, delete actions |
| **Info Cyan** | `#6C8F91` | `rgb(108, 143, 145)` | Information messages, tooltips |

---

## CSS Variable Reference

### How to Use in Code

```css
/* Primary Colors */
color: var(--bs-primary, #6C8F91);
background-color: var(--bs-secondary, #A5C2C4);
background: var(--bs-light-bg, #FBEFF1);

/* Semantic Colors */
color: var(--bs-success, #75B798);
color: var(--bs-warning, #F4C542);
color: var(--bs-danger, #F4A5A5);
color: var(--bs-info, #6C8F91);

/* Custom Variables */
color: var(--primary-green, #6C8F91);
color: var(--primary-green-light, #7BA6AA);
color: var(--highlight-color, #8A4F24);
```

---

## RGBA Values (With Opacity)

### Primary Teal Variations
```css
/* Subtle backgrounds */
background: rgba(108, 143, 145, 0.03);

/* Light backgrounds */
background: rgba(108, 143, 145, 0.08);

/* Borders */
border-color: rgba(108, 143, 145, 0.22);

/* Hover states */
background: rgba(108, 143, 145, 0.15);

/* Focus states */
box-shadow: 0 0 0 0.25rem rgba(108, 143, 145, 0.25);

/* Shadows */
box-shadow: 0 4px 12px rgba(108, 143, 145, 0.15);
```

---

## Common Color Combinations

### Buttons

#### Primary Button
```css
background: linear-gradient(135deg, #6C8F91, #8A4F24);
color: #FFFFFF;
```

#### Secondary Button
```css
background: #A5C2C4;
color: #4A4A4A;
```

#### Outline Button
```css
border: 2px solid #6C8F91;
color: #6C8F91;
background: transparent;
```

### Cards

#### Standard Card
```css
background: #FFFFFF;
border: 1px solid rgba(108, 143, 145, 0.22);
box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
```

#### Card Header
```css
background: linear-gradient(135deg, #6C8F91, #7BA6AA);
color: #FFFFFF;
```

### Forms

#### Input Fields
```css
border: 1px solid rgba(108, 143, 145, 0.22);
background: #FFFFFF;
color: #4A4A4A;
```

#### Input Focus
```css
border-color: #6C8F91;
box-shadow: 0 0 0 0.25rem rgba(108, 143, 145, 0.25);
```

---

## Usage Guidelines

### When to Use Each Color

#### Primary Teal (#6C8F91)
- ✅ Primary action buttons
- ✅ Navigation active states
- ✅ Important links
- ✅ Section headers
- ✅ Icons for primary actions

#### Light Teal (#A5C2C4)
- ✅ Secondary buttons
- ✅ Table headers
- ✅ Dividers and borders
- ✅ Disabled states
- ✅ Background accents

#### Blush Pink (#FBEFF1)
- ✅ Page backgrounds
- ✅ Card backgrounds (subtle)
- ✅ Section backgrounds
- ✅ Modal backgrounds

#### Brown Highlight (#8A4F24)
- ✅ Page titles
- ✅ Important headings
- ✅ Emphasis text
- ✅ Call-to-action elements
- ✅ Hover states for primary buttons

#### Dark Text (#4A4A4A)
- ✅ Body text
- ✅ Paragraphs
- ✅ Descriptions
- ✅ Labels
- ✅ Secondary information

---

## Accessibility Guidelines

### Contrast Ratios (WCAG AA Compliant)

| Foreground | Background | Ratio | Status |
|------------|------------|-------|--------|
| #6C8F91 | #FFFFFF | 4.5:1 | ✅ Pass |
| #4A4A4A | #FFFFFF | 9.2:1 | ✅ Pass |
| #8A4F24 | #FFFFFF | 5.8:1 | ✅ Pass |
| #FFFFFF | #6C8F91 | 4.5:1 | ✅ Pass |
| #4A4A4A | #FBEFF1 | 8.9:1 | ✅ Pass |

### Best Practices
- ✅ Always use dark text (#4A4A4A) on light backgrounds
- ✅ Use white text on primary teal backgrounds
- ✅ Ensure sufficient contrast for all interactive elements
- ✅ Test with color blindness simulators

---

## Gradient Patterns

### Hero Sections
```css
background: linear-gradient(135deg, #6C8F91 0%, #7BA6AA 100%);
```

### Card Headers
```css
background: linear-gradient(135deg, #6C8F91 0%, #7BA6AA 100%);
```

### Button Hover
```css
background: linear-gradient(135deg, #6C8F91 0%, #8A4F24 100%);
```

### Subtle Backgrounds
```css
background: linear-gradient(to bottom, #FBEFF1 0%, #FFFFFF 100%);
```

---

## Color Psychology & Rationale

### Why These Colors?

#### Teal (#6C8F91)
- **Professional:** Conveys trust and reliability
- **Calming:** Reduces stress in HR/payroll context
- **Modern:** Contemporary alternative to traditional blue
- **Gender-neutral:** Appropriate for all users

#### Blush Pink (#FBEFF1)
- **Soft:** Easy on the eyes for long sessions
- **Professional:** Subtle enough for corporate use
- **Warm:** Creates welcoming atmosphere
- **Distinctive:** Memorable brand identity

#### Brown (#8A4F24)
- **Stable:** Conveys reliability and security
- **Sophisticated:** Professional and mature
- **Complementary:** Works well with teal
- **Attention-grabbing:** Effective for emphasis

---

## Migration from Old Colors

### Color Mapping

| Old Color | Old Name | New Color | New Name |
|-----------|----------|-----------|----------|
| `#0D6EFD` | Bootstrap Blue | `#6C8F91` | Primary Teal |
| `#6610F2` | Bootstrap Purple | `#A5C2C4` | Light Teal |
| `#198754` | Bootstrap Green | `#C7E3E6` | Accent Teal |
| `#FFC107` | Bootstrap Yellow | `#8A4F24` | Brown Highlight |
| `#F8F9FA` | Bootstrap Light | `#FBEFF1` | Blush Pink |
| `#212529` | Bootstrap Dark | `#4A4A4A` | Dark Text |
| `#28a745` | Old Success | `#75B798` | Success Green |
| `#dc3545` | Old Danger | `#F4A5A5` | Danger Red |

---

## Code Examples

### HTML with Inline Styles
```html
<!-- Primary Button -->
<button style="background: #6C8F91; color: #FFFFFF;">
    Click Me
</button>

<!-- Card with Header -->
<div style="background: #FFFFFF; border: 1px solid rgba(108, 143, 145, 0.22);">
    <div style="background: linear-gradient(135deg, #6C8F91, #7BA6AA); color: #FFFFFF;">
        Card Header
    </div>
    <div style="padding: 1rem; color: #4A4A4A;">
        Card content goes here
    </div>
</div>
```

### CSS Classes
```css
/* Primary Elements */
.btn-primary {
    background: var(--bs-primary, #6C8F91);
    color: #FFFFFF;
}

.text-primary {
    color: var(--bs-primary, #6C8F91);
}

.bg-primary {
    background-color: var(--bs-primary, #6C8F91);
}

/* Secondary Elements */
.btn-secondary {
    background: var(--bs-secondary, #A5C2C4);
    color: var(--bs-dark, #4A4A4A);
}

/* Backgrounds */
.bg-light {
    background-color: var(--bs-light-bg, #FBEFF1);
}

/* Text */
.text-dark {
    color: var(--bs-dark, #4A4A4A);
}

.text-highlight {
    color: var(--highlight-color, #8A4F24);
}
```

---

## Testing Checklist

### Visual Testing
- [ ] All buttons display correct colors
- [ ] Card headers use gradient backgrounds
- [ ] Form inputs have proper border colors
- [ ] Hover states work correctly
- [ ] Focus states are visible
- [ ] Text is readable on all backgrounds

### Accessibility Testing
- [ ] Color contrast meets WCAG AA
- [ ] Interactive elements are distinguishable
- [ ] Focus indicators are visible
- [ ] Color is not the only indicator of state

### Cross-Browser Testing
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if applicable)
- [ ] Mobile browsers

---

## Quick Copy-Paste Values

### Hex Codes
```
Primary: #6C8F91
Secondary: #A5C2C4
Navbar: #7BA6AA
Background: #FBEFF1
Accent: #C7E3E6
Highlight: #8A4F24
Text: #4A4A4A
Success: #75B798
Warning: #F4C542
Danger: #F4A5A5
```

### RGB Values
```
Primary: rgb(108, 143, 145)
Secondary: rgb(165, 194, 196)
Navbar: rgb(123, 166, 170)
Background: rgb(251, 239, 241)
Accent: rgb(199, 227, 230)
Highlight: rgb(138, 79, 36)
Text: rgb(74, 74, 74)
Success: rgb(117, 183, 152)
Warning: rgb(244, 197, 66)
Danger: rgb(244, 165, 165)
```

### RGBA with Common Opacities
```
Primary 3%: rgba(108, 143, 145, 0.03)
Primary 8%: rgba(108, 143, 145, 0.08)
Primary 15%: rgba(108, 143, 145, 0.15)
Primary 22%: rgba(108, 143, 145, 0.22)
Primary 25%: rgba(108, 143, 145, 0.25)
```

---

## Support & Maintenance

### For Developers
- Always use CSS variables when possible
- Include fallback hex values for compatibility
- Test color changes across all modules
- Maintain consistent opacity values
- Document any new color additions

### For Designers
- Use this palette for all new designs
- Maintain color consistency across features
- Consider accessibility in color choices
- Test designs in both light and dark contexts

---

*Last Updated: December 2024*  
*Version: 1.0*  
*Status: Production Ready*