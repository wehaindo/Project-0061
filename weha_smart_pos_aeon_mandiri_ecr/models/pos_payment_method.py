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
import logging
import requests
import werkzeug

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError, AccessError

_logger = logging.getLogger(__name__)

TIMEOUT = 10

AVAIABLE_MANDIRI_TRANS_TYPE = [
    ('3130', 'Sale'),
    ('3C30', 'QRIS'),
]


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('mandiriecr', 'Mandiri ECR')]
    
    mandiri_trans_type = fields.Selection(AVAIABLE_MANDIRI_TRANS_TYPE,'Transaction Type', require=False)