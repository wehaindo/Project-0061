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

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    allow_for_deposit = fields.Boolean(string="Deposit")

    @api.model
    def create(self, vals):
        res = super(PosPaymentMethod, self).create(vals)
        if vals.get('allow_for_deposit'):
            if vals.get('is_cash_count'):
                raise UserError(_('You can not use cash in case of wallet !!!'))
            if not vals.get('split_transactions'):
                raise UserError(_('Please confirm your debug mode is on & split transaction is checked !!!'))
        return res

    def write(self, vals):
        if vals.get('allow_for_deposit'):
            if 'is_cash_count' in vals:
                if vals.get('is_cash_count'):
                    raise UserError(_('You can not use cash in case of wallet !!!'))
            if 'split_transactions' in vals:
                if not vals.get('split_transactions'):
                    raise UserError(_('Please confirm your debug mode is on & split transaction is checked !!!'))
        return super(PosPaymentMethod, self).write(vals)
