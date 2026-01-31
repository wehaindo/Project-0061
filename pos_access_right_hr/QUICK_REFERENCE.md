# Quick Reference: Open Cash Drawer Migration

## 📦 What Changed?

### ➡️ Feature Moved From:
**`em_pos_open_cash_drawer`** → **`pos_access_right_hr`**

---

## 🎯 Key Change: Permission Model

### Before 🔴
```python
# POS Configuration Level
pos.config.allow_open_cash_d = True/False
→ All cashiers have same permission
```

### After 🟢
```python
# Employee Level
hr.employee.allow_open_cash_drawer = True/False
→ Each cashier has individual permission
```

---

## 📁 Files Overview

### Created Files (6)
```
pos_access_right_hr/
├── static/src/
│   ├── js/
│   │   ├── OpenCashDrawer.js           ⭐ NEW
│   │   └── jQuery.print.min.js         📋 COPIED
│   ├── css/
│   │   └── pos_cash_drawer.css         📋 COPIED
│   └── xml/
│       └── PaymentScreenCashDrawer.xml ⭐ NEW
├── OPEN_CASH_DRAWER_MIGRATION.md       📄 NEW
└── MIGRATION_SUMMARY.md                 📄 NEW
```

### Modified Files (6)
```
pos_access_right_hr/
├── models/
│   ├── hr_employee.py                  ✏️ MODIFIED
│   └── pos_session.py                  ✏️ MODIFIED
├── views/
│   └── hr_employee_views.xml           ✏️ MODIFIED
├── static/src/
│   ├── js/
│   │   └── ActionpadWidgetAccessRight.js  ✏️ MODIFIED
│   └── xml/
│       └── ActionpadWidgetAccessRight.xml ✏️ MODIFIED
└── __manifest__.py                     ✏️ MODIFIED
```

---

## 🔑 New Field

```python
# hr.employee.base
allow_open_cash_drawer = fields.Boolean(
    string="POS-Allow Open Cash Drawer",
    help="Allow opening cash drawer from POS screen",
    default=False
)
```

**Location**: Employees → Access Right Tab

---

## 🖥️ User Interface

### Product Screen
```
┌─────────────────────────────┐
│     ActionPad Widget        │
├─────────────────────────────┤
│  👤 Customer │ 📦 Open CB   │  ⭐ Inline Layout
│  💳 Payment (Larger)        │
└─────────────────────────────┘
```

### Payment Screen
```
┌─────────────────────────────┐
│    Payment Controls         │
├─────────────────────────────┤
│  [Validate]                 │
│  [Invoice]                  │
│  📦 Open Cashbox    ⭐ NEW  │
└─────────────────────────────┘
```

---

## 🔐 Permission Check Logic

```javascript
// In ActionpadWidgetAccessRight.js
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

---

## 💬 Confirmation Popup

```
┌─────────────────────────────────────┐
│         Confirmation                │
├─────────────────────────────────────┤
│  [John Doe on 31-01-2026 14:30:45]  │
│  want to open cash drawer?          │
│  Please input reason:                │
│                                      │
│  ┌─────────────────────────────┐    │
│  │ Count cash                  │    │
│  └─────────────────────────────┘    │
│                                      │
│     [Cancel]        [Okay]           │
└─────────────────────────────────────┘
```

---

## 📝 Activity Log Format

```
Screen: Product Screen / Payment Screen
Action: Open Cash Drawer - [reason entered by user]
User ID: [POS user ID]
Cashier ID: [Employee ID]
Config ID: [POS Config ID]
Session ID: [POS Session ID]
Timestamp: [Auto-generated]
```

---

## ⚙️ Setup in 3 Steps

### Step 1: Upgrade Module
```
Apps → Search: pos_access_right_hr → Upgrade
```

### Step 2: Configure Employee
```
Employees → [Select Employee] → Access Right Tab
☑ POS-Allow Open Cash Drawer
[Save]
```

### Step 3: Test
```
Point of Sale → New Session
Login as configured employee
→ Look for "Open Cashbox" button
```

---

## 🔍 Troubleshooting Quick Guide

| Issue | Solution |
|-------|----------|
| Button not showing | Check employee's "Allow Open Cash Drawer" field |
| Button showing but disabled | Check if pos_hr module is installed |
| Drawer not opening | Check printer/cash drawer hardware connection |
| No activity log | Verify weha_smart_pos_aeon_activity_log is installed |

---

## ✅ Checklist for Migration

- [ ] Backup database
- [ ] Upgrade `pos_access_right_hr` module
- [ ] Configure employee permissions
- [ ] Test with multiple employees
- [ ] Verify activity logging works
- [ ] Check both Product and Payment screens
- [ ] Test confirmation popup
- [ ] Verify cash drawer opens
- [ ] (Optional) Uninstall `em_pos_open_cash_drawer`

---

## 📊 Comparison Table

| Feature | em_pos_open_cash_drawer | pos_access_right_hr |
|---------|------------------------|---------------------|
| Permission Level | POS Config | Employee |
| Granularity | All cashiers same | Per cashier |
| Configuration | POS Settings | Employee form |
| UI Location | ActionPad + Payment | ActionPad + Payment |
| Confirmation | ❌ No | ✅ Yes + Reason |
| Activity Log | Basic | Detailed |
| Integration | Standalone | With access rights |

---

## 🎨 Dependencies

```
pos_access_right_hr
├── base
├── hr
├── point_of_sale
├── pos_hr
└── weha_smart_pos_aeon_activity_log ⭐ NEW
```

---

## 📞 Support

**Issues?** Check:
1. Employee access rights configuration
2. Activity log module installation
3. Browser console for errors
4. Odoo server logs

**Documentation**:
- Full guide: `OPEN_CASH_DRAWER_MIGRATION.md`
- Technical details: `MIGRATION_SUMMARY.md`

---

**Version**: 16.0.1.0.0  
**Date**: January 31, 2026  
**Status**: ✅ Production Ready
