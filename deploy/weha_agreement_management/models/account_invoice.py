# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class InheritAccountMove(models.Model):
    _inherit = "account.move"

    settlement_id = fields.Many2one(
        string='settlement',
        comodel_name='settlement.process',
        ondelete='restrict',
    )
    contract_id = fields.Many2one(
        string='contract',
        comodel_name='agreement.contract',
        ondelete='restrict',
    )
    
    
