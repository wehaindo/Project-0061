# Troubleshooting: Disable Login Screen Not Working

## Problem
Cashiers with `disable_login_screen = True` are still appearing in the POS login screen.

## Diagnostic Steps

### 1. Check Backend - Verify Field Value
```bash
# Open Odoo shell
odoo-bin shell -c odoo.conf -d aeondb
```

```python
# Run this in shell
employees = env['hr.employee'].search([])
for emp in employees:
    print(f"{emp.name}: disable_login_screen = {emp.disable_login_screen}")
```

**Expected**: You should see `True` for the cashier you disabled.

### 2. Check Module Upgrade
```bash
# Stop Odoo
# Then upgrade the module
odoo-bin -c odoo.conf -d aeondb -u weha_smart_pos_aeon_pos_access_rights --stop-after-init

# Start Odoo again
```

**Important**: Module upgrade is REQUIRED after code changes!

### 3. Check POS Session
- Close current POS session
- Start a NEW POS session
- Data is loaded when session starts, not continuously

### 4. Check Browser Cache
- Press `Ctrl + Shift + R` (hard refresh)
- Or clear browser cache completely
- Or open in Incognito/Private mode

### 5. Check JavaScript Console

Open browser DevTools (F12) and look for these logs:
```
All employees: [...]
Employee: John Doe, ID: 5, disable_login_screen: true
Filtering John Doe: disable_login_screen=true, will EXCLUDE
```

**Expected**: 
- `disable_login_screen: true` for disabled cashier
- "will EXCLUDE" message for that cashier

**If you see**:
- `disable_login_screen: undefined` → Field not loaded from backend
- `disable_login_screen: false` → Field value not set in database

### 6. Check Server Logs

Look in Odoo logs for:
```
INFO ? odoo.addons.weha_smart_pos_aeon_pos_access_rights.models.pos_session: 
Total employees loaded: X
Employees with disable_login_screen: Y
```

**Expected**: Y should be > 0 if you have disabled any cashiers

## Common Issues & Solutions

### Issue 1: Field is `undefined` in JavaScript
**Cause**: Field not loaded from backend  
**Solution**: 
1. Check `_pos_data_process` includes `disable_login_screen` in field list
2. Upgrade module
3. Restart POS session

### Issue 2: Field is `false` but should be `true`
**Cause**: Database not updated  
**Solution**:
1. Open employee form in Odoo backend
2. Go to "POS Security" tab
3. Check "Disable Login Screen"
4. Save
5. Verify in database

### Issue 3: Still shows after fixing
**Cause**: Old POS session or cached data  
**Solution**:
1. Close POS session
2. Clear browser cache
3. Start new POS session

### Issue 4: Module upgrade fails
**Cause**: Syntax error or dependency issue  
**Solution**:
```bash
# Check logs for errors
tail -f /var/log/odoo/odoo-server.log

# Or run in foreground to see errors
odoo-bin -c odoo.conf -d aeondb -u weha_smart_pos_aeon_pos_access_rights
```

## Verification Checklist

- [ ] Field `disable_login_screen` exists in `hr.employee` model
- [ ] Field value is `True` for test cashier (checked in form)
- [ ] Module upgraded successfully (no errors in log)
- [ ] POS session closed and reopened
- [ ] Browser cache cleared
- [ ] JavaScript console shows correct field value
- [ ] Server logs show field being loaded
- [ ] Cashier does NOT appear in filtered list

## Quick Test

1. **Enable for one cashier**:
   - HR → Employees → Select cashier
   - POS Security tab → Check "Disable Login Screen"
   - Save

2. **Upgrade module**:
   ```bash
   odoo-bin -c odoo.conf -d aeondb -u weha_smart_pos_aeon_pos_access_rights --stop-after-init
   ```

3. **Test in POS**:
   - Close current session
   - Start new session
   - Open login screen
   - Verify cashier is NOT in the list

4. **Check console** (F12):
   - Should show filtering logs
   - Should show "will EXCLUDE" for disabled cashier

## Still Not Working?

Run the test script:
```bash
odoo-bin shell -c odoo.conf -d aeondb
```

Then paste the contents of `test_disable_login.py`

This will show exactly what data is being loaded and whether the field is present.
