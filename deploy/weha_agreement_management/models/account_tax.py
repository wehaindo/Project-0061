# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class InheritAccountTax(models.Model):
    _inherit = "account.tax"

    
    supplier_id = fields.Many2one(
        string='supplier',
        comodel_name='res.partner',
        ondelete='restrict',
    )
    deduction_id = fields.Many2one(
        string='deduction',
        comodel_name='contract.deduction',
        ondelete='restrict',
    )
    