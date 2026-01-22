from odoo import models, fields, api, _ 
from datetime import datetime

# class PosOrderLine(models.Model):
#     _inherit = 'pos.order.line'
    
#     def _process_order(self, order, draft, existing_order):
#         order_id = super(PosOrder, self)._process_order(order, draft, existing_order)
#         if order_id:
#             if order.get('data').get('redeem'):
#                 voucher = order.get('data').get('redeem')
#                 vals = {
#                     'voucher_id': voucher[0]['id'],
#                     'voucher_code': voucher[0]['voucher_code'],
#                     'user_id': order.get('data').get('user_id'),
#                     'customer_id': order.get('data').get('partner_id'),
#                     'order_name': order.get('data').get('name'),
#                     'order_amount': order.get('data').get('amount_total'),
#                     'voucher_amount': voucher[0]['voucher_amount'],
#                     'used_date': datetime.now(),
#                 }
#                 self.env['aspl.gift.voucher.redeem'].create(vals)
#         return order_id


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    def _export_for_ui(self, orderline):
        res = super(PosOrderLine, self)._export_for_ui(orderline)
        res['pos_order_line_discounts'] = []
        return res

    pos_order_line_discounts = fields.One2many('pos.order.line.discount','pos_order_line_id', 'Discount Lines')
    