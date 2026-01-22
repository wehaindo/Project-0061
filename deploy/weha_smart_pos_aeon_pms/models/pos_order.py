from odoo import models, fields, api, _
from datetime import datetime


import logging
_logger = logging.getLogger(__name__)



class PosOrder(models.Model):
    _inherit = 'pos.order'

    def action_pos_order_paid(self):
        result = super(PosOrder, self).action_pos_order_paid()
        #process /api/device/Trade
        _logger.info('process /api/device/Trade')
        consumption_list = []
        pay_tools = []
        if(self.aeon_member):
            for line in self.lines:
                consumption = {
                    "number": int(line.qty),
                    "price":line.price_unit,
                    "product_id": str(line.product_id.id),
                    "product_name":line.full_product_name,
                    "remarks":"",
                    "total":line.price_subtotal
                }
                consumption_list.append(consumption)
            pay_tools = []
            for payment_id in self.payment_ids:
                pay = {
                    "pay_amount":payment_id.amount,
                    "pay_type":"KWK"
                }
                pay_tools.append(pay)
            
            trade_type = "sale"
            if(self.is_refunded):
                trade_type = "return"
            
            trade_data = {
                "card_no": self.card_no,
                "pos_code":"015",
                "invoice": self.pos_reference,
                "consumption_no": self.pos_reference,
                "stamp": datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                "consumption_amount":self.amount_total,
                "trade_type":trade_type,
                "trade_lineType":1,
                "remarks":"",
                "trade_amount":self.amount_total,
                "consumption_list": consumption_list,
                "pay_tools": pay_tools,
                "merchant_id":"00",
                "ou_id":"01",
                "mb_id":"01002",
                "counter_code":"01002"
            }
            _logger.info("trade_data")
            _logger.info(trade_data)
            # Send /api/device/Trade
            result = self.env['res.partner'].sudo().pms_process_trade(trade_data)
            _logger.info(result)
            

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        order_fields['is_aeon_member'] = ui_order.get('is_aeon_member', False)
        order_fields['aeon_member'] = ui_order.get('aeon_member', False)
        order_fields['aeon_member_day'] = ui_order.get('aeon_member_day', False)
        order_fields['card_no'] = ui_order.get('card_no', False)
        return order_fields
    
    @api.model
    def _payment_fields(self, order, ui_paymentline):
        payment_fields = super(PosOrder, self)._payment_fields(order, ui_paymentline)
        payment_fields['voucher_ids'] = ui_paymentline['voucherlines']
        return payment_fields
        
    def _export_for_ui(self, order):
        result = super(PosOrder, self)._export_for_ui(order)
        result['is_aeon_member'] = order.is_aeon_member
        result['aeon_member'] = order.aeon_member
        result['aeon_member_day'] = order.aeon_member_day
        result['card_no'] = order.card_no
        return result
    
    def add_payment(self, data):
        """Create a new payment for the order"""
        _logger.info("add_payment")
        _logger.info(data)
        super(PosOrder, self).add_payment(data)


    is_aeon_member = fields.Char('Is Aeon Member')
    aeon_member = fields.Char('AEON Member #')
    aeon_member_day = fields.Boolean('AEON Member Day', default=False)
    card_no = fields.Char('Card No')
    is_has_voucher_payment = fields.Boolean('Has voucher payment', default=False)
    
    