# CRITICAL FIX: Disable Login Screen Field Not Loading

## Root Cause Found! 🎯

The `disable_login_screen` field was **not being returned** by the `get_barcodes_and_pin_hashed()` method in `hr_employee.py`.

## The Problem

The field was defined in THREE places, but they weren't all synchronized:

### ❌ Before Fix:

1. **`_pos_data_process`** (pos_session.py) - ✅ Loaded `disable_login_screen`
2. **`_get_pos_ui_hr_employee`** (pos_session.py) - ✅ Loaded `disable_login_screen`
3. **`get_barcodes_and_pin_hashed`** (hr_employee.py) - ❌ **DID NOT load** `disable_login_screen`

The POS uses data from `get_barcodes_and_pin_hashed()` which was missing the field!

## The Solution

### File: `models/hr_employee.py`

```python
def get_barcodes_and_pin_hashed(self):
    if not self.env.user.has_group('point_of_sale.group_pos_user'):
        return []
    visible_emp_ids = self.search([('id', 'in', self.ids)])
    employees_data = self.sudo().search_read([('id', 'in', visible_emp_ids.ids)], [
        'barcode', 
        'pin', 
        'fingerprint_primary', 
        'disable_login_screen'  # ← ADDED THIS
    ])

    for e in employees_data:
        e['barcode'] = hashlib.sha1(e['barcode'].encode('utf8')).hexdigest() if e['barcode'] else False
        e['pin'] = hashlib.sha1(e['pin'].encode('utf8')).hexdigest() if e['pin'] else False
        e['fingerprint_primary'] = e['fingerprint_primary']
        e['disable_login_screen'] = e.get('disable_login_screen', False)  # ← ADDED THIS
    return employees_data
```

### File: `static/src/js/Screen/LoginScreen.js`

Added comprehensive debugging to see what data is actually loaded:

```javascript
async selectEmployee() {
    // Debug logging
    console.log("All employees:", this.env.pos.employees);
    this.env.pos.employees.forEach(emp => {
        console.log(`Employee: ${emp.name}, disable_login_screen: ${emp.disable_login_screen}`);
    });
    
    const employees = this.env.pos.employees
        .filter((employee) => employee.id !== this.env.pos.get_cashier().id)
        .filter((employee) => {
            const shouldExclude = employee.disable_login_screen;
            console.log(`Filtering ${employee.name}: will ${shouldExclude ? 'EXCLUDE' : 'INCLUDE'}`);
            return !shouldExclude;
        })
        // ...rest of code
}
```

## Deployment Steps

### 1. Upgrade the Module
```bash
odoo-bin -c odoo.conf -d aeondb -u weha_smart_pos_aeon_pos_access_rights --stop-after-init
```

### 2. Restart Odoo Service
```bash
sudo systemctl restart odoo
# or
sudo service odoo restart
```

### 3. Close and Reopen POS Session
- Close current POS session
- Start a NEW session (data loads at session start)

### 4. Clear Browser Cache
- Press `Ctrl + Shift + R` (hard refresh)
- Or open in Incognito mode

### 5. Test
1. Open POS
2. Click login/change cashier
3. Open browser console (F12)
4. Look for debug logs showing:
   ```
   Employee: John Doe, disable_login_screen: true
   Filtering John Doe: will EXCLUDE
   ```
5. Verify cashier with `disable_login_screen=true` is NOT in the list

## Files Modified

1. ✅ `models/hr_employee.py` - Added `disable_login_screen` to `get_barcodes_and_pin_hashed()`
2. ✅ `models/pos_session.py` - Added field to `_pos_data_process()`
3. ✅ `static/src/js/Screen/LoginScreen.js` - Added filtering with debug logs
4. ✅ `views/hr_employee_view.xml` - Added field to form view

## Verification

Run this in Odoo shell to verify:
```python
# Open shell
odoo-bin shell -c odoo.conf -d aeondb

# Run test
employees = env['hr.employee'].search([])
for emp in employees:
    if emp.disable_login_screen:
        print(f"✓ {emp.name} - Login DISABLED")

# Test what get_barcodes_and_pin_hashed returns
test_emp = env['hr.employee'].search([('disable_login_screen', '=', True)], limit=1)
if test_emp:
    data = test_emp.get_barcodes_and_pin_hashed()
    print("\nData returned by get_barcodes_and_pin_hashed:")
    print(data)
    print(f"\nContains disable_login_screen? {'disable_login_screen' in data[0] if data else 'NO DATA'}")
```

## Expected Result

After the fix:
- ✅ Field loads from database
- ✅ Field included in `get_barcodes_and_pin_hashed()` response
- ✅ Field available in JavaScript `this.env.pos.employees`
- ✅ Filter works correctly
- ✅ Cashier with `disable_login_screen=true` does NOT appear in login screen

## Why This Happened

The `get_barcodes_and_pin_hashed()` method is specifically designed to return employee authentication data to the POS. It was returning barcode, PIN, and fingerprint, but we forgot to add the new `disable_login_screen` field to this critical method.

This is a common pattern in Odoo POS where data must be explicitly included in loader methods to be available on the frontend.
