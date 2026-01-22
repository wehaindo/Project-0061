# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

class InheritPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_settlement = fields.Boolean(
        string='is settlement',
        default=False
    )

class InheritPurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    is_settlement = fields.Boolean(
        string='is settlement',
        default=False
    )
    
    