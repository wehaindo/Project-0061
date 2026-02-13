#!/usr/bin/env python3
# Quick script to delete the cached view
# Run with: python odoo-bin shell -c odoo.conf -d aeondb < delete_view.py

import odoo
from odoo import api, SUPERUSER_ID

with odoo.api.Environment.manage():
    registry = odoo.registry(env.cr.dbname)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Find and delete the problematic view
        view = env['ir.ui.view'].search([
            ('name', '=', 'pos.activity.log.search'),
            ('model', '=', 'pos.activity.log')
        ])
        
        if view:
            print(f"Deleting view: {view.name} (ID: {view.id})")
            view.unlink()
            env.cr.commit()
            print("View deleted successfully! Restart Odoo to recreate from XML.")
        else:
            print("View not found in database")
