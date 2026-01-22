# Weha Smart POS - Remove Duplicate Order Lines

## Overview
Simple wizard to detect and remove duplicate POS order lines by session. Select sessions, review duplicates, and remove with one click.

## Features

### ✅ **Auto-Scan on Open**
- Wizard automatically scans when opened
- No manual "scan" button needed
- Instant results

### ✅ **Session-Based**
- Select one or multiple POS sessions
- Leave empty to process all sessions
- All orders in session processed automatically

### ✅ **Smart Duplicate Detection**
- Same product + price + discount + taxes = Duplicate
- First occurrence kept
- All subsequent removed

### ✅ **Simple 3-Step Process**
1. Select sessions (auto-scans)
2. Review results
3. Remove duplicates

## Installation

1. Copy module to addons directory
2. Update Apps List
3. Install "Weha Smart POS - Remove Duplicate Order Lines"

## Usage Guide

### Step 1: Open Wizard
**Point of Sale → Remove Duplicate Lines**

### Step 2: Select Sessions
**Option A: Select Specific Sessions**
- Choose sessions from dropdown
- Results appear automatically

**Option B: All Sessions**
- Leave field empty
- Click "Rescan" to process all

### Step 3: Review Results (3 Tabs)
- **Session Summary**: Overview per session
- **Order Summary**: Orders with duplicates
- **Duplicate Lines**: Exact lines to remove

### Step 4: Remove
- Click "Continue to Remove"
- Review warning
- Click "Remove Duplicates"
- Done!

## Example

```
Input:
- Session: POS/2024/001
- Auto-scan runs...

Results:
├─ Orders in session: 50
├─ Orders with duplicates: 12
└─ Duplicate lines found: 35

Action:
- Click "Continue to Remove"
- Click "Remove Duplicates"

Result:
✓ 35 duplicate lines removed
✓ 35 unique lines kept
✓ Order totals recalculated
```

## Duplicate Logic

A line is duplicate if **ALL** match:
- ✓ Same product_id
- ✓ Same price_unit
- ✓ Same discount
- ✓ Same taxes

**First = KEEP**  
**Rest = REMOVE**

## Features

### Auto-Scan
- Opens → Scans immediately
- Change sessions → Auto-rescans
- Click "Rescan" → Scans again

### Three-Level Summary
1. **Session level**: Which sessions have duplicates
2. **Order level**: Which orders have duplicates
3. **Line level**: Exact duplicate lines

### Safe Removal
- Review before delete
- Warning confirmation
- Automatic total recalculation
- Error tracking

## Best Practices

1. **Backup** database first
2. **Test** with one session
3. **Review** all three tabs
4. **Process** during off-peak
5. **Check** results summary

## Common Scenarios

### Scenario 1: Today's Session
```
1. Open wizard
2. Select today's session
3. Review auto-scan results
4. Remove duplicates
```

### Scenario 2: Multiple Sessions
```
1. Open wizard
2. Select 3 sessions
3. Review results
4. Remove duplicates
```

### Scenario 3: All Sessions
```
1. Open wizard
2. Leave sessions empty
3. Click "Rescan"
4. Review results
5. Remove duplicates
```

## Troubleshooting

**Q: No results shown?**
A: Make sure sessions are selected or click "Rescan"

**Q: Want to process all sessions?**
A: Clear session field and click "Rescan"

**Q: Need to change sessions?**
A: Just select different sessions, auto-rescans

**Q: Errors after removal?**
A: Check error messages in "Done" state

## Technical

### Models
- `remove.duplicate.wizard` - Main wizard
- `remove.duplicate.line` - Line details
- `remove.duplicate.order.summary` - Order summary
- `remove.duplicate.session.summary` - Session summary

### No Inheritance
- Does NOT modify pos.order
- Does NOT modify pos.order.line
- Does NOT modify pos.session
- Pure wizard approach

## Support

- Check Odoo logs
- Verify permissions
- Contact Weha Support

## Version
16.0.1.0.0

## License
LGPL-3

## Author
Weha (https://www.weha-id.com)
