# Developer Guide - Remove Duplicate Order Lines Module

## Module Structure

```
weha_smart_pos_remove_duplicate/
├── __init__.py                      # Module initialization
├── __manifest__.py                  # Module metadata
├── README.md                        # User documentation
├── models/
│   ├── __init__.py
│   └── pos_order.py                # Extended POS order models
├── wizard/
│   ├── __init__.py
│   ├── remove_duplicate_wizard.py  # Wizard logic
│   └── remove_duplicate_wizard_views.xml  # Wizard UI
├── views/
│   └── pos_order_views.xml         # Enhanced order views
├── security/
│   └── ir.model.access.csv         # Access rights
├── data/
│   └── cron.xml                    # Scheduled actions
└── static/
    └── description/
        └── index.html              # App store description
```

## Core Methods

### pos.order Model

#### `_find_duplicate_lines(order)`
```python
def _find_duplicate_lines(self, order):
    """
    Find duplicate order lines within an order.
    
    Args:
        order: pos.order recordset (single record)
    
    Returns:
        list: IDs of duplicate lines to be removed
    
    Logic:
        - Sorts lines by ID
        - Creates key from (product_id, price_unit, discount, taxes)
        - Keeps first occurrence, marks rest as duplicates
    """
```

#### `action_remove_duplicates()`
```python
def action_remove_duplicates(self):
    """
    Remove duplicate lines from current order.
    
    Returns:
        dict: Client action with notification
    
    Raises:
        UserError: If no access_token or no duplicates found
    """
```

#### `find_orders_with_duplicates(limit=None)`
```python
@api.model
def find_orders_with_duplicates(self, limit=None):
    """
    Find all orders with duplicate lines.
    
    Args:
        limit (int, optional): Max number of orders to return
    
    Returns:
        pos.order: Recordset of orders with duplicates
    """
```

#### `remove_all_duplicates(order_ids=None)`
```python
@api.model
def remove_all_duplicates(self, order_ids=None):
    """
    Batch remove duplicates.
    
    Args:
        order_ids (list, optional): Specific order IDs to process
    
    Returns:
        dict: {
            'orders_processed': int,
            'total_removed': int,
            'errors': list
        }
    """
```

## Duplicate Detection Algorithm

### Key Generation
```python
key = (
    line.product_id.id,           # Product identifier
    line.price_unit,              # Unit price
    line.discount,                # Discount percentage
    tuple(line.tax_ids_after_fiscal_position.ids)  # Applied taxes
)
```

### Logic Flow
1. Order lines sorted by ID (ascending)
2. For each line, generate key
3. If key exists in seen_lines dict:
   - Mark as duplicate
   - Add to removal list
4. Else:
   - Add to seen_lines dict
   - Keep this line

### Example
```python
Order Lines:
  ID: 1, Product: A, Price: 100, Discount: 0  ✓ Keep
  ID: 2, Product: B, Price: 50, Discount: 10  ✓ Keep
  ID: 3, Product: A, Price: 100, Discount: 0  ✗ Remove (duplicate of #1)
  ID: 4, Product: A, Price: 90, Discount: 0   ✓ Keep (different price)
```

## Wizard State Machine

```
draft (initial) 
  ↓ action_scan()
scanned (duplicates found)
  ↓ action_remove()
done (removal complete)
  ↓ action_reset()
draft (back to start)
```

## API Examples

### Example 1: Remove from specific order
```python
order = self.env['pos.order'].browse(123)
result = order.action_remove_duplicates()
```

### Example 2: Find and process all duplicates
```python
# Find orders with duplicates
orders = self.env['pos.order'].find_orders_with_duplicates()

# Process them
result = self.env['pos.order'].remove_all_duplicates(order_ids=orders.ids)
print(f"Removed {result['total_removed']} duplicates from {result['orders_processed']} orders")
```

### Example 3: Filter by access token
```python
# Via wizard
wizard = self.env['remove.duplicate.wizard'].create({
    'access_token': 'abc123xyz',
})
wizard.action_scan_and_remove()
```

### Example 4: Scheduled job (XML-RPC)
```python
import xmlrpc.client

url = "https://your-odoo-instance.com"
db = "your_database"
username = "admin"
password = "admin_password"

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
result = models.execute_kw(
    db, uid, password,
    'pos.order', 'remove_all_duplicates',
    [[]]
)
print(result)
```

## Extending the Module

### Add custom duplicate criteria
```python
class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    def _find_duplicate_lines(self, order):
        # Override to add custom logic
        if not order.lines:
            return []
        
        seen_lines = {}
        duplicates = []
        
        for line in order.lines.sorted(key=lambda l: l.id):
            # Custom key including your fields
            key = (
                line.product_id.id,
                line.price_unit,
                line.discount,
                line.your_custom_field,  # Add custom field
            )
            
            if key in seen_lines:
                duplicates.append(line.id)
            else:
                seen_lines[key] = line.id
        
        return duplicates
```

### Add pre/post removal hooks
```python
class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    def _before_remove_duplicates(self, duplicate_lines):
        """Hook called before removing duplicates"""
        # Custom logic here
        pass
    
    def _after_remove_duplicates(self, removed_count):
        """Hook called after removing duplicates"""
        # Custom logic here
        pass
    
    def action_remove_duplicates(self):
        duplicates = self._find_duplicate_lines(self)
        duplicate_lines = self.env['pos.order.line'].browse(duplicates)
        
        self._before_remove_duplicates(duplicate_lines)
        duplicate_lines.unlink()
        self._after_remove_duplicates(len(duplicates))
        
        return super().action_remove_duplicates()
```

## Testing

### Manual Testing Checklist
- [ ] Create order with duplicate lines
- [ ] Verify duplicate detection (has_duplicates field)
- [ ] Test wizard scan function
- [ ] Test wizard remove function
- [ ] Test direct button on order form
- [ ] Verify order totals recalculated
- [ ] Test with access token filter
- [ ] Test with no duplicates (error handling)
- [ ] Test cron job
- [ ] Check logs for proper entries

### Test Data Setup
```python
# Create test order with duplicates
order = self.env['pos.order'].create({
    'name': 'Test Order',
    'access_token': 'test_token_123',
    'session_id': session.id,
    'partner_id': partner.id,
})

# Add duplicate lines
product = self.env['product.product'].browse(1)
for i in range(3):  # Create 3 identical lines
    self.env['pos.order.line'].create({
        'order_id': order.id,
        'product_id': product.id,
        'price_unit': 100.0,
        'discount': 0,
        'qty': 1,
    })

# Should have 2 duplicates
assert order.duplicate_count == 2
```

## Performance Tips

1. **Use filters**: Don't process all orders at once
2. **Limit results**: Use limit parameter when finding duplicates
3. **Off-peak hours**: Run cron during low traffic
4. **Batch commits**: Module handles commits automatically
5. **Monitor logs**: Check for performance issues

## Troubleshooting

### Common Issues

**Issue**: Duplicates not detected
```python
# Debug: Check duplicate detection logic
order = self.env['pos.order'].browse(ORDER_ID)
duplicates = order._find_duplicate_lines(order)
print(f"Found duplicates: {duplicates}")

# Check line details
for line in order.lines:
    print(f"Line {line.id}: Product={line.product_id.id}, "
          f"Price={line.price_unit}, Discount={line.discount}")
```

**Issue**: Access denied
- Check user has `point_of_sale.group_pos_user` or `group_pos_manager`
- Verify ir.model.access.csv is loaded

**Issue**: Cron not running
```python
# Check cron status
cron = self.env.ref('weha_smart_pos_remove_duplicate.ir_cron_remove_pos_order_duplicates')
print(f"Active: {cron.active}")
print(f"Next call: {cron.nextcall}")
```

## Security Considerations

- Only POS users and managers can access wizard
- Deletion operations logged
- No direct SQL, uses ORM for safety
- Proper transaction management

## Dependencies
- Odoo 16.0
- point_of_sale
- weha_smart_pos (adjust in __manifest__.py if different)

## License
LGPL-3
