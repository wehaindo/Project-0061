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
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_round



import logging
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'


    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        order_fields['is_deposit_order'] = ui_order.get('is_deposit_order', False)
        return order_fields
    
    @api.model
    def _process_order(self, order, existing_order):
        order_id = super(PosOrder, self)._process_order(order, existing_order)
        if order_id:
            pos_order_id = self.browse(order_id)
            if pos_order_id.is_deposit_order:
                vals = {
                    'customer_id': pos_order_id.partner_id.id,
                    'type': 'recharge',
                    'order_id': pos_order_id.id,
                    'cashier_id': pos_order_id.user_id.id,
                    'credit': pos_order_id.amount_total
                }
                res = self.env['customer.deposit'].create_from_ui(vals)
        return order_id
    
    is_deposit_order = fields.Char('Is Deposit Order')

   