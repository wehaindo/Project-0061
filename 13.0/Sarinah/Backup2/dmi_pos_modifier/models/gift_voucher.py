# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GiftVoucher(models.Model):
    _inherit = 'gift.voucher'

    def reset_voucher_used(self):
        for res in self :
            res.write({
                'redeemed_in': False,
                'remaining_amt': res.used_amt or res.remaining_amt,
                'used_amt': 0,
                'order_ref': False
            })
