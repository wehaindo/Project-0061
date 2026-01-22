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
    
    def _get_pos_ui_product_product(self, params): 
        _logger.info("_get_pos_ui_product_product")       
        if self.config_id.use_pos_data_speed_up:
            _logger.info('use_pos_data_speed_up 1')
            return []
        else:
            _logger.info('not use_pos_data_speed_up 1')
            return super(PosSession, self)._get_pos_ui_product_product(params)

    def _get_pos_ui_pos_config(self, params):
        config = super(PosSession, self)._get_pos_ui_pos_config(params)
        branch_id = self.env['res.branch'].browse(config['branch_id'][0])
        config['couchdb_server_url'] = branch_id.couchdb_server_url
        config['couchdb_products'] = branch_id.couchdb_product_db
        return config

    def _process_pos_ui_product_product_by_product_id(self, products):
        """
        Modify the list of products to add the categories as well as adapt the lst_price
        :param products: a list of products
        """        
        categories = self._get_pos_ui_product_category(self._loader_params_product_category())
        product_category_by_id = {category['id']: category for category in categories}                
        for product in products: 
            product['categ'] = product_category_by_id[product['categ_id'][0]]  

    def _loader_params_product_product_by_product_id(self):
        result = self._loader_params_product_product()        
        product_id = self.env.context.get('product_id')
        domain = [('id','=', product_id.id)]
        result['search_params']['domain'] = domain           
        return result

    def _get_pos_ui_product_product_by_product_id(self, params):
        self = self.with_context(**params['context'])
        products = self.env['product.product'].search_read(**params['search_params'])
        self._process_pos_ui_product_product_by_product_id(products)
        return products
                                
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
            if isinstance(json_data, dict):
                couchdb_data = json_data
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
        else:
            _logger.error("Error")
            _logger.info(response.status_code)

    def get_closing_control_data(self):
        _logger.info('get_closing_control_data')
        # self.ensure_one()
        # self.sync_from_couchdb()
        return super(PosSession, self).get_closing_control_data()    


