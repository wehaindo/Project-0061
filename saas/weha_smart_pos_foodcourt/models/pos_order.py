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

    @api.depends('amount_total', 'amount_paid')
    def _compute_amount_due(self):
        for row in self:
            row.amount_due = (row.amount_total - row.amount_paid) + row.change_amount_for_deposit

    customer_email = fields.Char('Customer Email')
    change_amount_for_deposit = fields.Float('Deposit Amount')  # store wallet amount
    amount_due = fields.Float(string='Amount Due', compute='_compute_amount_due')

    def action_pos_order_paid(self):
        self.ensure_one()
        if self.config_id.enable_deposit:
            if not self.config_id.cash_rounding:
                total = self.amount_total
            else:
                total = float_round(0, precision_rounding=self.config_id.rounding_method.rounding,
                                    rounding_method=self.config_id.rounding_method.rounding_method)
            if not float_is_zero(0, precision_rounding=self.currency_id.rounding):
                raise UserError(_("Order %s is not fully paid.", self.name))

            self.write({'state': 'paid'})
        return super(PosOrder, self).action_pos_order_paid()

    @api.model
    def _process_order(self, order, draft, existing_order):
        order_id = super(PosOrder, self)._process_order(order, draft, existing_order)
        if order_id:
            pos_order_id = self.browse(order_id)
            if order['data']['deposit_type']:
                vals = {
                    'customer_id': pos_order_id.partner_id.id,
                    'type': order['data']['deposit_type'],
                    'order_id': pos_order_id.id,
                    'cashier_id': order['data']['user_id'],
                }
                if order['data']['change_amount_for_deposit']:
                    session_id = pos_order_id.session_id
                    cash_register_id = session_id.cash_register_id
                    if not cash_register_id:
                        raise Warning(_('There is no cash register for this PoS Session'))
                    cash_box_out_obj = self.env['cash.box.out'].create(
                        {'name': 'Credit', 'amount': order['data']['change_amount_for_deposit']})
                    cash_box_out_obj.with_context({'partner_id': pos_order_id.partner_id.id})._run(cash_register_id)
                    vals.update({'credit': order['data']['change_amount_for_deposit']})
                    self.env['pos.deposit'].create(vals)
                elif order['data']['used_amount_from_deposit']:
                    vals.update({'debit': order['data']['used_amount_from_deposit']})
                    self.env['pos.deposit'].create(vals)
                else:
                    vals.update({'credit': order['data']['lines'][0][2].get('price_subtotal_incl')})
                    self.env['pos.deposit'].create(vals)
        return order_id

    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update({
            'customer_email': ui_order.get('customer_email') or False,
            'change_amount_for_deposit': ui_order.get('change_amount_for_deposit') or 0.00,
            'amount_due': ui_order.get('amount_due'),
            'amount_paid': ui_order.get('amount_paid'),
        })
        return res
