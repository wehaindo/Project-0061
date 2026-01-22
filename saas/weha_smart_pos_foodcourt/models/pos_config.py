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

class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_deposit = fields.Boolean('Enable Deposit')
    deposit_product = fields.Many2one('product.product', string="Deposit Product")
    receipt_balance = fields.Boolean('Display Balance info in Receipt')
    print_ledger = fields.Boolean('Print Deposit Ledger')
    deposit_account_id = fields.Many2one("account.account", string="Deposit Account")
    deposit_payment_method_id = fields.Many2one("pos.payment.method", "Deposit Payment Method",
                                               domain=[('allow_for_deposit', '=', True)])
