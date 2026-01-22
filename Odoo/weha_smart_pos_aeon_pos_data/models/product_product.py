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
        active_id = self.id
        with api.Environment.manage(), self.pool.cursor() as new_cr:            
            self = self.with_env(self.env(cr=new_cr))
            product_template_id = self.env['product.template'].browse(active_id)
            product_template_id.sync_product()

    def action_sync_product(self):
        _logger.info("action_sync_product")
        for row in self:            
            row.generate_product_json()
            row.sync_product()

    def action_sync_product_by_branch(self, branch_id):
        self.ensure_one()
        self.generate_product_json_by_branch(branch_id)
        self.sync_product_by_branch(branch_id)
            
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
        products = self.env['pos.session'].with_context({'product_id': product_product_id,'product_category_id': self.categ_id.id,'product_sub_category_id': self.sub_categ_id.id})._load_model('product.product.by.product.id')
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
        # domain = [
        #     ('res_branch_id','=', branch_id.id),
        #     ('product_template_id','=', self.id)
        # ]
        # product_template_price_id = self.env['product.template.price'].search(domain,limit=1)
        # if product_template_price_id:
        #     product['lst_price'] =  product_template_price_id.list_price
        # else:
        #     product['lst_price'] =  0

        return product_template_couchdb_id, product_couchdb_id, product
        
    def _prepare_product_json_by_branch(self, branch):
        _logger.info("Prepare Product Json by branch")
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
        products = self.env['pos.session'].with_context({'product_id': product_product_id.id,'product_category_id': self.categ_id.id, 'product_sub_category_id': self.sub_categ_id.id})._load_model('product.product.by.product.id')
        product = products[0]
        if '__last_update' in product:
            del product['__last_update']
        
        domain  = [
            ('branch_id','=', branch.id),
            ('product_template_id','=', self.id)
        ]
        product_template_couchdb_id = self.env['product.template.couchdb'].search(domain,limit=1)
        
        if not product_template_couchdb_id:
            product_couchdb_id = "product_" + str(uuid.uuid4())
            product['_id'] =  product_couchdb_id           
        else:
            product['_id'] =  product_template_couchdb_id.product_couchdb_id
            product_couchdb_id = product_template_couchdb_id.product_couchdb_id
        
        # #Update Store Price
        # domain  = [
        #     ('res_branch_id','=', branch.id),
        #     ('product_template_id','=', self.id)
        # ]
        # product_template_price_id = self.env['product.template.price'].search(domain,limit=1)
        # if product_template_price_id:
        #     product['lst_price'] =  product_template_price_id.list_price
    

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
   
    def generate_product_json_by_branch(self, branch):
        _logger.info("Generate Product Json by branch")
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))

        pos_session_obj = self.env['pos.session']        
        branch_id = self.env['res.branch'].browse(branch)
        if branch_id:
            product_template_couchdb_id, product_couchdb_id, product = self._prepare_product_json_by_branch(branch_id)
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
        
        # if len(branch_ids) > 0:            
        #     domain = [('branch_id', 'in', branch_ids)]
        #     product_template_data_ids = self.env['product.template.couchdb'].search(domain)
        # else:
        #     product_template_data_ids = self.product_template_data_ids

        for product_template_data_id in self.product_template_data_ids:
            if product_template_data_id.product_couchdb_id:
                branch_id = product_template_data_id.branch_id
                _logger.info("Have Product Couchdb ID")
                _logger.info(product_template_data_id.product_couchdb_id)
                try:
                    response = requests.get(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_name}/{product_template_data_id.product_couchdb_id}', auth=auth, headers=headers, verify=False)
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
                        response = requests.put(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_name}/{couchdb_product["_id"]}', auth=auth, headers=headers, data=product_json, verify=False)
                        if response.status_code == 200:
                            pass
                        if response.status_code == 201:                    
                            json_data = response.json()
                            _logger.info(json_data)
                        else:
                            pass
                    elif response.status_code == 404:
                        _logger.info("Product CouchDB Not Found then create new one")
                        response = requests.post(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_name}', auth=auth, headers=headers, data=product_template_data_id.product_json, verify=False)        
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
                    response = requests.post(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_name}', auth=auth, headers=headers, data=product_template_data_id.product_json, verify=False)    
                    if response.status_code == 200:
                        pass
                    if response.status_code == 201:
                        json_data = response.json()
                        _logger.info(json_data)
                except requests.exceptions.HTTPError as errh:
                    _logger.error("Error")
                    _logger.error(errh)

    def sync_product_by_branch(self, branch): 
        _logger.info('sync_product_by_branch')       
        auth = HTTPBasicAuth('admin','pelang1')
        headers = {
            'Content-Type': 'application/json'                  
        }                
        
        # if len(branch_ids) > 0:            
        #     domain = [('branch_id', 'in', branch_ids)]
        #     product_template_data_ids = self.env['product.template.couchdb'].search(domain)
        # else:
        #     product_template_data_ids = self.product_template_data_ids

        domain = [('branch_id', '=', branch),('product_template_id','=',self.id)]
        product_template_data_id = self.env['product.template.couchdb'].search(domain, limit=1)        
        if product_template_data_id.product_couchdb_id:
            branch_id = product_template_data_id.branch_id
            _logger.info("Have Product Couchdb ID")
            _logger.info(product_template_data_id.product_couchdb_id)
            try:
                response = requests.get(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_name}/{product_template_data_id.product_couchdb_id}', auth=auth, headers=headers, verify=False)
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
                    response = requests.put(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_name}/{couchdb_product["_id"]}', auth=auth, headers=headers, data=product_json, verify=False)
                    if response.status_code == 200:
                        pass
                    if response.status_code == 201:                    
                        json_data = response.json()
                        _logger.info(json_data)
                    else:
                        pass
                elif response.status_code == 404:
                    _logger.info("Product CouchDB Not Found then create new one")
                    response = requests.post(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_name}', auth=auth, headers=headers, data=product_template_data_id.product_json, verify=False)        
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
                response = requests.post(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_name}', auth=auth, headers=headers, data=product_template_data_id.product_json, verify=False)    
                if response.status_code == 200:
                    pass
                if response.status_code == 201:
                    json_data = response.json()
                    _logger.info(json_data)
            except requests.exceptions.HTTPError as errh:
                _logger.error("Error")
                _logger.error(errh)

    def remove_product(self, branch):
        auth = HTTPBasicAuth('admin','pelang1')
        headers = {
            'Content-Type': 'application/json'
        }
        domain = [('branch_id', '=', branch),('product_template_id','=',self.id)]
        product_template_data_id = self.env['product.template.couchdb'].search(domain, limit=1)        
        if product_template_data_id.product_couchdb_id:
            branch_id = product_template_data_id.branch_id
            _logger.info("Have Product Couchdb ID")
            _logger.info(product_template_data_id.product_couchdb_id)
            try:
                response = requests.get(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_name}/{product_template_data_id.product_couchdb_id}', auth=auth, headers=headers, verify=False)
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
                    response = requests.delete(f'{branch_id.couchdb_server_url}/{branch_id.couchdb_name}/{product_template_data_id.product_couchdb_id}/?rev={couchdb_product["_rev"]}', auth=auth, headers=headers, verify=False)
                    _logger.info(response.status_code)
                    if response.status_code == 200 or response.status_code == 201:
                        product_template_data_id.unlink()                         
                        domain = [('res_branch_id', '=', branch),('product_template_id','=',self.id)]
                        product_template_price_id = self.env['product.template.price'].search(domain, limit=1)        
                        if product_template_price_id:
                            product_template_price_id.unlink()
                                                                              
            except requests.exceptions.HTTPError as errh:
                _logger.error(errh)

    @api.model
    def create(self, vals):
        _logger.info("Create Product Product")
        _logger.info(vals)
        res = super().create(vals)        
        context = self.env.context
        cron_process_download = context.get('cron_process_download',False)
        if not cron_process_download:
            res.action_sync_product()        
        return res

    def write(self, vals):
        _logger.info("Write Product Product")
        _logger.info(vals)    
        res = super(ProductTemplate, self).write(vals)
        _logger.info("Prepare Sync Product")
        context = self.env.context
        cron_process_download = context.get('cron_process_download',False)
        if not cron_process_download:
            self.action_sync_product()
        return res
    
    def unlink(self):
        pass
    
class ProductTemplateCouchdb(models.Model):
    _inherit = 'product.template.couchdb'
        
    branch_id = fields.Many2one('res.branch','Store')
    
