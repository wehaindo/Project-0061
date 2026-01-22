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
import simplejson
import requests
from requests.auth import HTTPBasicAuth
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    def action_sync_products(self):
        for product_template_data_id in self.product_template_data_ids:
            product_template_data_id.action_sync_product()

    product_template_data_ids  = fields.One2many('product.template.couchdb', 'product_template_id', 'Product Template Couchdbs')
    
    @api.model
    def create(self, vals):
        res = super().create(vals)        
        res.action_sync_products()        
        return res

    def write(self, vals):
        super().write(vals)
        self.action_sync_products()        
    
    def unlink(self):
        pass
    
class ProductTemplateCouchdb(models.Model):
    _name = 'product.template.couchdb'

    def action_sync_product(self):              
        self.generate_product_json()
        self.sync_product()

    def _prepare_product_json(self, product_template_id, is_variants=False):
        _logger.info("Prepare Product Json")
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))
        
        pos_session_obj = self.env['pos.session']         
        if not is_variants:
            domain = [
                ('product_tmpl_id','=', product_template_id.id)
            ]  
            product_product_id = self.env['product.product'].search(domain, limit=1) 
        else:
            product_product_id = self.product_id
                      
        products = self.env['pos.session'].with_context({'product_id': product_product_id})._load_model('product.product.by.product.id')
        product = products[0]
        if '__last_update' in product:
            del product['__last_update']

        if not self.product_couchdb_id:
            product_couchdb_id = "product_" + str(uuid.uuid4())
            product['_id'] =  product_couchdb_id           
        else:
            product['_id'] =  self.product_couchdb_id
            product_couchdb_id = self.product_couchdb_id
        
        #Update Store Price

        product['lst_price'] = self.list_price
        return product_couchdb_id, product

    def generate_product_json(self):
        _logger.info("Generate Product Json")
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))

        pos_session_obj = self.env['pos.session']
        
        if self.product_id:
            product_couchdb_id, product = self._prepare_product_json(self.product_id, True)
        else:
            product_couchdb_id, product = self._prepare_product_json(self.product_template_id, False)
            
        products_json = json.dumps(product, default=json_serial)

        vals = {
            'product_couchdb_sync': True,
            'product_json': products_json,
            'product_couchdb_id': product_couchdb_id,
        }
        super().write(vals)
    
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
        
    def sync_product(self):
        auth = HTTPBasicAuth('admin','pelang1')
        headers = {
            'Content-Type': 'application/json'                  
        }        
        if self.product_couchdb_id:
            branch_id = self.branch_id
            try:
                response = requests.get(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_product_db}/{self.product_couchdb_id}', auth=auth, headers=headers, verify=False)
                _logger.info(response.status_code)
                if response.status_code == 200:
                    json_data = response.json()
                    if isinstance(json_data, dict):
                        couchdb_product = json_data
                    if isinstance(json_data, list):
                        couchdb_product = json_data[0]
                    #Update Product
                    _logger.info(couchdb_product)                                
                    product_json = self._update_rev(self.product_json, couchdb_product['_rev'])
                    response = requests.put(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_product_db}/{couchdb_product["_id"]}', auth=auth, headers=headers, data=product_json, verify=False)
                    if response.status_code == 200:
                        pass
                    if response.status_code == 201:                    
                        json_data = response.json()
                        _logger.info(json_data)
                    else:
                        pass
                elif response.status_code == 404:
                    response = requests.post(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_product_db}', auth=auth, headers=headers, data=self.product_json, verify=False)        
                    _logger.info(response.status_code)
                    if response.status_code == 200:
                        pass
                    if response.status_code == 201:
                        json_data = response.json()
                        _logger.info(json_data)
            except requests.exceptions.HTTPError as errh:
                _logger.error(errh)
        else:
            _logger.info("Have no Product Couchdb ID")      
            try:
                response = requests.post(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_product_db}', auth=auth, headers=headers, data=self.product_json, verify=False)    
                if response.status_code == 200:
                    pass
                if response.status_code == 201:
                    json_data = response.json()
                    _logger.info(json_data)
            except requests.exceptions.HTTPError as errh:
                _logger.error("Error")
                _logger.error(errh)

    def sync_delete_product(self):
        auth = HTTPBasicAuth('admin','pelang1')
        headers = {
            'Content-Type': 'application/json'                  
        }       
        try:
            response = requests.get(f'{self.branch_id.couchdb_server_url}/{self.branch_id.couchdb_product_db}/{self.product_couchdb_id}', auth=auth, headers=headers, verify=False)
            _logger.info(response.status_code)
            if response.status_code != 200:
                return False            
            
            json_data = response.json()
            if isinstance(json_data, dict):
                couchdb_product = json_data
            if isinstance(json_data, list):
                couchdb_product = json_data[0]
            
            response = requests.delete(f'{self.branch_id.couchdb_server_url}/{self.branch_id.couchdb_product_db}/{self.product_couchdb_id}/?rev={couchdb_product["_rev"]}', auth=auth, headers=headers, verify=False)
            _logger.info(response.status_code)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:            
                return False
        except requests.exceptions.HTTPError as errh:
            _logger.error(errh)
            return False 
        
    product_template_id = fields.Many2one('product.template', 'Product Template #')
    product_id = fields.Many2one('product.product','Variants')
    branch_id = fields.Many2one('res.branch','Store')
    list_price = fields.Float('Branch Price')
    product_couchdb_sync = fields.Boolean('Is Sync', default=False)
    product_json = fields.Text('Product JSON')
    product_couchdb_id = fields.Text('CouchDB Id')
    product_couchdb_rev = fields.Text('CouchDB Rev')
    

    @api.model
    def create(self, vals):
        res = super().create(vals)        
        res.action_sync_product()        
        return res

    def write(self, vals):
        super().write(vals)
        self.action_sync_product()        
    
    def unlink(self):
        res = self.sync_delete_product()
        if res:
            super().unlink()
