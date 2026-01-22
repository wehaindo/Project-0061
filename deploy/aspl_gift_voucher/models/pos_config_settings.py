# -*- coding: utf-8 -*-
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


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_enable_gift_voucher = fields.Boolean(related='pos_config_id.enable_gift_voucher', readonly=False,
                                             string='Gift Voucher')
    pos_gift_voucher_account_id = fields.Many2one("account.account", related='pos_config_id.gift_voucher_account_id',
                                                  readonly=False, string="Account")
    pos_gift_voucher_payment_method = fields.Many2one("pos.payment.method",
                                                      related='pos_config_id.gift_voucher_payment_method',
                                                      readonly=False, string="Payment Method")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
