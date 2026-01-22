from odoo import _, api, fields, models
from datetime import datetime, timedelta, date


class InheritResCompany(models.Model):
    _inherit = 'res.company'

    rebate_product_id = fields.Many2one(
        string='Rebate Product',
        comodel_name='product.product',
    )
    journal_id = fields.Many2one(
        string='Journal',
        comodel_name='account.journal',
        ondelete='restrict',
    )
    account_id = fields.Many2one(
        string='Account',
        comodel_name='account.account',
        ondelete='restrict',
    )