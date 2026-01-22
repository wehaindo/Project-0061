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
        payment_fields.update({'bca_ecr_data': ui_paymentline['bca_ecr_data']})
        payment_fields.update({'pan': ui_paymentline['pan']})
        payment_fields.update({'approval_code': ui_paymentline['approval_code']})
        payment_fields.update({'merchant_id': ui_paymentline['merchant_id']})
        payment_fields.update({'terminal_id': ui_paymentline['terminal_id']})
        payment_fields.update({'card_holder_name': ui_paymentline['card_holder_name']})
        return payment_fields