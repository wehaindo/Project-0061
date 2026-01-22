from odoo import models, fields, api, exceptions, _


class InheritProductSubCategory(models.Model):
    _inherit = 'product.sub.category'

    code = fields.Char(string='Code',)
    active = fields.Boolean('active')