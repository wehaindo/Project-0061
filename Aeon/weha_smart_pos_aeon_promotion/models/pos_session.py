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
from odoo import models, fields
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result.append('pos.promotion')            
        result.append('pos.conditions')       
        result.append('partial.quantity.fixed.price')     
        result.append('price.combination.products')
        result.append('quantity.fixed.price')
        result.append('get.discount')           
        result.append('quantity.discount')         
        result.append('quantity.discount.amt')
        result.append('fixed.price.multi.products')        
        result.append('free.product.multi.products')
        result.append('discount.multi.products')
        result.append('discount.multi.categories')
        result.append('discount.above.price')
        return result

    def _loader_params_pos_promotion(self):
        res = {
            'search_params': {
                'domain': [('active','=',True)],
                'fields': [],
            },
        }
        return res
    
    def _loader_params_pos_conditions(self):
        res = {
            'search_params': {
                'domain': [('active','=',True)],
                'fields': [],
            },
        }
        return res
    
    def _loader_params_partial_quantity_fixed_price(self):
        res = {
            'search_params': {
                'domain': [('active','=',True)],
                'fields': [],
            },
        }
        return res
    
    def _loader_params_quantity_fixed_price(self):
        res = {
            'search_params': {
                'domain': [('active','=',True)],
                'fields': [],
            },
        }
        return res
    
    def _loader_params_get_discount(self):
        res = {
            'search_params': {
                'domain': [('active','=',True)],
                'fields': [],
            },
        }
        return res        
    
    def _loader_params_quantity_discount(self):
        res = {
            'search_params': {
                'domain': [('active','=',True)],
                'fields': [],
            },
        }
        return res        

    def _loader_params_quantity_discount_amt(self):
        res = {
            'search_params': {
                'domain': [('active','=',True)],    
                'fields': [],
            },
        }
        return res
    
    def _loader_params_fixed_price_multi_products(self):
        res = {
            'search_params': {
                'domain': [('active','=',True)],
                'fields': [],
            },
        }
        return res

    def _loader_params_price_combination_products(self):
        res = {
            'search_params': {
                'domain': [('active','=',True)],
                'fields': [],
            },
        }
        return res          

    def _loader_params_free_product_multi_products(self):
        res = {
            'search_params': {
                'domain': [('active','=',True)],
                'fields': [],
            },
        }
        return res      

    def _loader_params_discount_multi_products(self):
        res = {
            'search_params': {
                'domain': [('active','=',True)],
                'fields': [],
            },
        }
        return res      

    def _loader_params_discount_multi_categories(self):
        res = {
            'search_params': {
                'domain': [('active','=',True)],
                'fields': [],
            },
        }
        return res        

    def _loader_params_discount_above_price(self):
        res = {
            'search_params': {
                'domain': [('active','=',True)],
                'fields': [],
            },
        }
        return res        

    def _get_pos_ui_pos_promotion(self, params):
        return self.env['pos.promotion'].search_read(**params['search_params'])

    def _get_pos_ui_pos_conditions(self, params):
        return self.env['pos.conditions'].search_read(**params['search_params'])

    def _get_pos_ui_partial_quantity_fixed_price(self, params):
        return self.env['partial.quantity.fixed.price'].search_read(**params['search_params'])

    def _get_pos_ui_quantity_fixed_price(self, params):
        return self.env['quantity.fixed.price'].search_read(**params['search_params'])

    def _get_pos_ui_get_discount(self, params):
        return self.env['get.discount'].search_read(**params['search_params'])

    def _get_pos_ui_quantity_discount(self, params):
        return self.env['quantity.discount'].search_read(**params['search_params'])

    def _get_pos_ui_quantity_discount_amt(self, params):
        return self.env['quantity.discount.amt'].search_read(**params['search_params'])

    def _get_pos_ui_fixed_price_multi_products(self, params):
        return self.env['fixed.price.multi.products'].search_read(**params['search_params'])
    
    def _get_pos_ui_price_combination_products(self, params):
        return self.env['price.combination.products'].search_read(**params['search_params'])

    def _get_pos_ui_free_product_multi_products(self, params):
        return self.env['free.product.multi.products'].search_read(**params['search_params'])

    def _get_pos_ui_discount_multi_products(self, params):
        return self.env['discount.multi.products'].search_read(**params['search_params'])
    
    def _get_pos_ui_discount_multi_categories(self, params):
        return self.env['discount.multi.categories'].search_read(**params['search_params'])

    def _get_pos_ui_discount_above_price(self, params):
        return self.env['discount.above.price'].search_read(**params['search_params'])

