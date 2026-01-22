# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import requests
import werkzeug

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError, AccessError

_logger = logging.getLogger(__name__)

TIMEOUT = 10

AVAIABLE_TRANS_TYPE = [
    ('01', 'Purchase'),
    # ('02', 'Sale & Cash'),    
    # ('03', 'Refund'),
    # ('04', 'Release Cardver'),
    # ('05', 'Authorization'),            
    # ('07', 'Offline'),    
    # ('08', 'Void'),    
    # ('10', 'Settlement'),
    # ('12', 'Adjustment'),
    # ('13', 'Sale Contactless'),
    # ('17', 'Echo Test'),
    # ('19', 'Print Receipt and EDC sends the details'),
    # ('20', 'Inquiry All Transaction'),
    # ('21', 'Top Up Flazz using Debit Card'),
    # ('22', 'Cash Topup using Cashier Card'),
    # ('23', 'Get Information'),
    # ('24', 'Cash Topup from ECR Flazz using Cashier Card'),
    # ('25', 'Get Card Information'),
    # ('26', 'Payment transaction SAKUKU'),
    # ('27', 'Continue transaction SAKUKU'),
    # ('28', 'Inquiry Transaction SAKUKU'),
    ('31', 'Payment QRIS'),
    # ('32', 'Inquiry QRIS'),
    # ('36', 'Balance Inquiry Flazz (Prepaid ) Card'),
]


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('bcaecr', 'Bca ECR'),('bankmanual','Bank Manual'),('qrismanual','QRIS Manual')]
    
    terminal_id = fields.Char('Terminal #')
    is_dev = fields.Boolean('Is Development', default=False)
    pan = fields.Char('PAN #')
    expirydate = fields.Char('Expiry Date')
    trans_type = fields.Selection(AVAIABLE_TRANS_TYPE,'Transaction Type', require=False)
    

    @api.onchange('use_payment_terminal')
    def _onchange_use_payment_terminal(self):
        super(PosPaymentMethod, self)._onchange_use_payment_terminal()
        if self.use_payment_terminal != 'bcaecr':
            self.terminal_id = False
        if self.use_payment_terminal != 'bankmanual':
            self.terminal_id = False
