# Open Cash Drawer - UI Layout Guide

## Overview
The Open Cashbox button is designed to maintain the consistent numpad style of the POS interface by being positioned inline with the Customer button.

---

## Layout Structure

### Product Screen - ActionPad Widget

#### Visual Layout
```
┌─────────────────────────────────────┐
│         ActionPad Widget            │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────┬──────────────┐   │
│  │   Customer   │ Open Cashbox │   │ ← Row 1 (60px each)
│  │    👤        │     📦       │   │
│  └──────────────┴──────────────┘   │
│  ┌───────────────────────────┐     │
│  │                           │     │
│  │        Payment            │     │ ← Row 2 (132px)
│  │          💳 →            │     │
│  │                           │     │
│  └───────────────────────────┘     │
│                                     │
└─────────────────────────────────────┘
```

#### Button Heights
- **Customer Button**: 60px
- **Open Cashbox Button**: 60px (same height as Customer)
- **Payment Button**: 132px (equals Customer + Open Cashbox heights)

#### CSS Styling
```css
.pos .actionpad .button.set-partner {
    height: 60px;
}

.pos .actionpad .button.js-open-cashdrawer {
    height: 60px;
}

.pos .actionpad .button.pay {
    height: 132px;
}
```

---

## Responsive Behavior

### When Permission is GRANTED
```
┌─────────────────────────────────────┐
│  ┌──────────────┬──────────────┐   │
│  │   Customer   │ Open Cashbox │   │
│  └──────────────┴──────────────┘   │
│  ┌───────────────────────────┐     │
│  │        Payment            │     │
│  └───────────────────────────┘     │
└─────────────────────────────────────┘
```

### When Permission is DENIED
```
┌─────────────────────────────────────┐
│  ┌───────────────────────────┐     │
│  │        Customer           │     │ ← Full width, 120px
│  └───────────────────────────┘     │
│  ┌───────────────────────────┐     │
│  │        Payment            │     │ ← Full width, 120px
│  └───────────────────────────┘     │
└─────────────────────────────────────┘
```
*Note: Default Odoo layout when Open Cashbox button is hidden*

---

## XML Template Structure

### ActionpadWidget Template
```xml
<div class="actionpad">
    <!-- Dynamic Styling (only when permission exists) -->
    <t t-if="allow_open_cash_drawer">
        <style>
            .pos .actionpad .button.set-partner { height: 60px; }
            .pos .actionpad .button.js-open-cashdrawer { height: 60px; }
            .pos .actionpad .button.pay { height: 132px; }
        </style>
    </t>
    
    <!-- Row 1: Customer Button -->
    <button class="button set-partner" ...>
        <i class="fa fa-user" /> Customer
    </button>
    
    <!-- Row 1: Open Cashbox Button (conditional) -->
    <button t-if="allow_open_cash_drawer" 
            class='button js-open-cashdrawer' ...>
        <i class='fa fa-archive' /> Open Cashbox
    </button>
    
    <!-- Row 2: Payment Button -->
    <button class="button pay validation" ...>
        <div class="pay-circle">
            <i class="fa fa-chevron-right" />
        </div>
        Payment
    </button>
</div>
```

---

## Alignment with Numpad Style

### Standard Odoo Numpad Layout
```
┌─────────────────────┐
│   7   │   8   │  9  │
├───────┼───────┼─────┤
│   4   │   5   │  6  │
├───────┼───────┼─────┤
│   1   │   2   │  3  │
├───────┼───────┼─────┤
│   +/- │   0   │  .  │
└─────────────────────┘
```

### ActionPad Layout (with Open Cashbox)
```
┌─────────────────────┐
│ Customer│Open CB    │  ← Same 2-column concept
├───────────────────────┤
│                       │
│      Payment          │  ← Spans full width
│                       │
└─────────────────────┘
```

**Key Design Principle**: 
- Maintains the 2-column grid concept used in numpad
- Customer + Open Cashbox = Same width as Payment button
- Height proportions: 60 + 60 = 120 < 132 (Payment slightly taller)

---

## Button States & Visual Feedback

### Customer Button States
```
┌──────────────┐
│  👤 Customer │  ← Enabled
└──────────────┘

┌──────────────┐
│  👤 Customer │  ← Disabled (grayed out)
└──────────────┘
  #E0E2E6 background
  #666666 text color
```

### Open Cashbox Button States
```
┌──────────────┐
│  📦 Open CB  │  ← Normal state
└──────────────┘

┌──────────────┐
│  📦 Open CB  │  ← Hover state (lighter)
└──────────────┘

┌──────────────┐
│  📦 Open CB  │  ← Click/Active state
└──────────────┘
```

### Payment Button States
```
┌───────────────────────────┐
│        Payment            │  ← Normal
│          💳 →            │
└───────────────────────────┘

┌───────────────────────────┐
│        Payment            │  ← Highlighted
│          💳 → ⚡          │  ← pay-circle.highlight
└───────────────────────────┘

┌───────────────────────────┐
│        Payment            │  ← Disabled
│          💳 →            │
└───────────────────────────┘
  #E0E2E6 background
```

---

## Permission-Based Rendering

### JavaScript Logic
```javascript
get allow_open_cash_drawer() {
    if (this.env.pos.config.module_pos_hr) {
        const cashierId = this.env.pos.get_cashier().id;
        const sessionAccess = this.env.pos.session_access
            .find(access => access.id === cashierId);
        return sessionAccess ? 
            sessionAccess.allow_open_cash_drawer : false;
    }
    return false;
}
```

### Rendering Flow
```
1. User logs into POS
   ↓
2. Load cashier data (including allow_open_cash_drawer)
   ↓
3. Render ActionpadWidget
   ↓
4. Check: allow_open_cash_drawer === true?
   ↓
   YES                          NO
   ↓                            ↓
   Show button                  Hide button
   Apply inline styles          Use default styles
   (60+60+132 layout)          (120+120 layout)
```

---

## Comparison with Original Implementation

### em_pos_open_cash_drawer (Original)
```
Config-based: pos.config.allow_open_cash_d
All cashiers: Same permission

Layout:
┌─────────────────────┐
│     Customer        │ ← Full width
├─────────────────────┤
│     Payment         │ ← Reduced to 108px
├─────────────────────┤
│   Open Cashbox      │ ← Additional row
└─────────────────────┘
```

### pos_access_right_hr (New Implementation)
```
Employee-based: hr.employee.allow_open_cash_drawer
Per cashier: Individual permission

Layout:
┌─────────────────────┐
│ Customer│Open CB    │ ← Split row (60px each)
├─────────────────────┤
│     Payment         │ ← Expanded to 132px
└─────────────────────┘
```

**Improvement**: 
- ✅ More compact (2 rows vs 3 rows)
- ✅ Better use of space
- ✅ Maintains visual balance
- ✅ Consistent with numpad grid concept

---

## Mobile Considerations

### Desktop/Tablet View
```
┌─────────────────────────────┐
│ Customer     │ Open Cashbox │
├──────────────────────────────┤
│         Payment              │
└─────────────────────────────┘
```

### Mobile View (if env.isMobile)
```
┌─────────────────┐
│    Customer     │
├─────────────────┤
│  Open Cashbox   │
├─────────────────┤
│    Payment      │
├─────────────────┤
│      Back       │  ← Additional mobile button
└─────────────────┘
```
*Note: Mobile layout may need adjustment - consider stacking buttons vertically*

---

## Accessibility Considerations

### ARIA Labels
```html
<!-- Customer Button -->
<i class="fa fa-user" 
   role="img" 
   aria-label="Customer" 
   title="Customer" />

<!-- Open Cashbox Button -->
<i class='fa fa-archive' 
   role="img" 
   aria-label="Open Cash Drawer" 
   title="Open Cash Drawer" />

<!-- Payment Button -->
<i class="fa fa-chevron-right" 
   role="img" 
   aria-label="Pay" 
   title="Pay" />
```

### Keyboard Navigation
- Tab order: Customer → Open Cashbox → Payment
- Enter/Space: Activates button
- Focus visible: Standard browser outline

---

## Testing Checklist

### Visual Testing
- [ ] Customer and Open Cashbox buttons same height (60px)
- [ ] Buttons aligned horizontally on same row
- [ ] Payment button properly sized (132px)
- [ ] No gaps or overlaps between buttons
- [ ] Icons properly centered
- [ ] Text properly centered and readable

### Functional Testing
- [ ] Click Customer button - opens customer selection
- [ ] Click Open Cashbox - shows confirmation popup
- [ ] Click Payment - proceeds to payment screen
- [ ] Hover states work correctly
- [ ] Disabled states display properly
- [ ] Permission toggle (enable/disable in employee) works

### Responsive Testing
- [ ] Desktop view: buttons inline as designed
- [ ] Tablet view: buttons maintain layout
- [ ] Mobile view: buttons stack appropriately
- [ ] Different screen sizes: no layout breaks

### Permission Testing
- [ ] Employee with permission: button visible
- [ ] Employee without permission: button hidden
- [ ] Layout adjusts correctly when button hidden/shown
- [ ] Switch cashier: button visibility updates

---

## Troubleshooting

### Button Not Showing
**Check:**
1. Employee has `allow_open_cash_drawer = True`
2. `module_pos_hr` is enabled in POS config
3. Cashier is logged in (not just default user)
4. Browser cache cleared after upgrade

### Layout Issues
**Check:**
1. CSS is loading correctly
2. No conflicting styles from other modules
3. Browser console for JavaScript errors
4. Inspect element to verify actual heights

### Height Mismatch
**Check:**
1. Style tag is rendering (view source)
2. CSS specificity (use `.pos .actionpad .button`)
3. Other modules overriding styles
4. Browser zoom level at 100%

---

## Future Enhancements

### Potential Improvements
1. **Icon customization**: Allow different icon per configuration
2. **Color coding**: Different colors for different button types
3. **Tooltips**: Show permission info on hover
4. **Animation**: Subtle transition when button appears/disappears
5. **Shortcut keys**: Keyboard shortcuts for quick access

### Mobile Optimization
- Consider separate mobile layout
- Touch-friendly button sizes (minimum 44x44 dp)
- Swipe gestures for quick access

---

**Document Version**: 1.0  
**Last Updated**: January 31, 2026  
**Status**: ✅ Production Ready
