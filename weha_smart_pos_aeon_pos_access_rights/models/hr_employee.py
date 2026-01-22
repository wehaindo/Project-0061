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
import logging
import hashlib

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
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
    
    fingerprint_primary = fields.Text('Fingerprint Primary')
    fingerprint_secondary = fields.Text('Fingerprint Secondary')
    fingerprint_primary_id = fields.Binary('Fingerprint Primary')
    fingerprint_secondary_id = fields.Binary('Fingerprint Secondary')