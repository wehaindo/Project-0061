#!/usr/bin/env python3
"""
Test script to verify disable_login_screen field is properly set and loaded
Run this in Odoo shell:
    odoo-bin shell -c odoo.conf -d aeondb
    
Then paste this code:
"""

# Get all employees and check disable_login_screen field
employees = env['hr.employee'].search([])
print(f"\n{'='*80}")
print(f"Total Employees: {len(employees)}")
print(f"{'='*80}\n")

for emp in employees:
    status = "DISABLED ❌" if emp.disable_login_screen else "ENABLED ✅"
    print(f"ID: {emp.id:4} | Name: {emp.name:30} | Login: {status}")

print(f"\n{'='*80}")
disabled_count = employees.filtered(lambda e: e.disable_login_screen)
print(f"Employees with login DISABLED: {len(disabled_count)}")
print(f"{'='*80}\n")

# Test what POS session would load
session = env['pos.session'].search([('state', '=', 'opened')], limit=1)
if session:
    print(f"\nActive POS Session: {session.name}")
    print(f"Config: {session.config_id.name}")
    
    # Simulate what gets loaded
    all_employees = env['hr.employee'].sudo().search_read(
        [],
        [
            'id', 'name', 'user_id', 'barcode', 'pin', 
            'fingerprint_primary', 'fingerprint_secondary',
            'disable_login_screen',
            'pin_last_change_date',
            'pin_expiry_days',
            'pin_reminder_sent',
            'pin_reminder_days_before'
        ]
    )
    
    print(f"\nEmployees loaded for POS: {len(all_employees)}")
    for emp in all_employees:
        status = "DISABLED ❌" if emp.get('disable_login_screen') else "ENABLED ✅"
        print(f"  - {emp['name']:30} | Login: {status} | disable_login_screen: {emp.get('disable_login_screen')}")
else:
    print("\n⚠️  No opened POS session found!")
