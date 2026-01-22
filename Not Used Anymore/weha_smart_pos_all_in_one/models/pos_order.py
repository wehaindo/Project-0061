# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _, registry
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import odoo
import logging
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import threading

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    #Loyalty
    plus_point = fields.Float('Plus point', readonly=1)
    redeem_point = fields.Float('Redeem point', readonly=1)

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    #Reward
    reward_id = fields.Many2one('pos.loyalty.reward', 'Reward')
    #Loyalty
    plus_point = fields.Float('Plus point', readonly=1)
    redeem_point = fields.Float('Redeem point', readonly=1)
