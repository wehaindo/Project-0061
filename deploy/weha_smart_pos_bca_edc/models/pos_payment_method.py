import json
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

from odoo.http import request

_logger = logging.getLogger(__name__)

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'


    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('bca_edc', 'Bca EDC')]
        
    