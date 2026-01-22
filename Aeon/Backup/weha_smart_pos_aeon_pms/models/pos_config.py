from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_pms_voucher = fields.Boolean(string='PMS Voucher')
    pms_voucher_account_id = fields.Many2one("account.account", string="Account")
    pms_voucher_payment_method = fields.Many2one("pos.payment.method", string="Payment Method")

