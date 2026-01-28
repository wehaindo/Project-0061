import xmlrpc.client

# Odoo Source connection details
src_url = "https://aeondb.server1601.weha-id.com"
src_db = "aeondb"
src_username = "admin"
src_password = "pelang123"



# Odoo Destination connection details
dest_url = "https://pos.aeonindonesia.co.id"
dest_db = "aeondb"
dest_username = "admin"
dest_password = "pelang123"

# Common endpoint
common = xmlrpc.client.ServerProxy(f"{src_url}/xmlrpc/2/common", allow_none=True)
uid = common.authenticate(src_db, src_username, src_password, {})
dest_uid = common.authenticate(dest_db, dest_username, dest_password, {})

# Object endpoint
models = xmlrpc.client.ServerProxy(f"{src_url}/xmlrpc/2/object", allow_none=True)
dest_models = xmlrpc.client.ServerProxy(f"{dest_url}/xmlrpc/2/object", allow_none=True)


# Check if authentication was successful
if uid:    
    print(f"Authenticated as {src_username} (UID: {uid})")
    print("-" * 80)
    
    # Search for all employees
    search_domain = [[]]  # Empty domain to get all employees
    employee_ids = models.execute_kw(src_db, uid, src_password, 'hr.employee', 'search', search_domain)
    
    print(f"Found {len(employee_ids)} employees")
    print("-" * 80)
    
    # Get employee details
    if employee_ids:
        # Read employee fields
        employee_fields = ['name', 'barcode', 'job_id', 'department_id', 'work_email', 'work_phone', 'fingerprint_primary', 'pin']
        employees = models.execute_kw(src_db, uid, src_password, 'hr.employee', 'read', [employee_ids], {'fields': employee_fields})
        
        # Print employee list
        print(f"{'ID':<10} {'Name':<30} {'Email':<30} {'Status':<15}")
        print("=" * 85)
        
        for employee in employees:
            emp_id = employee.get('id', 'N/A')
            emp_name = employee.get('name', 'N/A')
            #emp_barcode = employee.get('barcode', 'N/A')
            emp_email = employee.get('work_email', 'N/A')
            emp_primary_fingerprint = employee.get('fingerprint_primary', 'N/A')
            emp_pin = employee.get('pin', 'N/A')

            dest_domain = [['name', '=', emp_name]]
            dest_employee_id = dest_models.execute_kw(dest_db, dest_uid, dest_password, 'hr.employee', 'search', [dest_domain], {'limit': 1})
            if dest_employee_id:
                # Update pin and fingerprint_primary on destination employee
                update_vals = {}
                
                if emp_pin and emp_pin != 'N/A':
                    update_vals['pin'] = emp_pin
                
                if emp_primary_fingerprint and emp_primary_fingerprint != 'N/A':
                    update_vals['fingerprint_primary'] = emp_primary_fingerprint
                
                if update_vals:
                    try:
                        dest_models.execute_kw(dest_db, dest_uid, dest_password, 'hr.employee', 'write', [dest_employee_id, update_vals])
                        status = "Updated"
                        if 'pin' in update_vals and 'fingerprint_primary' in update_vals:
                            status = "Updated (PIN + Fingerprint)"
                        elif 'pin' in update_vals:
                            status = "Updated (PIN)"
                        elif 'fingerprint_primary' in update_vals:
                            status = "Updated (Fingerprint)"
                        print(f"{emp_id:<10} {emp_name:<30} {emp_email:<30} {status}")
                    except Exception as e:
                        print(f"{emp_id:<10} {emp_name:<30} {emp_email:<30} Error: {str(e)}")
                else:
                    print(f"{emp_id:<10} {emp_name:<30} {emp_email:<30} No data to update")
            else:
                print(f"{emp_id:<10} {emp_name:<30} {emp_email:<30} Not Found")
        print("-" * 80)
        print(f"Total employees printed: {len(employees)}")
    else:
        print("No employees found.")
else:
    print("Authentication failed.")
