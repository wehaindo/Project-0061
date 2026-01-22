# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PosWallet(models.Model):
    _name = 'pos.wallet.transaction'

    partner_id = fields.Many2one('res.partner','Partner')
    
    