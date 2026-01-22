from odoo import models, fields, api, exceptions, _


class InheritProductCategory(models.Model):
    _inherit = 'product.category'

    code = fields.Char(string='Code',)
    active = fields.Boolean('active')