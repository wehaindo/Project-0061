from odoo import models, fields, api, _ 


class PosOrderLineDiscount(models.Model):
    _name = 'pos.order.line.discount'

    pos_order_line_id = fields.Many2one('pos.order.line', 'Line #')    
    discount_source = fields.Selection([('member_day','Member Day'),('promotion','Promotion'),('manual','Manual')], 'Discount Type') 
    discount_type = fields.Selection([('percentage','Percentage'),('fixed','Fixed')], 'Discount Type')
    discount_percentage = fields.Float('Percentage')
    discount_fixed = fields.Float('Amount')
    discount_str = fields.Char('Description')

    