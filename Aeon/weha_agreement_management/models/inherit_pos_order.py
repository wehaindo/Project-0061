# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class InheritPosOrderLine(models.Model):
    _inherit = "pos.order.line"

    is_settlement = fields.Boolean(
        string='is settlement',
        default=False,
        index=True
    )
    is_profit = fields.Boolean(
        string='is profit',
        default=False,
        index=True
    )
    