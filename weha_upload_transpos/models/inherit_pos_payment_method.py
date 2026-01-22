from odoo import models, fields, api, exceptions, _


class InheritPosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    code = fields.Char(string='Code', size=8)
    pos_pay_type_code = fields.Char(string='POS Payment Type Code')
    payment_description = fields.Char(string='Payment Description')
    merchant_code = fields.Char(string='Merchant Code')
    description = fields.Char(string='Merchant Description')
    store_id = fields.Many2one('res.branch', string='Store')
    credit_card_number = fields.Char(string='Credit Card Number', size=20)
    approval_code = fields.Char(string='Approval Code', size=6)
    credit_card_terminal_id = fields.Char(string='Credit Card Terminal ID', size=8)
    credit_card_trace_no = fields.Char(string='Credit Card Trace NO', size=10)
    active = fields.Boolean('active')