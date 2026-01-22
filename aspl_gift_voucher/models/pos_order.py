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
from odoo import models, fields, api, _
import datetime


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _process_order(self, order, draft, existing_order):
        order_id = super(PosOrder, self)._process_order(order, draft, existing_order)
        if order_id:
            if order.get('data').get('redeem'):
                voucher = order.get('data').get('redeem')
                vals = {
                    'voucher_id': voucher[0]['id'],
                    'voucher_code': voucher[0]['voucher_code'],
                    'user_id': order.get('data').get('user_id'),
                    'customer_id': order.get('data').get('partner_id'),
                    'order_name': order.get('data').get('name'),
                    'order_amount': order.get('data').get('amount_total'),
                    'voucher_amount': voucher[0]['voucher_amount'],
                    'used_date': datetime.datetime.now(),
                }
                self.env['aspl.gift.voucher.redeem'].create(vals)
        return order_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
