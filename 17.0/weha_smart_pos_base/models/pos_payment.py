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
from odoo.tools import float_is_zero, float_round



import logging
_logger = logging.getLogger(__name__)

class PosPayment(models.Model):
    _inherit = 'pos.payment'

    #Gift and Voucher
    is_voucher_payment = fields.Boolean('Is Voucher Payment', default=False)
    voucher_id = fields.Many2one('pos.voucher', 'Voucher')
    voucher_amount = fields.Float('Voucher Amount')
    
