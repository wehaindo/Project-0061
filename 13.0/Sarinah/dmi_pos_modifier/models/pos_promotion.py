# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritPosPromotion(models.Model):
    _inherit = 'pos.promotion'

    total_discount_tour = fields.Float('Total Discount For Tourist (%)')
    percent_discount_tour = fields.Float('Total Discount For Tourist (%)')
    promotion_type = fields.Selection(selection_add=[('quantity_price_all', 'Fix Discount on Quantity All'),
                                                     ('buy_x_get_cheapest_free','Buy x, get the cheapest free')])
    product_amt_multi_ids = fields.Many2many('product.product', 'pos_product_amt_multi_rel', string='Products')

    @api.model
    def default_get(self, fields_list):
        res = super(InheritPosPromotion, self).default_get(fields_list)
        res['active'] = True
        return res

    @api.model
    def create(self, vals):
        res = super(InheritPosPromotion, self).create(vals)
        res.active = True
        return res

class InheritPosConditions(models.Model):
    _inherit = 'pos.conditions'

    discount_before_quantity = fields.Float('Discount Before Quantity %')
    apply_keep_before_discount = fields.Boolean(string='Keep Apply Before Discount', default=True)