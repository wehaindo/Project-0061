import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)

class ProductSubCategory(models.Model):
    _name = "product.sub.category"
    _description = 'Product Sub Category'
    _order = 'name'

    def name_get(self):
        result = []            
        for rec in self:
            result.append((rec.id, '(%s) %s' % (rec.code,rec.name)))
        return result

    name = fields.Char(string='Sub Category', required=False)
    code = fields.Integer(string='Code', required=False)
    description = fields.Char(string='Desscription', required=False)
    product_category_id = fields.Many2one('product.category','Product Category')
    product_count = fields.Integer(
        '# Products', compute='_compute_product_count',
        help="The number of products under this sub category ")

    def _compute_product_count(self):
        domain = [
            ('sub_categ_id', '=', self.id)
        ]
        count = self.env['product.template'].search_count(domain)
        self.product_count = count