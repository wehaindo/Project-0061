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
import simplejson as json
from datetime import datetime, date
import uuid
import requests
from requests.auth import HTTPBasicAuth
import threading

import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _process_sync_product(self):
        _logger.info("run _process_download")
        # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
        active_id = self.id
        with api.Environment.manage(), self.pool.cursor() as new_cr:            
            self = self.with_env(self.env(cr=new_cr))
            product_template_id = self.env['product.template'].browse(active_id)
            product_template_id.sync_product()

    def action_sync_product(self):
        for row in self:            
            row.generate_product_json()
            row.sync_product()
            # threaded_sync_product = threading.Thread(target=row._process_sync_product, args=())
            # threaded_sync_product.start()
            
    def _update_rev(self, json_str, rev):
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))
        
        product = json.loads(json_str)
        product.update({'_rev': rev})
        products_json = json.dumps(product, default=json_serial)
        return products_json

        return json

    def _prepare_product_json(self, branch_id):
        _logger.info("Prepare Product Json")
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))
        
        pos_session_obj = self.env['pos.session']         
        domain = [
            ('product_tmpl_id','=', self.id)
        ]  
        product_product_id = self.env['product.product'].search(domain, limit=1)       
        products = self.env['pos.session'].with_context({'product_id': product_product_id.id,'product_category_id': self.categ_id.id})._load_model('product.product.by.product.id')
        product = products[0]
        if '__last_update' in product:
            del product['__last_update']
        
        domain  = [
            ('branch_id','=', branch_id.id),
            ('product_template_id','=', self.id)
        ]
        product_template_couchdb_id = self.env['product.template.couchdb'].search(domain,limit=1)
        
        if not product_template_couchdb_id:
            product_couchdb_id = "product_" + str(uuid.uuid4())
            product['_id'] =  product_couchdb_id           
        else:
            product['_id'] =  product_template_couchdb_id.product_couchdb_id
            product_couchdb_id = product_template_couchdb_id.product_couchdb_id
        
        #Update Store Price
        domain  = [
            ('res_branch_id','=', branch_id.id),
            ('product_template_id','=', self.id)
        ]
        product_template_price_id = self.env['product.template.price'].search(domain,limit=1)
        if product_template_price_id:
            product['lst_price'] =  product_template_price_id.list_price

        return product_template_couchdb_id, product_couchdb_id, product
        
    def generate_product_json(self):
        _logger.info("Generate Product Json")
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))

        pos_session_obj = self.env['pos.session']         
        for branch_id in self.branch_ids:
            product_template_couchdb_id, product_couchdb_id, product = self._prepare_product_json(branch_id)
            products_json = json.dumps(product, default=json_serial)
            _logger.info(products_json)            

            if not product_template_couchdb_id:
                vals = {
                    'branch_id': branch_id.id,
                    'product_template_id': self.id,
                    'product_couchdb_sync': False,
                    'product_json': products_json,
                    'product_couchdb_id': product_couchdb_id,
                }
                res = self.env['product.template.couchdb'].create(vals)
            else:
                vals = {
                    'product_couchdb_sync': False,
                    'product_json': products_json,
                    'product_couchdb_id': product_couchdb_id,
                }
                product_template_couchdb_id.write(vals)

    def sync_product(self):
        auth = HTTPBasicAuth('admin','pelang1')
        headers = {
            'Content-Type': 'application/json'
        }

        for product_template_data_id in self.product_template_data_ids:
            if product_template_data_id.product_couchdb_id:
                branch_id = product_template_data_id.branch_id
                _logger.info("Have Product Couchdb ID")
                _logger.info(product_template_data_id.product_couchdb_id)
                try:
                    response = requests.get(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_name}/{product_template_data_id.product_couchdb_id}', auth=auth, headers=headers)
                    _logger.info(response.status_code)
                    if response.status_code == 200:
                        _logger.info("Product Found")
                        json_data = response.json()
                        if isinstance(json_data, dict):
                            couchdb_product = json_data
                        if isinstance(json_data, list):
                            couchdb_product = json_data[0]
                        #Update Product
                        _logger.info(couchdb_product)                                
                        product_json = self._update_rev(product_template_data_id.product_json, couchdb_product['_rev'])
                        response = requests.put(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_name}/{couchdb_product["_id"]}', auth=auth, headers=headers, data=product_json)
                        if response.status_code == 200:
                            pass
                        if response.status_code == 201:                    
                            json_data = response.json()
                            _logger.info(json_data)
                        else:
                            pass
                    elif response.status_code == 404:
                        response = requests.post(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_name}', auth=auth, headers=headers, data=product_template_data_id.product_json)        
                        _logger.info(response.status_code)
                        if response.status_code == 200:
                            pass
                        if response.status_code == 201:
                            json_data = response.json()
                            _logger.info(json_data)
                except requests.exceptions.HTTPError as errh:
                    _logger.info("Error")
            else:
                _logger.info("Have no Product Couchdb ID")      
                try:
                    response = requests.post(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_name}', auth=auth, headers=headers, data=product_template_data_id.product_json)    
                    if response.status_code == 200:
                        pass
                    if response.status_code == 201:
                        json_data = response.json()
                        _logger.info(json_data)
                except requests.exceptions.HTTPError as errh:
                    _logger.info("Error")
                
    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.product_couchdb_sync = False
        res.action_sync_product()
        return res

    def write(self, vals):
        _logger.info("Write Product Product")
        res = super(ProductTemplate, self).write(vals)
        self.action_sync_product()
        return res
    
class ProductTemplateCouchdb(models.Model):
    _inherit = 'product.template.couchdb'
        
    branch_id = fields.Many2one('res.branch','Store')
    
