# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import requests
import werkzeug

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError, AccessError

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        payment_fields = super(PosOrder, self)._payment_fields(order, ui_paymentline)
        payment_fields.update({'is_prima': ui_paymentline['is_prima']})
        payment_fields.update({'partner_reference_no': ui_paymentline['partner_reference_no']})
        payment_fields.update({'reference_no': ui_paymentline['reference_no']})
        payment_fields.update({'external_id': ui_paymentline['external_id']})
        payment_fields.update({'transaction_date': ui_paymentline['transaction_date']})        
        payment_fields.update({'service_code': ui_paymentline['service_code']})    
        payment_fields.update({'invoice_number': ui_paymentline['invoice_number']})    
        payment_fields.update({'transaction_id': ui_paymentline['transaction_id']})        
        # payment_fields.update({'refund_reference_no': ui_paymentline['refund_reference_no']})        
        payment_fields.update({'refund_time': ui_paymentline['refund_time']})        
        return payment_fields