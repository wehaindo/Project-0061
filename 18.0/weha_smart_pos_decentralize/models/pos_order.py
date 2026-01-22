
from odoo import api, fields, models


import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def sync_from_ui(self, orders):
        _logger.info("sync_from_ui called")
        _logger.info(orders)
        res = super().sync_from_ui(orders)
        return res
