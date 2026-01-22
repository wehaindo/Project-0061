from odoo import models, fields, api, _ 


import logging
_logger = logging.getLogger(__name__)

AVAILABLE_PAYMENT_TYPES = [
    ('cash','Cash'),
    ('comm','Comm'),
    ('nocomm','No Comm')
]

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    pos_payment_method_type = fields.Selection(AVAILABLE_PAYMENT_TYPES, default='cash')

