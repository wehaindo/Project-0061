from odoo import models, fields, api, _ 



class ProductProduct(models.Model):
    _inherit = 'product.product'

    member_price = fields.Float('Member Price')
