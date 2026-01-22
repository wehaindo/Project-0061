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
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        # POS Acccess Rights
        if self.config_id.use_store_access_rights:
            loaded_data['hr.employee.supervisor.by.id'] = {supervisor['id']: supervisor for supervisor in loaded_data['hr.employee.supervisor']}
            loaded_data['hr.employee.supervisor.by.rfid'] = {supervisor['pin']: supervisor for supervisor in loaded_data['hr.employee.supervisor']}        
        # POS Multi UOM
        loaded_data['multi_uom_id'] = {multi_uom['id']: multi_uom for multi_uom in loaded_data['pos.product.multi.uom']}

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()

        # POS Acccess Rights
        if self.config_id.use_store_access_rights:
            new_model = 'hr.employee.supervisor'
            if new_model not in result:
                result.append(new_model)

        # POS Multiple Barcode
        new_model = 'product.template.barcode'
        if new_model not in result:
            result.append(new_model)

        #Support Channel
        new_model = 'discuss.channel'
        if new_model not in result:
            result.append(new_model)

        #PosPromotion       
        result.append('pos.promotion')            
        result.append('pos.conditions')       
        result.append('partial.quantity.fixed.price')     
        # result.append('price.combination.products')
        result.append('quantity.fixed.price')
        result.append('get.discount')           
        result.append('quantity.discount')         
        result.append('quantity.discount.amt')
        result.append('fixed.price.multi.products')        
        result.append('free.product.multi.products')
        # result.append('discount.multi.products')
        # result.append('discount.multi.categories')
        result.append('discount.above.price')       
        
        new_model = 'pos.product.multi.uom'
        if new_model not in result:
            result.append(new_model)
                     
        return result

    #HR Employee
    def _loader_params_hr_employee_supervisor(self):
        if len(self.config_id.supervisor_ids) > 0:
            domain = [('id', 'in', self.config_id.supervisor_ids.ids)]
        else: 
            domain = []
        return {'search_params': {'domain': domain, 'fields': ['name', 'id', 'pin'], 'load': False}}

    def _get_pos_ui_hr_employee_supervisor(self, params):
        supervisor_ids = self.env['hr.employee'].sudo().search_read(**params['search_params'])
        return supervisor_ids
    
    #Multiple Barcode
    def _loader_params_product_template_barcode(self):
        domain = []
        return {'search_params': {'domain': domain, 'fields': ['product_template_id', 'barcode'], 'load': False}}
    
    def _get_pos_ui_product_template_barcode(self, params):
        barcode_ids = self.env['product.template.barcode'].search_read(**params['search_params'])        
        for barcode_id in barcode_ids:
            domain = [('product_tmpl_id','=', barcode_id['product_template_id'])]
            product_product_id = self.env['product.product'].search(domain, limit=1)
            barcode_id['product_product_id'] = product_product_id.id         
        return barcode_ids


    #Support Channel
    def _loader_params_discuss_channel(self):
        domain = [('is_available_on_pos','=', True)]
        return {'search_params': {'domain': domain, 'fields': ['name'], 'load': False}}
    
    def _get_pos_ui_discuss_channel(self, params):
        discuss_channel_ids = self.env['discuss.channel'].search_read(**params['search_params'])                 
        return discuss_channel_ids
    
    @api.model
    def action_send_message_to_channel(self):
        self.send_message_to_channel(6, "Test Support Message")

    @api.model
    def send_message_to_channel(self, channel_id, message):
        channel_id = self.env['discuss.channel'].browse(channel_id)
        channel_id.message_post(
        body=(message),
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
        )

    def send_message_to_pos_session(self):
        live_data = {'id': 1, 'name': 'Live Data from Backend'}
        # Send the live data to the frontend using the bus service
        channel = self._get_bus_channel_name()
        _logger.info(channel)
        message = {
            "data": live_data,
            "channel": channel
        }
        self.env["bus.bus"]._sendone(channel, "notification", message)

    
    #POS Deposit
    def _loader_params_pos_payment_method(self):
        result = super()._loader_params_pos_payment_method()
        #POS Deposit
        result['search_params']['fields'].append('terminal_id')               
        #POS Voucher
        result['search_params']['fields'].append('is_allow_voucher')               
        return result

    #POS Promotion
    def _loader_params_res_partner(self):
        result = super()._loader_params_res_partner()
        result['search_params']['fields'].append('remaining_deposit_amount')               
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
       
    def _loader_params_fixed_price_combination_products(self):
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

    def _loader_params_free_discount_multi_products(self):
        res = {
            'search_params': {
                'domain': [('active','=',True)],
                'fields': [],
            },
        }
        return res 

    def _loader_params_free_discount_multi_categories(self):
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
    
    # Product Multi UOM
    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend(['has_multi_uom','multi_uom_ids','new_barcode'])
        return result

    def _loader_params_pos_product_multi_uom(self):
        return {'search_params': {'domain': [], 'fields': ['multi_uom_id','price','barcode','uom_name'], 'load': False}}

    def _get_pos_ui_pos_product_multi_uom(self, params):
        result = self.env['pos.product.multi.uom'].search_read(**params['search_params'])
        for res in result:
            uom_id = self.env['uom.uom'].browse(res['multi_uom_id'])
            res['multi_uom_id'] = [uom_id.id,uom_id.name] 
        return result