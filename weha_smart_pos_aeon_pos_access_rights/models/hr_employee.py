# -*- coding: utf-8 -*-
#################################################################################
# Author      : WEHA Consultant (<www.weha-id.com>)
# Copyright(c): 2015-Present WEHA Consultant.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging
import hashlib

_logger = logging.getLogger(__name__)

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
    
    fingerprint_primary = fields.Text(
        string='Primary Fingerprint',
        related='employee_id.fingerprint_primary',
        readonly=True
    )
    fingerprint_secondary = fields.Text(
        string='Secondary Fingerprint',
        related='employee_id.fingerprint_secondary',
        readonly=True
    )
    fingerprint_primary_id = fields.Binary(
        string='Primary Fingerprint Binary',
        related='employee_id.fingerprint_primary_id',
        readonly=True
    )
    fingerprint_secondary_id = fields.Binary(
        string='Secondary Fingerprint Binary',
        related='employee_id.fingerprint_secondary_id',
        readonly=True
    )
    disable_login_screen = fields.Boolean(
        string='POS-Disable Login Screen',
        related='employee_id.disable_login_screen',
        readonly=True
    )


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    disable_login_screen = fields.Boolean(
        string='POS-Disable Login Screen',
        help='Prevent this cashier from logging in via the login screen',
        default=False
    )
    
    # PIN Expiration Management Fields
    pin_last_change_date = fields.Date(
        string="PIN Last Change Date",
        help="Date when the PIN was last changed")
    pin_expiry_days = fields.Integer(
        string="PIN Expiry Days",
        help="Number of days after which PIN should be changed (0 = never expires)",
        default=90)
    pin_reminder_sent = fields.Boolean(
        string="PIN Reminder Sent",
        help="Indicates if reminder email has been sent",
        default=False)
    pin_reminder_days_before = fields.Integer(
        string="Reminder Days Before Expiry",
        help="Send reminder email this many days before PIN expires",
        default=7)
    
    def write(self, vals):
        """Track when PIN is changed"""
        if 'pin' in vals and vals.get('pin'):
            vals['pin_last_change_date'] = fields.Date.today()
            vals['pin_reminder_sent'] = False
        return super(HrEmployee, self).write(vals)
    
    @api.model
    def _cron_check_pin_expiry(self):
        """Scheduled action to check PIN expiry and send reminder emails"""
        _logger.info("Starting PIN expiry check cron job")
        
        today = fields.Date.today()
        employees = self.env['hr.employee'].search([
            ('pin', '!=', False),
            ('pin_expiry_days', '>', 0),
            ('pin_last_change_date', '!=', False),
        ])
        
        for employee in employees:
            # Calculate expiry date
            expiry_date = employee.pin_last_change_date + timedelta(days=employee.pin_expiry_days)
            days_until_expiry = (expiry_date - today).days
            
            # Check if reminder should be sent
            if days_until_expiry <= employee.pin_reminder_days_before and not employee.pin_reminder_sent:
                _logger.info(f"Sending PIN reminder to {employee.name}, expires in {days_until_expiry} days")
                employee._send_pin_reminder_email(days_until_expiry, expiry_date)
                employee.pin_reminder_sent = True
            
            # Log expired PINs
            if days_until_expiry < 0:
                _logger.warning(f"PIN expired for {employee.name} since {abs(days_until_expiry)} days ago")
    
    def _send_pin_reminder_email(self, days_until_expiry, expiry_date):
        """Send reminder email to employee about PIN expiry"""
        template = self.env.ref('weha_smart_pos_aeon_pos_access_rights.email_template_pin_reminder', raise_if_not_found=False)
        if template:
            ctx = {
                'employee_name': self.name,
                'days_until_expiry': days_until_expiry,
                'expiry_date': expiry_date.strftime('%d-%m-%Y'),
            }
            template.with_context(ctx).send_mail(self.id, force_send=True)
            _logger.info(f"PIN reminder email sent to {self.name}")
        else:
            _logger.warning("PIN reminder email template not found")
    
    def get_barcodes_and_pin_hashed(self):
        if not self.env.user.has_group('point_of_sale.group_pos_user'):
            return []
        # Apply visibility filters (record rules)
        visible_emp_ids = self.search([('id', 'in', self.ids)])
        employees_data = self.sudo().search_read([('id', 'in', visible_emp_ids.ids)], ['barcode', 'pin', 'fingerprint_primary'])

        for e in employees_data:
            e['barcode'] = hashlib.sha1(e['barcode'].encode('utf8')).hexdigest() if e['barcode'] else False
            e['pin'] = hashlib.sha1(e['pin'].encode('utf8')).hexdigest() if e['pin'] else False
            e['fingerprint_primary'] = e['fingerprint_primary']
        return employees_data
    
    def open_finger_dialog(self):
        return {
            "type": "ir.actions.client",
            "tag": "action_open_finger_dialog",
            "params": {
                "record_id": self.id,  # Pass the current model's ID
            },
        }
    
    # Fingerprint fields
    fingerprint_primary = fields.Text('Fingerprint Primary')
    fingerprint_secondary = fields.Text('Fingerprint Secondary')
    fingerprint_primary_id = fields.Binary('Fingerprint Primary')
    fingerprint_secondary_id = fields.Binary('Fingerprint Secondary')