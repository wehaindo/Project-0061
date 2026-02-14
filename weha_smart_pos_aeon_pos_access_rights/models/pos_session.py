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
import hashlib
import logging

_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        if self.config_id.use_store_access_rights:
            loaded_data['res.users.supervisor.by.id'] = {supervisor['id']: supervisor for supervisor in loaded_data['res.users.supervisor']}
            loaded_data['res.users.supervisor.by.rfid'] = {supervisor['rfid']: supervisor for supervisor in loaded_data['res.users.supervisor']}
        if self.config_id.module_pos_hr:
            # loaded_data['employee_by_user_id'] = {employee['user_id']: employee for employee in loaded_data['hr.employee']}
            # loaded_data['employee_by_id'] = {employee['id']: employee for employee in loaded_data['hr.employee']}
            # Search all employees directly with sudo to access all fields INCLUDING disable_login_screen
            all_employees = self.env['hr.employee'].sudo().search_read(
                [],
                [
                    'id', 'name', 'user_id', 'barcode', 'pin', 
                    'fingerprint_primary', 'fingerprint_secondary',
                    'disable_login_screen',  # Add this field
                    'pin_last_change_date',
                    'pin_expiry_days',
                    'pin_reminder_sent',
                    'pin_reminder_days_before'
                ]
            )
            # for employee in all_employees:
            #     # Hash barcode and pin for security            
            #     if employee.get('pin'):
            #         employee['pin'] = hashlib.sha1(employee['pin'].encode('utf8')).hexdigest() if employee['pin'] else False
                
            # Create mappings
            
            loaded_data['employee_by_user_id'] = {employee['user_id'][0]: employee for employee in all_employees if employee.get('user_id')}
            loaded_data['employee_by_id'] = {employee['id']: employee for employee in all_employees}
            
            # Log for debugging
            _logger.info("Total employees loaded: %s", len(all_employees))
            _logger.info("Employees with user_id: %s", len(loaded_data['employee_by_user_id']))
            _logger.info("Employees with disable_login_screen: %s", 
                        len([e for e in all_employees if e.get('disable_login_screen')]))

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        
        # new_model = 'res.users.supervisor'
        # if new_model not in result:
        #     result.append(new_model)

        if self.config_id.use_store_access_rights:
            new_model = 'res.users.supervisor'
            if new_model not in result:
                result.append(new_model)

        return result

    def _loader_params_res_users_supervisor(self):
        if len(self.config_id.supervisor_ids) > 0:
            domain = [('id', 'in', self.config_id.supervisor_ids.ids)]
        else: 
            domain = []
        return {'search_params': {'domain': domain, 'fields': ['name', 'id', 'rfid'], 'load': False}}

    def _get_pos_ui_res_users_supervisor(self, params):
        supervisor_ids = self.env['res.users'].search_read(**params['search_params'])
        return supervisor_ids
    
    def _get_pos_ui_hr_employee(self, params):
        """
        Override to add additional fields for fingerprint and PIN expiry management
        """
        employees = self.env['hr.employee'].search_read(**params['search_params'])
        employee_ids = [employee['id'] for employee in employees]
        user_ids = [employee['user_id'] for employee in employees if employee['user_id']]
        manager_ids = self.env['res.users'].browse(user_ids).filtered(lambda user: self.config_id.group_pos_manager_id in user.groups_id).mapped('id')

        employees_barcode_pin = self.env['hr.employee'].browse(employee_ids).get_barcodes_and_pin_hashed()
        bp_per_employee_id = {bp_e['id']: bp_e for bp_e in employees_barcode_pin}
        
        # Get additional fields for each employee
        additional_fields = self.env['hr.employee'].browse(employee_ids).read([
            'disable_login_screen',
            'pin_last_change_date',
            'pin_expiry_days',
            'pin_reminder_sent',
            'pin_reminder_days_before',
            'fingerprint_primary',
            'fingerprint_secondary',
            'fingerprint_primary_id',
            'fingerprint_secondary_id'
        ])
        additional_fields_by_id = {field['id']: field for field in additional_fields}
        
        for employee in employees:
            employee['role'] = 'manager' if employee['user_id'] and employee['user_id'] in manager_ids else 'cashier'
            employee['barcode'] = bp_per_employee_id[employee['id']]['barcode']
            employee['pin'] = bp_per_employee_id[employee['id']]['pin']
            employee['fingerprint_primary'] = bp_per_employee_id[employee['id']]['fingerprint_primary']
            
            # Add additional fields
            emp_additional = additional_fields_by_id.get(employee['id'], {})
            employee['disable_login_screen'] = emp_additional.get('disable_login_screen', False)
            employee['pin_last_change_date'] = emp_additional.get('pin_last_change_date', False)
            employee['pin_expiry_days'] = emp_additional.get('pin_expiry_days', 90)
            employee['pin_reminder_sent'] = emp_additional.get('pin_reminder_sent', False)
            employee['pin_reminder_days_before'] = emp_additional.get('pin_reminder_days_before', 7)
            # Note: fingerprint_primary is already set from get_barcodes_and_pin_hashed()
            employee['fingerprint_secondary'] = emp_additional.get('fingerprint_secondary', False)
            employee['fingerprint_primary_id'] = emp_additional.get('fingerprint_primary_id', False)
            employee['fingerprint_secondary_id'] = emp_additional.get('fingerprint_secondary_id', False)
            
        _logger.info("Loaded %s employees with extended fields", len(employees))
        return employees