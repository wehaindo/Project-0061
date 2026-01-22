# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    member_type = fields.Selection(selection_add=[('tourist', 'Tourist')])