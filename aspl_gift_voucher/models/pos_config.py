# -- coding: utf-8 --
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_gift_voucher = fields.Boolean(string='Gift Voucher', readonly=False)
    gift_voucher_account_id = fields.Many2one("account.account", readonly=False, string="Account")
    gift_voucher_payment_method = fields.Many2one("pos.payment.method", readonly=False, string="Payment Method")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
