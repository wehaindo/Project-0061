# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
from odoo.exceptions import UserError
import json


_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = "pos.config"

    #Deposit / Wallet Card
    is_wallet_cashier = fields.Boolean('Wallet Cashier', default=False)
    wallet_product_id = fields.Many2one('product.product', string='Wallet Product', domain=[('sale_ok', '=', True)])
    
    loyalty_id = fields.Many2one('pos.loyalty', 'Loyalty',domain=[('state', '=', 'running')])
    