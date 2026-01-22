# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosPayment(models.Model):
    _inherit = "pos.payment"
    _description = "Point of Sale Payments"

    def add_voucher(self, data):
        """Create a new payment for the order"""
        self.ensure_one()
        self.env['pos.payment.voucher'].create(data)

    def get_voucher_count(self):
        for row in self:
            row.voucher_count = len(row.voucher_ids)

    voucher_no = fields.Char('Voucher No')
    voucher_ids = fields.One2many('pos.payment.voucher','pos_payment_id', 'Vouchers')
    voucher_count = fields.Integer('Voucher Count', compute="get_voucher_count")
    
    @api.constrains('payment_method_id')
    def _check_payment_method_id(self):
        for payment in self:
            if payment.payment_method_id not in payment.session_id.config_id.pms_voucher_payment_method:
                if payment.payment_method_id not in payment.session_id.config_id.payment_method_ids:
                    raise ValidationError(
                        _('The payment method selected is not allowed in the config of the POS session.'))
                

class PosPaymentVoucher(models.Model):
    _name = "pos.payment.voucher"

    pos_payment_id = fields.Many2one("pos.payment", "Pos Payment #")
    voucher_full = fields.Char('Voucher Full')
    voucher_no = fields.Char('Voucher No')
    voucher_amount = fields.Char('Voucher Amount')
