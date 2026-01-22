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



class ProductProductBarcode(models.Model):
    _name = 'product.product.barcode'
    _description = "Product Barcode"
    _rec_name = "barcode"

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

    def action_sync_product(self):
        _logger.info("action_sync_product")
        for row in self:            
            row.generate_product_json()
            # row.sync_product()

    def _prepare_product_json(self):
        _logger.info("Prepare Product Multiple Barcode JSON")
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))
        
        _logger.info("check error")
        domain = [
            ('product_tmpl_id','=', self.product_id.id)
        ]  
        product_product_id = self.env['product.product'].search(domain, limit=1)       
        products = self.env['pos.session'].with_context({'product_id': product_product_id,'product_category_id': product_product_id.categ_id.id, 'product_sub_category_id': product_product_id.sub_categ_id.id})._load_model('product.product.by.product.id')
        product = products[0]
        if '__last_update' in product:
            del product['__last_update']
        
        #Update New Barcode
        product['_id'] = self.product_couchdb_id
        product['barcode'] = self.barcode
        product['is_secondary_barcode'] = True
        return product

    def generate_product_json(self):
        _logger.info("Generate Product Json")
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))

        product = self._prepare_product_json()
        products_json = json.dumps(product, default=json_serial)
        _logger.info(products_json)  
        self.product_json =  products_json

        # pos_session_obj = self.env['pos.session']         
        # for branch_id in self.branch_ids:
        #     product = self._prepare_product_json(branch_id)
        #     products_json = json.dumps(product, default=json_serial)
            

            # if not product_template_couchdb_id:
            #     vals = {
            #         'branch_id': branch_id.id,
            #         'product_template_id': self.id,
            #         'product_couchdb_sync': False,
            #         'product_json': products_json,
            #         'product_couchdb_id': product_couchdb_id,
            #     }
            #     res = self.env['product.template.couchdb'].create(vals)
            # else:
            #     vals = {
            #         'product_couchdb_sync': False,
            #         'product_json': products_json,
            #         'product_couchdb_id': product_couchdb_id,
            #     }
            #     product_template_couchdb_id.write(vals)
   
    def sync_product(self):        
        auth = HTTPBasicAuth('admin','pelang1')
        headers = {
            'Content-Type': 'application/json'                  
        }                

        if self.product_couchdb_id:
            branch_id = self.branch_id
            _logger.info("Have Product Couchdb ID")
            _logger.info(self.product_couchdb_id)
            try:
                response = requests.get(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_product_barcode}/{self.product_couchdb_id}', auth=auth, headers=headers, verify=False)
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
                    # product_json = self._update_rev(self., couchdb_product['_rev'])
                    response = requests.put(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_product_barcode}/{couchdb_product["_id"]}', auth=auth, headers=headers, data=json_data, verify=False)
                    if response.status_code == 200:
                        pass
                    if response.status_code == 201:                    
                        json_data = response.json()
                        _logger.info(json_data)
                    else:
                        pass
                elif response.status_code == 404:
                    response = requests.post(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_product_barcode}', auth=auth, headers=headers, data=self.product_json, verify=False)        
                    _logger.info(response.status_code)
                    if response.status_code == 200:
                        pass
                    if response.status_code == 201:
                        json_data = response.json()
                        _logger.info(json_data)
            except requests.exceptions.HTTPError as errh:
                _logger.error("Error")
                _logger.error(errh)
        else:
            _logger.info("Have no Product Couchdb ID")      
            try:
                response = requests.post(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_product_barcode}', auth=auth, headers=headers, data=self.product_json, verify=False)    
                if response.status_code == 200:
                    pass
                if response.status_code == 201:
                    json_data = response.json()
                    _logger.info(json_data)
            except requests.exceptions.HTTPError as errh:
                _logger.error("Error")
                _logger.error(errh)
    
    def remove_product_barcode(self):
        auth = HTTPBasicAuth('admin','pelang1')
        headers = {
            'Content-Type': 'application/json'
        }        
        product_barcode_id = self  
        if product_barcode_id.product_couchdb_id:
            branch_id = product_barcode_id.branch_id
            _logger.info("Have Product Couchdb ID")
            _logger.info(product_barcode_id.product_couchdb_id)
            try:
                response = requests.get(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_product_barcode}/{product_barcode_id.product_couchdb_id}', auth=auth, headers=headers, verify=False)
                _logger.info(response.status_code)
                if response.status_code == 200:
                    _logger.info("Product Barcode Found")
                    json_data = response.json()
                    if isinstance(json_data, dict):
                        couchdb_product = json_data
                    if isinstance(json_data, list):
                        couchdb_product = json_data[0]
                    #Update Product
                    _logger.info(couchdb_product)     
                    response = requests.delete(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_product_barcode}/{product_barcode_id.product_couchdb_id}/?rev={couchdb_product["_rev"]}', auth=auth, headers=headers, verify=False)
                    _logger.info(response.status_code)
                    if response.status_code == 200 or response.status_code == 201:
                        # product_barcode_id.unlink()      
                        return True
                else:
                    return False                                                                                           
            except requests.exceptions.HTTPError as errh:
                _logger.error(errh)
                return False

    branch_id = fields.Many2one('res.branch', 'Branch #', required=True)
    product_id_bak = fields.Many2one('product.product', 'Product', ondelete='cascade')
    product_id = fields.Many2one('product.template', 'Product', required=True, ondelete='cascade')
    product_name = fields.Char(related='product_id.name', string="Product Name")
    barcode = fields.Char("Barcode", required=True, ondelete='cascade')
    quantity = fields.Float("Quantity", default=1)
    lst_price = fields.Float('Sales Price')
    
    #CouchDB
    product_couchdb_sync = fields.Boolean('Is Sync', default=False)
    product_json = fields.Text('Product JSON')
    product_couchdb_id = fields.Text('CouchDB Id')
    product_couchdb_rev = fields.Text('CouchDB Rev')

    @api.model
    def create(self, vals):
        vals['product_couchdb_id'] = "product_" + str(uuid.uuid4())        
        res = super(ProductProductBarcode,self).create(vals) 
        res.action_sync_product()
        return res
    
    def write(self, vals):
        res = super(ProductProductBarcode,self).write(vals)
        # super(ProductProductBarcode,self).action_sync_product()
        return res 
    
    def unlink(self):
        for row in self:        
            row.remove_product_barcode()
        # for row in self:
        #     res = row.remove_product_barcode()        
        super(ProductProductBarcode, self).unlink()