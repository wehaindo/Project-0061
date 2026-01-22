from odoo import models, fields, api, _
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    refund_user = fields.Many2one('res.users','Refund User')
    void_user = fields.Many2one('res.users','Void User')

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    refund_user = fields.Many2one('res.users','Refund User')