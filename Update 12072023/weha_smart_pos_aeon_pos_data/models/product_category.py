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
import logging
_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    def action_sync(self):
        for row in self:            
            row.generate_json()
            row.sync_couchdb()
            
    def _prepare_json(self):
        _logger.info("Prepare Product Category Json")
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))
        
        product_categories = self.env['pos.session'].with_context({'product_category_id': self.id})._load_model('product.category.by.id')
        product_category = product_categories[0]
        if '__last_update' in product_category:
            del product_category['__last_update']
        
        if self.product_category_couchdb_id:
            product_category['_id'] =  self.product_category_couchdb_id
        else:
            product_category_couchdb_id = "productcategory_" + str(uuid.uuid4())
            product_category['_id'] =  product_category_couchdb_id
        
        return product_category['_id'], product_category 

    def _update_rev(self, json_str, rev):
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))
        
        product_category = json.loads(json_str)
        product_category.update({'_rev': rev})
        product_category_json = json.dumps(product_category, default=json_serial)
        return product_category_json
        
    def generate_json(self):
        _logger.info("Generate Product Json")
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))

        product_category_couchdb_id, product_category = self._prepare_json()
        vals = {
            "product_category_couchdb_id" : product_category_couchdb_id
        }
        super(ProductCategory,self).write(vals)
        # self.product_category_couchdb_id= product_category_couchdb_id

        product_category_json = json.dumps(product_category, default=json_serial)
        vals = {
            "product_category_json": product_category_json
        }
        super(ProductCategory,self).write(vals)

    def sync_couchdb(self):
        auth = HTTPBasicAuth('admin','pelang1')
        headers = {
            'Content-Type': 'application/json'
        }
        try:
            if self.product_category_couchdb_id:
                response = requests.get(f'http://server1601.weha-id.com:5984/product_categories/{self.product_category_couchdb_id}', auth=auth, headers=headers)
                if response.status_code == 200:
                    _logger.info("Product Category Found")
                    json_data = response.json()
                    if isinstance(json_data, dict):
                        couchdb_product_category = json_data
                    if isinstance(json_data, list):
                        couchdb_product_category = json_data[0]
                    _logger.info(couchdb_product_category)
                    # self.product_category_couchdb_rev = couchdb_product_category['_rev']
                    product_category_json = self._update_rev(self.product_category_json, couchdb_product_category['_rev'])
                    response = requests.put(f'http://server1601.weha-id.com:5984/product_categories/{couchdb_product_category["_id"]}', auth=auth, headers=headers, data=product_category_json)
                    if response.status_code == 200 or response.status_code == 201:
                        json_data = response.json()
                        vals = {
                            "product_category_couchdb_rev": json_data['rev']
                        }
                        super(ProductCategory,self).write(vals)
                    else:
                        pass
                elif response.status_code == 404:
                    response = requests.post(f'http://server1601.weha-id.com:5984/product_categories', auth=auth, headers=headers, data=self.product_category_json)        
                    _logger.info(response.status_code)
                    if response.status_code == 200:
                        pass
                    if response.status_code == 201:
                        json_data = response.json()
                        _logger.info(json_data)
                        vals = {
                            "product_category_couchdb_rev": json_data['rev']
                        }
                        super(ProductCategory,self).write(vals)
            else:
                _logger.info("Have no Product Couchdb ID")      
                response = requests.post(f'http://server1601.weha-id.com:5984/product_categories', auth=auth, headers=headers, data=self.product_category_json)        
                _logger.info(response.status_code)
                if response.status_code == 200:
                    pass
                if response.status_code == 201:
                    json_data = response.json()
                    _logger.info(json_data)
                    vals = {
                        "product_category_couchdb_rev": json_data['rev']
                    }
                    super(ProductCategory,self).write(vals)
        except requests.exceptions.HTTPError as errh:
            _logger.info("Error")
               
        
    product_category_couchdb_sync = fields.Boolean('Is Sync', default=False)
    product_category_json = fields.Text('JSON')
    product_category_couchdb_id = fields.Text('CouchDB ID')
    product_category_couchdb_rev = fields.Text('CouchDB Rev')


    @api.model
    def create(self, vals):
        res = super(ProductCategory, self).create(vals)
        res.action_sync()
        return res
    
    def write(self, vals):
        res = super(ProductCategory, self).write(vals)
        self.action_sync()
        return res
    



