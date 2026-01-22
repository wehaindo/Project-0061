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

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    #POS Deposit
    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('deposit', 'Deposit')]
    
    #POS Deposit
    @api.onchange('use_payment_terminal')
    def _onchange_use_payment_terminal(self):
        super(PosPaymentMethod, self)._onchange_use_payment_terminal()
        if self.use_payment_terminal != 'deposit':
            self.terminal_id = False

    #POS Voucher
    @api.constrains('is_allow_voucher', 'split_transactions', 'journal_id')
    def _check_valid_method(self):
        for record in self:
            if record.is_allow_voucher:
                if not record.split_transactions:
                    raise UserError(_('Please enable Identify Customer !'))
                if record.journal_id:
                    raise UserError(_('You can not select any journal in case of %s !') % record.name)

    #POS Deposit
    terminal_id = fields.Char('Terminal #')

    #POS Voucher
    is_allow_voucher = fields.Boolean("Allow For Voucher",default=False)