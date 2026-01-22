from odoo import models, fields, api
import uuid

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    couch_id = fields.Char('Couch ID', size=100)
    is_avaiable_on_pos = fields.Boolean('Available on Pos', default=False)
    smart_pos_product_category_id = fields.Many2one('smart.pos.product.category', "Pos Product Category")

    @api.model
    def create(self, vals):
        vals['couch_id'] = str(uuid.uuid4())
        return super(ProductTemplate, self).create(vals)

    def write(self, vals):
        if not self.couch_id:
            vals['couch_id'] = str(uuid.uuid4())
        return super(ProductTemplate, self).write(vals)