from odoo import models, fields, api, _

class ResBranch(models.Model):
    _inherit = 'res.branch'

    code = fields.Char('Code', size=10)
    product_pricelist_id = fields.Many2one('product.pricelist','Store Pricelist')
