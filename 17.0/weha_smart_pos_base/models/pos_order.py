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
    def _process_order(self, order, draft, existing_order):
        order_id = super(PosOrder, self)._process_order(order, draft, existing_order)
        _logger.info(order_id)    
        if order_id:
            pos_order_id = self.browse(order_id)
            if pos_order_id.is_deposit_order:
                _logger.info('Is Deposit Order')
                vals = {
                    'customer_id': pos_order_id.partner_id.id,
                    'type': 'recharge',
                    'order_id': pos_order_id.id,
                    'cashier_id': order['data']['user_id'],
                    'credit': pos_order_id.amount_total,
                }
                _logger.info("create_from_ui")
                res = self.env['pos.deposit'].create_from_ui(vals)
        return order_id
    

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        paymentline = super(PosOrder, self)._payment_fields(order, ui_paymentline)
        paymentline.update({'is_voucher_payment': ui_paymentline['isVoucherPayment']})
        paymentline.update({'voucher_id': ui_paymentline['voucherId']})
        paymentline.update({'voucher_amount': ui_paymentline['voucherAmount']})
        return paymentline
       
    # def _prepare_invoice_lines(self):
    #     result = super()._prepare_invoice_lines()
    #     result['product_uom_id'] = order_line.product_uom.id or order_line.product_uom_id.id
    #     return result

    def _get_pos_anglo_saxon_price_unit2(self, product, partner_id, quantity,product_uom_id):
        moves = self.filtered(lambda o: o.partner_id.id == partner_id)\
            .mapped('picking_ids.move_ids')\
            ._filter_anglo_saxon_moves(product)\
            .sorted(lambda x: x.date)
        price_unit = product.with_company(self.company_id)._compute_average_price(0, quantity, moves)
        if product_uom_id:
            price_unit = product.uom_id.with_company(self.company_id)._compute_price(price_unit, product_uom_id)
        return price_unit
    
    is_deposit_order = fields.Char('Is Deposit Order')

   