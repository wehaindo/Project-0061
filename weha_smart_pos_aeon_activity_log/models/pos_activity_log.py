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


_logger = logging.getLogger(__name__)


class PosActivityLog(models.Model):
    _name = "pos.activity.log"    
    _description = 'POS Activity Log'
    _order = "timestamp desc"
    
    @api.model
    def create_from_ui(self, logs, draft=False):
        log_ids = []
        for log in logs:
            log_id = self.env['pos.activity.log'].create(log)
            log_ids.append(log_id)
                    
        return log_ids

    name = fields.Char('Activity Type', required=True)
    
    timestamp = fields.Datetime('Timestamp', default=fields.Datetime.now)
    details = fields.Text('Details')    
    user_id = fields.Many2one('res.users','User')
    hr_employee_id = fields.Many2one('hr.employee','Employee')    
    pos_config_id = fields.Many2one('pos.config', string="POS Config")
    pos_session_id = fields.Many2one('pos.session', string="POS Session")
    pos_order_reference = fields.Char('POS Reference')
    pos_order_id = fields.Many2one('pos.order', string="POS Order")

