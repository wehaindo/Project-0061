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
from odoo.osv.expression import AND, OR
from odoo.service.common import exp_version
# from odoo.addons.weha_smart_pos_data.libs.lzstring import LZString
import simplejson as json
import base64
# from lzstring import LZString
from datetime import datetime, date
import requests
from requests.auth import HTTPBasicAuth
import threading

import logging
_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'
    
    def _get_pos_ui_pos_config(self, params):
        config = super(PosSession, self)._get_pos_ui_pos_config(params)
        res_branch_id = self.env['res.branch'].browse(config['res_branch_id'][0])
        config['couchdb_server_url'] = res_branch_id.couchdb_server_url
        config['couchdb_products'] = res_branch_id.couchdb_name
        config['couchdb_product_categories'] = res_branch_id.couchdb_product_categories
        config['couchdb_product_pricelist_items'] = res_branch_id.couchdb_product_pricelist_items
        config['couchdb_product_barcodes'] = res_branch_id.couchdb_product_barcode
        # config['couchdb_pos_orders'] = res_branch_id.couchdb_pos_order
        return config
    
    def _process_pos_ui_product_product_by_product_id(self, products):
        """
        Modify the list of products to add the categories as well as adapt the lst_price
        :param products: a list of products
        """        
        categories = self._get_pos_ui_product_category(self._loader_params_product_category_by_id())
        _logger.info("1")
        _logger.info(categories)
        sub_categories = self._get_pos_ui_product_sub_category(self._loader_params_product_sub_category_by_id())
        _logger.info("2")
        _logger.info(sub_categories)
        product_category_by_id = {category['id']: category for category in categories}                
        _logger.info("3")
        _logger.info(product_category_by_id)
        product_subcategory_by_id = {sub_category['id']: sub_category for sub_category in sub_categories}
        _logger.info("4")
        _logger.info(product_subcategory_by_id)
        for product in products: 
            _logger.info(product)
            _logger.info(product['categ_id'][0])
            _logger.info(product['sub_categ_id'][0])
            product['categ'] = product_category_by_id[product['categ_id'][0]]  
            old_sub_category_id = self.env['product.sub.category'].browse(product['sub_categ_id'][0])
            if old_sub_category_id:            
                sub_category_id = self.env['product.sub.category'].search([('code','=',old_sub_category_id.code),('active','=',True)], limit=1)
                _logger.info(sub_category_id)
                if sub_category_id:
                    _logger.info("new sub category")
                    sub_category = sub_category_id.read()[0]
                    sub_category_val = {                    
                        "id": sub_category['id'],
                        "code": sub_category['code'],
                        "name": sub_category['name'],
                        "description": sub_category['name'],
                        "is_member_discount": sub_category['is_member_discount'],
                        "member_discount_percentage": sub_category['member_discount_percentage'],
                        "is_member_day_discount": sub_category['is_member_day_discount'],
                        "member_day_discount_percentage": sub_category['member_day_discount_percentage']
                    }
                    product['sub_categ'] = sub_category_val          
                else:
                    # sub_category = self.sub_categ_id.id  
                    _logger.info("old sub category")
                    product['sub_categ'] = product_subcategory_by_id[product['sub_categ_id'][0]]          
            else:
                product['sub_categ'] = {}    

    def _loader_params_product_product(self):
        _logger.info('_loader_params_product_product')
        res = super(PosSession, self)._loader_params_product_product()
        domain =  [
            '&', '&', '&',('sale_ok', '=', True), ('available_in_pos', '=', True), ('branch_ids', 'in', self.config_id.res_branch_id.id),
            '|',('company_id', '=', self.config_id.company_id.id), ('company_id', '=', False)
        ]
        res['search_params']['domain'] = domain
        res['search_params']['fields'].append('sub_categ_id')
        _logger.info(res['search_params']['fields'])
        return res

    def _loader_params_product_product_by_product_id(self):
        _logger.info("_loader_params_product_product_by_product_id")
        result = self._loader_params_product_product()        
        product_id = self.env.context.get('product_id')
        domain = [('id','=', product_id.id)]
        result['search_params']['domain'] = domain           
        return result
    
    def _loader_params_product_category_by_id(self):        
        result = self._loader_params_product_category()
        product_category_id = self.env.context.get('product_category_id')
        domain = [('id','=',product_category_id)]
        _logger.info('Domain')
        _logger.info(domain)
        result['search_params']['domain'] = domain
        return result

    def _loader_params_product_sub_category_by_id(self):
        result = self._loader_params_product_sub_category()
        product_sub_category_id = self.env.context.get('product_sub_category_id')
        domain = [('id','=',product_sub_category_id)]
        _logger.info('Domain Sub Category')
        _logger.info(domain)
        result['search_params']['domain'] = domain
        return result

    def _loader_params_product_sub_category(self):
        return {'search_params': {'domain': [], 'fields': ['code','name','description']}}

    def _get_pos_ui_product_product_by_product_id(self, params):
        self = self.with_context(**params['context'])
        _logger.info("Params")
        _logger.info(params)
        products = self.env['product.product'].search_read(**params['search_params'])
        _logger.info('_get_pos_ui_product_product_by_product_id')
        _logger.info(products)
        self._process_pos_ui_product_product_by_product_id(products)
        _logger.info('_process_pos_ui_product_product_by_product_id')
        return products

    def _get_pos_ui_product_product(self, params): 
        _logger.info("_get_pos_ui_product_product")       
        if self.config_id.use_pos_data_speed_up:
            return []
        else:
            return super(PosSession, self)._get_pos_ui_product_product(params)

    def _get_pos_ui_product_category(self, params):
        return super(PosSession, self)._get_pos_ui_product_category(params)

    def _get_pos_ui_product_sub_category(self, params):
        _logger.info(params)
        sub_categories = self.env['product.sub.category'].search_read(**params['search_params'])        
        return sub_categories

    def _get_pos_ui_product_category_by_id(self, params):        
        # self = self.with_context(**params['context'])
        _logger.info(params['search_params'])
        categories = self.env['product.category'].search_read(**params['search_params'])
        return categories

    def _get_pos_ui_product_pricelist(self, params):
        _logger.info('_get_pos_ui_product_pricelist')
        _logger.info(params)
        if self.config_id.use_pos_data_speed_up:
            _logger.info('use_pos_data_speed_up')
            pricelists = self.env['product.pricelist'].search_read(**params['search_params'])
            _logger.info(pricelists)
            for pricelist in pricelists:
                pricelist['items'] = []
            return pricelists
        else:
            return super(PosSession, self)._get_pos_ui_product_pricelist(params)

    @api.model
    def _pos_ui_models_to_load(self):
        models_to_load = super(PosSession, self)._pos_ui_models_to_load()
        models_to_load.append('product.category')
        models_to_load.append('product.sub.category')
        # if self.config_id.use_pos_data_speed_up:
        #     models_to_load.remove('product.product')      
        return models_to_load

    def sync_test_from_couchdb(self):
        _logger.info("sync_tes_from_couchdb")
        
    def sync_from_couchdb(self):
        _logger.info("sync_from_couchdb")
        self.ensure_one()
        
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))
         
        
        auth = HTTPBasicAuth('admin','pelang1')
        headers = {
            'Content-Type': 'application/json'                  
        }      
        data = {
            'use_index': 'pos-session-id-index',
            'selector':{ 
                "pos_session_id": {'$eq': self.id}
            },
            'limit': 2000            
        }
        _logger.info(data)

        json_data = json.dumps(data, default=json_serial)
        branch_id = self.config_id.res_branch_id
        url = f'{branch_id.couchdb_server_url}p_{branch_id.code}_{self.config_id.code}_pos_orders/_find'
        _logger.info(url)
        response = requests.post(url, auth=auth, headers=headers, data=json_data, verify=False)        
        if response.status_code == 200:
            _logger.info("Order By POS Session Found")
            json_data = response.json()
            # pos_order = json.loads(json_data)
            # _logger.info(json_data)
            if isinstance(json_data, dict):
                couchdb_data = json_data
                #_logger.info(couchdb_data)
                pos_order_list = couchdb_data['docs']
                for pos_order in pos_order_list:
                    _logger.info(pos_order['access_token'])                
                    domain = [('access_token','=',pos_order['access_token'])]
                    pos_order_id = self.env['pos.order'].search(domain, limit=1)
                    if pos_order_id:
                        _logger.info("Order Already Exist")
                    else:
                        _logger.info("Order Already not Exist")                        
                        pos_order.pop("_id")
                        pos_order.pop("_rev")
                        data_to_server = {
                            'id': pos_order['uid'],
                            'data': pos_order
                        }
                        _logger.info(data_to_server)
                        try:
                            self.env['pos.order'].create_from_ui_couchdb([data_to_server])
                            _logger.info("create_order")
                        except Exception as e:
                            _logger.info(e)

            if isinstance(json_data, list):
                couchdb_data = json_data[0]            
                #_logger.info(couchdb_data)
        else:
            _logger.error("Error")
            _logger.info(response.status_code)

    def get_closing_control_data(self):
        _logger.info('get_closing_control_data')
        self.ensure_one()
        self.sync_from_couchdb()
        return super(PosSession, self).get_closing_control_data()    

    pos_data_datetime = fields.Datetime('POS Data Datetime')
    pos_data_zip = fields.Binary('POS Data Zip')
    pos_data_base64 = fields.Text('POs Data (Base64)')


