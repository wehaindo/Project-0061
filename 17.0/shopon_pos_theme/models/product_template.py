from odoo import api, fields, models, _


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    setu_alternative_products = fields.Many2many(
        'product.product', string='Alternative Products', domain="[('available_in_pos', '=', True)]")


