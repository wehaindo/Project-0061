# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_wallet_balance(self):
        self.wallet_balance = 0.0

    wallet_balance = fields.Float('Wallet Balance', compute="get_wallet_balance")