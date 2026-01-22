# Duplicate Orders Detection Implementation

## Overview
This module has been refactored to detect and remove **duplicate orders** instead of duplicate order lines. Orders are identified as duplicates based on their `access_token` field.

## Changes Made

### 1. Detection Logic Changed
**Before:** Detected duplicate order lines within each order based on product, price, discount, and taxes  
**After:** Detects duplicate orders across sessions based on `access_token`

### 2. Duplicate Identification
- Orders with the same `access_token` are considered duplicates
- Orders without an `access_token` are skipped
- The **first order** (oldest by `date_order`) is kept as the original
- All subsequent orders with the same token are marked as duplicates

### 3. Model Changes

#### Main Wizard Model (`remove.duplicate.wizard`)
**Changed Fields:**
- `orders_with_duplicates` → `total_duplicate_orders`
- `total_duplicate_lines` → removed
- `unique_orders_count` → added
- `duplicate_line_ids` → `duplicate_order_ids` (different model)
- `removed_lines_count` → `removed_orders_count`
- `processed_orders_count` → removed

#### Transient Models
**Removed:**
- `remove.duplicate.line` (was for duplicate order lines)

**Added:**
- `remove.duplicate.order` - Stores details of duplicate orders

**Updated:**
- `remove.duplicate.order.summary` - Now groups by access_token instead of individual orders
- `remove.duplicate.session.summary` - Updated to show duplicate orders instead of duplicate lines

### 4. Algorithm

```python
def _find_duplicate_orders(self, orders):
    """Find duplicate orders based on access_token"""
    orders_by_token = {}
    
    for order in orders:
        token = order.access_token or ''
        if not token:
            continue  # Skip orders without token
            
        if token not in orders_by_token:
            orders_by_token[token] = []
        orders_by_token[token].append(order)
    
    duplicate_orders = []
    for token, token_orders in orders_by_token.items():
        if len(token_orders) > 1:
            # Sort by date, keep first (oldest)
            sorted_orders = sorted(token_orders, key=lambda o: o.date_order)
            duplicate_orders.extend(sorted_orders[1:])  # All except first
    
    return duplicate_orders
```

### 5. Removal Process
**Before:** Removed duplicate order lines, kept one line per product/price combination  
**After:** Removes entire duplicate orders (which cascades to all order lines)

**Important:** This is a destructive operation that permanently deletes orders!

### 6. User Interface Updates

#### Scan Results View
- Shows **total duplicate orders** instead of duplicate lines
- Displays **unique orders count**
- Three tabs:
  1. **Session Summary** - Orders per session with duplicate counts
  2. **Grouped by Access Token** - Shows how many orders share each token
  3. **Duplicate Orders Details** - List of orders to be removed

#### Confirmation View
- Warning message updated to reflect order deletion
- Shows duplicate orders with their details (date, amount, customer)

#### Completion View
- Reports number of orders removed instead of lines removed
- Shows simplified statistics

### 7. Security Model Update
Changed access rights from:
- `model_remove_duplicate_line` 

To:
- `model_remove_duplicate_order`

## Usage Workflow

1. **Open Wizard**
   - Navigate to: Point of Sale → Remove Duplicate Orders
   - Or from POS Session context menu

2. **Select Sessions** (Optional)
   - Choose specific sessions to scan
   - Leave empty to scan all sessions

3. **Scan for Duplicates**
   - Click "Scan for Duplicates" button
   - System groups orders by access_token
   - Identifies which orders are duplicates

4. **Review Results**
   - View duplicate orders organized by session and token
   - See which orders will be kept vs removed
   - Check affected sessions and order counts

5. **Confirm and Remove**
   - Click "Continue to Remove"
   - Review the warning (action cannot be undone!)
   - Click "Remove Duplicates" to permanently delete

6. **Completion**
   - View summary of removed orders
   - Check for any errors
   - Option to scan again

## Important Notes

⚠️ **Warning:** This operation permanently deletes entire orders, not just lines!

- Orders are identified by `access_token` field
- First order (by date) is always kept
- All subsequent orders with the same token are removed
- Orders without `access_token` are ignored
- Deletion cascades to all order lines

## Technical Details

### Files Modified
- `wizard/remove_duplicate_wizard.py` - Main logic and models
- `wizard/remove_duplicate_wizard_views.xml` - UI updated for orders
- `security/ir.model.access.csv` - Updated model access rights
- `views/menu_views.xml` - Updated menu name

### Database Impact
- Transient models only (no persistent data)
- Actual orders are deleted from `pos.order` table
- Related `pos.order.line` records are cascade deleted

### Performance
- Processes all orders from selected sessions in memory
- Groups by access_token for efficient duplicate detection
- Single transaction for all deletions
