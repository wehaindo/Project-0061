# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    agreement_id = fields.Many2one(
        string='Agreement',
        comodel_name='agreement',
        ondelete='restrict',
    )
    
class ProductProduct(models.Model):
    _inherit = "product.product"

    agreement_id = fields.Many2one(
        string='Agreement',
        comodel_name='agreement',
        ondelete='restrict',
    )
    