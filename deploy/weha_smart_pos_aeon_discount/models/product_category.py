from odoo import models, fields, api, _ 

class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    is_member_discount = fields.Boolean('Member Discount', default=False)
    member_discount_percentage = fields.Float('Member Discount Percentage', default=0.0)
    is_member_day_discount = fields.Boolean('Member Day Discount', default=False)
    member_day_discount_percentage = fields.Float('Member Day Discount Percentage', default=0.0)
