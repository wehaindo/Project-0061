from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    def name_get(self):
        result = []            
        for rec in self:
            result.append((rec.id, '(%s) %s' % (rec.code,rec.name)))
        return result

    code = fields.Integer(string='Code', required=True)
    description = fields.Char(string='Description', required=True)
    dept_id = fields.Many2one('res.department', 'Department', required=False)
    
