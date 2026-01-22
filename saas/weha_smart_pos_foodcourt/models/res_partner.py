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
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends('deposit_lines')
    def _calc_remaining(self):
        total = 0.00
        for line in self.deposit_lines:
            total += line.credit - line.debit
        self.remaining_deposit_amount = total

    deposit_lines = fields.One2many('pos.deposit', 'customer_id', string="Deposit", readonly=True)
    remaining_deposit_amount = fields.Float(compute="_calc_remaining", string="Remaining Amount", readonly=True, store=True)
    add_change_deposit = fields.Boolean('Add Change to Deposit')
