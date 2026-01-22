from odoo import models, fields, api


class inheritProductBrand(models.Model):
    _inherit = 'product.brand'

    location_id = fields.Many2one('stock.location', string='Location')
    lantai = fields.Char("Lantai")
    luas = fields.Char("Luas")