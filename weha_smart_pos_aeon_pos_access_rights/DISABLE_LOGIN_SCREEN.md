# Disable Login Screen Feature

## Overview
The `disable_login_screen` feature allows administrators to prevent specific employees (cashiers) from accessing the POS login screen. When this field is enabled for an employee, they will not appear in the employee selection list during login.

## Implementation Details

### Backend (Python)

#### 1. Field Definition (models/hr_employee.py)
```python
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    disable_login_screen = fields.Boolean(
        string='Disable Login Screen',
        default=False,
        help='If checked, this employee will not be able to access the POS login screen'
    )
```

#### 2. Related Field for Public View (models/hr_employee.py)
```python
class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
    
    disable_login_screen = fields.Boolean(
        related='employee_id.disable_login_screen',
        readonly=True
    )
```

#### 3. Field Loading (models/pos_session.py)
The field is loaded into the POS session via `_loader_params_hr_employee`:
```python
def _loader_params_hr_employee(self):
    result = super()._loader_params_hr_employee()
    result['search_params']['fields'].extend([
        'disable_login_screen',
        # ... other fields
    ])
    return result
```

### Frontend (JavaScript)

#### Employee Filtering (static/src/js/Screen/LoginScreen.js)

**In `selectEmployee()` method:**
```javascript
const employees = this.env.pos.employees
    .filter((employee) => employee.id !== this.env.pos.get_cashier().id)
    .filter((employee) => !employee.disable_login_screen) // Exclude disabled employees
    .map((employee) => {
        return {
            id: employee.id,
            item: employee,
            label: employee.name,
            isSelected: false,
            fingerprintPrimary: employee.fingerprint_primary,
        };
    });
```

**In `selectCashier()` method:**
```javascript
const employees = this.env.pos.employees
    .filter((employee) => employee.id !== this.env.pos.get_cashier().id)
    .filter((employee) => !employee.disable_login_screen) // Exclude disabled employees
    .map((employee) => {
        return {
            id: employee.id,
            item: employee,
            label: employee.name,
            isSelected: false,
            fingerprintPrimary: employee.fingerprint_primary,
        };
    });
```

### UI/Form View (views/hr_employee_view.xml)

The field is displayed in the "POS Security" page of the employee form:
```xml
<page string="POS Security" name="pos_security" groups="base.group_erp_manager">
    <group>
        <group string="Login Settings">
            <field name="disable_login_screen"/>
        </group>
        <!-- Other groups... -->
    </group>
</page>
```

## Usage

### For Administrators:
1. Go to **HR > Employees**
2. Open the employee record
3. Navigate to the **POS Security** tab
4. Check the **Disable Login Screen** checkbox
5. Save the record

### Effect:
- When enabled, the employee will **NOT** appear in:
  - The cashier selection popup
  - The employee change popup
  - Any login screen selection list

### Use Cases:
1. **Suspended Employees**: Temporarily prevent access without deleting the employee
2. **Terminated Employees**: Keep records but block POS access
3. **Training Accounts**: Restrict access after training period
4. **Security Compliance**: Quick access revocation for security incidents
5. **Role Changes**: Employees who no longer work as cashiers

## Security Notes

- Only users in the `base.group_erp_manager` group can modify this field
- The field is checked on the frontend, but backend validation should also be considered
- When an employee is already logged in and this field is enabled, they can continue their session
- The setting takes effect on the next login attempt

## Related Features

This feature works in conjunction with:
- **PIN Expiry Management**: Controls PIN validity
- **Fingerprint Authentication**: Biometric access control
- **Access Rights**: Fine-grained permission control

## Testing

To test this feature:
1. Enable `disable_login_screen` for a test employee
2. Open POS and click "Change Cashier" or access the login screen
3. Verify the employee does NOT appear in the selection list
4. Disable the field
5. Refresh the POS session
6. Verify the employee DOES appear in the selection list

## Module Dependencies

- `pos_hr` (Odoo standard)
- `pos_access_right_hr` (base module)
- `weha_smart_pos_aeon_pos_access_rights` (this module)
