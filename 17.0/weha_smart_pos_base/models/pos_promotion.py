# -*- coding: utf-8 -*-
#################################################################################
# Author      : WEHA Consultant (<www.weha-id.com>)
# Copyright(c): 2015-Present WEHA Consultant.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


import logging
_logger = logging.getLogger(__name__)


class PosPromotion(models.Model):
    _name = 'pos.promotion'
    _order = "sequence"
    _rec_name = 'promotion_code'
    _description = 'Pos Promotion'

    AVAILABLE_TIMES = [
        ('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
        ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'),
        ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'),
        ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'), ('22', '22'), ('23', '23')
    ]

    promotion_code = fields.Char('Promotion Code', required=True)
    promotion_description = fields.Char('Description')
    promotion_type = fields.Selection([('buy_x_quantity_get_special_price', 'Buy X Quantity Get Special Price (AEON)'),                                       
                                       ('buy_x_get_y', 'Buy X Get Y Free'),
                                       ('buy_x_partial_quantity_get_special_price', 'Buy X Partial Quantity Get Special Price (AEON)'),
                                       ('buy_x_get_dis_y', 'Buy X Get Discount On Y'),
                                       ('discount_total', 'Discount (%) on Total Amount'),
                                       ('quantity_discount', 'Percent Discount on Quantity'),
                                       ('quantity_price', 'Fix Discount on Quantity'),
                                       ('fixed_price_on_multi_product', 'Fixed Price On Combination Products (AEON)'),
                                       ('free_product_on_multi_product', 'Free Product On Combination Products (AEON)'),
                                       ('combination_product_fixed_price', 'Combination Product Fixed Price (AEON)'),
                                       ('discount_on_multi_product', 'Discount On Combination Products'),
                                       ('discount_on_multi_category', 'Discount On Multiple Categories')],
                                      default="buy_x_get_y", required=True)
    is_member = fields.Boolean('Need Member', default=False)
    from_date = fields.Date('From', required=True)
    to_date = fields.Date('To', required=True)
    from_time = fields.Selection(AVAILABLE_TIMES, string="From Time")
    to_time = fields.Selection(AVAILABLE_TIMES, string="To Time")
    day_of_week_ids = fields.Many2many('day.week', string="Day Of The Week", required=True)
    
    pos_condition_ids = fields.One2many('pos.conditions', 'pos_promotion_rel')
    pos_partial_quantity_fixed_price_ids  = fields.One2many('partial.quantity.fixed.price', 'pos_promotion_id')
    pos_quantity_ids = fields.One2many('quantity.discount', 'pos_quantity_rel')
    pos_quantity_fixed_price_ids = fields.One2many('quantity.fixed.price', 'pos_promotion_id')
    pos_quantity_amt_ids = fields.One2many('quantity.discount.amt', 'pos_quantity_amt_rel')
    pos_quantity_dis_ids = fields.One2many('get.discount', 'pos_quantity_dis_rel')
    product_id_qty = fields.Many2one('product.product', 'Product')
    product_id_amt = fields.Many2one('product.product', 'Select Product')
    product_id_x_y = fields.Many2one('product.product', 'Choose Product')
    multi_products_fixed_price_ids = fields.One2many('fixed.price.multi.products', 'promotion_id')
    multi_products_free_product_ids = fields.One2many('free.product.multi.products', 'promotion_id')
    combination_product_fixed_price_ids = fields.One2many('price.combination.products', 'promotion_id')
    multi_products_discount_ids = fields.One2many('discount.multi.products', 'multi_product_dis_rel')
    multi_category_discount_ids = fields.One2many('discount.multi.categories', 'multi_category_dis_rel')
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of promotions.")
    
    # Invoice Promotion
    total_amount = fields.Float('Total Invoice Amount')
    operator = fields.Selection([('is_eql_to', 'Is Equal To'),('greater_than_or_eql', 'Greater Than Or Equal')])
    total_discount = fields.Float('Total Discount(%)')
    
    # discount_product = fields.Many2one("product.product", "Discount Product", default=lambda self: self.env.ref('aspl_pos_promotion.disc_product').id)
    discount_product = fields.Many2one("product.product", "Discount Product")
    active = fields.Boolean("Active", default=True)
    parent_product_ids = fields.Many2many(comodel_name='product.product', string="Products")
    discount_price_ids = fields.One2many('discount.above.price', 'pos_promotion_id')
    
    @api.model
    def default_get(self, fields_list):
        res = super(PosPromotion, self).default_get(fields_list)
        days = self.env['day.week'].search([])
        list_day = []
        for rec in days:
            list_day.append(rec.id)
        res['day_of_week_ids'] = [(6, 0, list_day)]
        return res

    @api.constrains('from_date', 'to_date')
    def date_check(self):
        if self.from_date > self.to_date:
            raise ValidationError("To Date must be greater than From date")

    @api.constrains('from_time', 'to_time')
    def time_check(self):
        if self.from_time and not self.to_time:
            raise ValidationError("You have to set 'To' Time.")
        if not self.from_time and self.to_time:
            raise ValidationError("You have to set 'From' Time.")
        if self.from_time and self.to_time and int(self.from_time) > int(self.to_time):
            raise ValidationError("To Time must be greater than From Time")

    @api.model
    def check_promotion(self):
        pass 

class PosCondition(models.Model):
    _name = 'pos.conditions'
    _description = 'Pos Promotion Conditions'

    def compute_active(self):
        for row in self:
            row.active = row.pos_promotion_rel.active

    pos_promotion_rel = fields.Many2one('pos.promotion', ondelete='cascade')
    product_x_id = fields.Many2one('product.product', 'Product(X)')
    operator = fields.Selection([('greater_than_or_eql', 'Greater Than Or Equal')])
    quantity = fields.Float('Quantity(X)')
    product_y_id = fields.Many2one('product.product', 'Product(Y)')
    quantity_y = fields.Float('Quantity(Y)')
    active = fields.Boolean("Active", compute="compute_active", store=True)

# AEON
class PartialQuantityFixedPrice(models.Model):
    _name = 'partial.quantity.fixed.price'
    _description = 'Partial Quantity Fixed Price'

    def compute_active(self):
        for row in self:
            row.active = row.pos_promotion_id.active

    pos_promotion_id = fields.Many2one('pos.promotion', ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Product')
    product_ids = fields.Many2many(comodel_name='product.product', string="Products")
    operator = fields.Selection([('greater_than_or_eql', 'Greater Than Or Equal')])
    quantity = fields.Integer('Quantity/Multiply')
    quantity_amt = fields.Integer('Max Quantity', default=0)
    fixed_price = fields.Float('Fixed Price')
    active = fields.Boolean("Active")

class QuantityDiscount(models.Model):
    _name = 'quantity.discount'
    _description = 'Quantity Discount'

    def compute_active(self):
        for row in self:
            self.active = self.pos_quantity_rel.active

    pos_quantity_rel = fields.Many2one('pos.promotion', ondelete='cascade')
    quantity_dis = fields.Integer('Quantity')
    discount_dis = fields.Float('Discount(%)')
    active = fields.Boolean("Active")

class QuantityDiscountAmount(models.Model):
    _name = 'quantity.discount.amt'
    _description = "Quantity Discount Amount"

    def compute_active(self):
        for row in self:
            self.active = self.pos_quantity_amt_rel.active

    pos_quantity_amt_rel = fields.Many2one('pos.promotion', ondelete='cascade')
    quantity_amt = fields.Integer('Quantity')
    discount_price = fields.Float('Discount Price (Fixed)')
    active = fields.Boolean("Active")

# AEON 
class QuantityFixedPrice(models.Model):
    _name = 'quantity.fixed.price'
    _description = "Quantity Fixed Price"

    def compute_active(self):
        for row in self:
            row.active = row.pos_promotion_id.active

    pos_promotion_id = fields.Many2one('pos.promotion', ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Product')
    # operator = fields.Selection([
    #         ('greater_than_or_eql', 'Greater Than Or Equal'),
    #         ('lower_than_or_eql', 'Lower Than or Equal')
    #     ]
    # )
    quantity_amt = fields.Integer('Quantity')
    fixed_price = fields.Float('Price (Fixed)')
    active = fields.Boolean("Active")

class GetProductDiscount(models.Model):
    _name = 'get.discount'
    _description = "Get Discount"

    def compute_active(self):
        for row in self:
            self.active = self.pos_quantity_dis_rel.active

    pos_quantity_dis_rel = fields.Many2one('pos.promotion', ondelete='cascade')
    product_id_dis = fields.Many2one('product.product', 'Product')
    qty = fields.Float("Quantity")
    discount_dis_x = fields.Float('Discount (%)')
    active = fields.Boolean("Active")

# AEON
class GetProductFixedPrice(models.Model):
    _name = 'get.fixed.price'
    _description = "Get Fixed Price"

    def compute_active(self):
        for row in self:
            row.active = row.promotion_id.active

    promotion_id = fields.Many2one('pos.promotion', ondelete='cascade')
    product_id_dis = fields.Many2one('product.product', 'Product')
    qty = fields.Float("Quantity")
    discount_dis_x = fields.Float('Discount (%)')
    active = fields.Boolean("Active")

# AEON
class FixedPriceOnMultipleProducts(models.Model):
    _name = 'fixed.price.multi.products'
    _description = "Apply Fixed Price on Multiple Products"

    def compute_active(self):
        for row in self:
            row.active = row.promotion_id.active

    promotion_id = fields.Many2one('pos.promotion', ondelete='cascade')
    product_ids = fields.Many2many(comodel_name='product.product', string="Products")
    fixed_price = fields.Float("Fixed Price")
    margin = fields.Float('Margin in %', default=0.0)
    active = fields.Boolean("Active")

# AEON
class FreeProductOnMultipleProducts(models.Model):
    _name = 'free.product.multi.products'
    _description = "Apply Free Product on Multiple Products"

    def compute_active(self):
        for row in self:
            row.active = row.promotion_id.active

    promotion_id = fields.Many2one('pos.promotion', ondelete='cascade')
    product_ids = fields.Many2many(comodel_name='product.product', string="Products")
    product_id = fields.Many2one("product.product", "Free Product")
    quantity_amt = fields.Integer('Quantity')    
    active = fields.Boolean("Active")

# AEON 
class PriceOnCombinationProducts(models.Model):
    _name = 'price.combination.products'
    _description = "Apply Price on Combination Products"

    def compute_active(self):
        for row in self:
            row.active = row.promotion_id.active

    promotion_id = fields.Many2one('pos.promotion', ondelete='cascade')
    product_id = fields.Many2one("product.product", "Product")
    quantity_amt = fields.Integer('Quantity')
    fixed_price = fields.Float('Price (Fixed)')
    active = fields.Boolean("Active")
    
class DiscountOnMultipleProducts(models.Model):
    _name = 'discount.multi.products'
    _description = "Apply Discount on Multiple Products"

    def compute_active(self):
        for row in self:
            self.active = self.multi_product_dis_rel.active

    multi_product_dis_rel = fields.Many2one('pos.promotion', ondelete='cascade')
    products_discount = fields.Float("Discount")
    product_ids = fields.Many2many(comodel_name='product.product', string="Products")
    margin = fields.Float('Margin in %', default=0.0)
    active = fields.Boolean("Active")

class DiscountOnMultipleCategories(models.Model):
    _name = 'discount.multi.categories'
    _description = "Apply Discount on Multiple Categories"

    def compute_active(self):
        for row in self:
            self.active = self.multi_category_dis_rel.active

    multi_category_dis_rel = fields.Many2one('pos.promotion', ondelete='cascade')
    category_discount = fields.Float("Discount")
    category_ids = fields.Many2many(comodel_name='pos.category', string="Categories")
    margin = fields.Float('Margin in %', default=0.0)
    active = fields.Boolean("Active")

class DiscountOnAbovePrice(models.Model):
    _name = 'discount.above.price'
    _description = "Apply Discount, if price is above define price"

    def compute_active(self):
        for row in self:
            self.active = self.pos_promotion_id.active

    pos_promotion_id = fields.Many2one('pos.promotion', ondelete='cascade')
    discount = fields.Float("Discount (%)")
    price = fields.Float("Price")
    discount_type = fields.Selection([('percentage', 'Percentage'),
                                      ('fix_price', 'Fix Price'),
                                      ('free_product', 'Free Product')])
    fix_price_discount = fields.Char("Price Discount")
    product_category_ids = fields.Many2many('pos.category', 'discount_pos_categ_rel', string="Categories")
    product_brand_ids = fields.Many2many('product.brand', 'product_brand_rel', string="Product Brands")
    free_product = fields.Many2one('product.product', string="Product")
    active = fields.Boolean("Active")

class DayWeek(models.Model):
    _name = 'day.week'
    _description = "Promotion Week Days"

    name = fields.Char(string="Name")
