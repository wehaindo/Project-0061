import xmlrpc.client
import sys

# Odoo connection details
url = "https://pos.aeonindonesia.co.id"  # Change to your Odoo URL
db = "aeondb"  # Change to your database name
username = "admin"  # Change to your username
password = "pelang123"  # Change to your password

# Get POS Config ID from command line argument
pos_config_id = 31
# Common endpoint
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
uid = common.authenticate(db, username, password, {})

# Object endpoint
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)

# Check if authentication was successful
if uid:
    print(f"Authenticated as {username} (UID: {uid})")
    print("=" * 80)
    
    # Search for "Cashier" job position
    print("\n[1] Searching for Cashier job position...")
    job_ids = models.execute_kw(db, uid, password,
        'hr.job', 'search',
        [['|',['name', 'ilike', 'Cashier'],['name', 'ilike', 'Supervisor']]])
    
    if not job_ids:
        print("❌ No 'Cashier' job position found!")
        print("Please create a job position with 'Cashier' in the name first.")
        exit(1)
    else:
        print(f"✓ Found Cashier job IDs: {job_ids}")
        
        # Get job details
        jobs = models.execute_kw(db, uid, password,
            'hr.job', 'read',
            [job_ids, ['id', 'name']])
        
        for job in jobs:
            print(f"  - ID: {job['id']}, Name: {job['name']}")
    
    print("-" * 80)
    
    # Search for employees with Cashier job
    print("\n[2] Searching for employees with Cashier job...")
    employee_ids = models.execute_kw(db, uid, password,
        'hr.employee', 'search',
        [[['job_id', 'in', job_ids]]])
    
    if not employee_ids:
        print("❌ No employees found with Cashier job!")
        print("Please assign employees to the Cashier job position first.")
        exit(1)
    else:
        # Get employee details
        employees = models.execute_kw(db, uid, password,
            'hr.employee', 'read',
            [employee_ids, ['id', 'name', 'job_id', 'barcode']])
        
        print(f"✓ Found {len(employees)} cashier employee(s):")
        print(f"{'ID':<10} {'Name':<30} {'Job':<25} {'Barcode':<15}")
        print("=" * 80)
        for emp in employees:
            emp_id = emp['id']
            emp_name = emp['name']
            emp_job = emp['job_id'][1] if emp['job_id'] else 'N/A'
            emp_barcode = emp['barcode'] or 'N/A'
            print(f"{emp_id:<10} {emp_name:<30} {emp_job:<25} {emp_barcode:<15}")
    
    print("-" * 80)
    
    # Verify the specified POS config exists
    print(f"\n[3] Verifying POS Config ID: {pos_config_id}...")
    pos_exists = models.execute_kw(db, uid, password,
        'pos.config', 'search',
        [[['id', '=', pos_config_id]]])
    
    if not pos_exists:
        print(f"❌ POS Config with ID {pos_config_id} not found!")
        print("Please check the POS Config ID and try again.")
        exit(1)
    else:
        print(f"✓ POS Config ID {pos_config_id} exists")
    
    print("-" * 80)
    
    # Enable Multiple Employees per Session
    print(f"\n[4] Enabling 'Multiple Employees per Session' for POS Config ID: {pos_config_id}...")
    try:
        models.execute_kw(db, uid, password,
            'pos.config', 'write',
            [[pos_config_id], {
                'module_pos_hr': True
            }])
        print(f"  ✓ Successfully enabled 'Multiple Employees per Session'")
    except Exception as e:
        print(f"  ⚠ Warning: Could not enable 'Multiple Employees per Session'")
        print(f"  Error: {str(e)}")
        print(f"  Continuing with employee update...")
    
    print("-" * 80)
    
    # Update the specified POS config with cashier employees
    print(f"\n[5] Updating POS Config ID: {pos_config_id}...")
    print("=" * 80)
    
    # Get current POS config details
    config = models.execute_kw(db, uid, password,
        'pos.config', 'read',
        [[pos_config_id], ['name', 'employee_ids', 'module_pos_hr']])
    
    if not config:
        print(f"❌ Could not read POS Config ID {pos_config_id}")
        exit(1)
    
    config_data = config[0]
    config_name = config_data['name']
    current_employee_ids = config_data.get('employee_ids', [])
    module_pos_hr = config_data.get('module_pos_hr', False)
    
    print(f"\nPOS Config: {config_name} (ID: {pos_config_id})")
    print(f"  Multiple Employees per Session: {'Enabled ✓' if module_pos_hr else 'Disabled ✗'}")
    print(f"  Current employees: {len(current_employee_ids)}")
    
    print(f"\nPOS Config: {config_name} (ID: {pos_config_id})")
    print(f"  Multiple Employees per Session: {'Enabled ✓' if module_pos_hr else 'Disabled ✗'}")
    print(f"  Current employees: {len(current_employee_ids)}")
    
    # Combine current employees with cashier employees (remove duplicates)
    updated_employee_ids = list(set(current_employee_ids + employee_ids))
    new_employees_count = len(updated_employee_ids) - len(current_employee_ids)
    
    # Update POS config with cashier employees
    # Using (6, 0, [ids]) command to replace the many2many relationship
    try:
        result = models.execute_kw(db, uid, password,
            'pos.config', 'write',
            [[pos_config_id], {
                'employee_ids': [(6, 0, updated_employee_ids)]
            }])
        
        # Write returns True on success, but check if no exception was raised
        print(f"  ✓ Successfully updated!")
        print(f"  Added: {new_employees_count} new cashier(s)")
        print(f"  Total employees now: {len(updated_employee_ids)}")
        print("=" * 80)
        print(f"\n🎉 Update Complete!")
        print(f"  - POS Config: {config_name}")
        print(f"  - Cashiers added: {new_employees_count}")
        print(f"  - Total employees: {len(updated_employee_ids)}")
        print(f"  - Cashier employees processed: {len(employee_ids)}")
    except Exception as e:
        print(f"  ❌ Failed to update POS config")
        print(f"  Error: {str(e)}")
        exit(1)
    
else:
    print("❌ Authentication failed!")
    print("Please check your connection details (url, db, username, password)")
