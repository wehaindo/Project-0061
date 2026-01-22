# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_remove_all_item = fields.Boolean(string="Remover todos los items del carrito")
    sh_remove_single_item = fields.Boolean(
        string="Remover un producto del carrito")
