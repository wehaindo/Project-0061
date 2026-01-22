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

import logging
_logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    branch_id = fields.Many2one('res.branch', 'Store')  
    # price_type = fields.Selection(
    #     [
    #         ('PDC','PDC'),
    #         ('PDCM','PDCM'),
    #     ],
    #     "Price Type",
    #     default='PDC'      
    # )

class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'


    def action_sync(self):
        for row in self:            
            row.generate_json()
            row.sync_couchdb()
            
    def _prepare_json(self):
        _logger.info("Prepare Product Pricelist Item Json")
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))
        
        product_pricelist_items = self.env['product.pricelist.item'].search_read(domain=[('id','=', self.id)], fields=self.env['pos.session']._product_pricelist_item_fields(), limit=1)
        product_pricelist_item = product_pricelist_items[0]

        _logger.info('product_pricelist_item')
        _logger.info(product_pricelist_item)
        if '__last_update' in product_pricelist_item:
            del product_pricelist_item['__last_update']

        if self.product_pricelist_item_couchdb_id:
            product_pricelist_item['_id'] =  self.product_pricelist_item_couchdb_id
        else:
            product_pricelist_item_couchdb_id = "productpricelistitem_" + str(uuid.uuid4())
            product_pricelist_item['_id'] =  product_pricelist_item_couchdb_id
        
        return product_pricelist_item['_id'], product_pricelist_item 


    def _update_rev(self, json_str, rev):
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))
        
        product_pricelist_item = json.loads(json_str)
        product_pricelist_item.update({'_rev': rev})
        product_pricelist_item_json = json.dumps(product_pricelist_item, default=json_serial)
        return product_pricelist_item_json
        # return json
    
    def generate_json(self):
        _logger.info("Generate Product Pricelist Item Json")
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))

        product_pricelist_item_couchdb_id, product_pricelist_item = self._prepare_json()

        product_pricelist_item_json = json.dumps(product_pricelist_item, default=json_serial)
        vals = {
            'product_pricelist_item_couchdb_id': product_pricelist_item_couchdb_id,
            'product_pricelist_item_json': product_pricelist_item_json
        }
        super(PricelistItem, self).write(vals)
        
    def sync_couchdb(self):
        auth = HTTPBasicAuth('admin','pelang1')
        headers = {
            'Content-Type': 'application/json'
        }
        store_code = self.pricelist_id.branch_id.code
        try:
            if self.product_pricelist_item_couchdb_id:
                response = requests.get(f'http://server1601.weha-id.com:5984/s_{store_code}_product_pricelist_items/{self.product_pricelist_item_couchdb_id}', auth=auth, headers=headers)
                if response.status_code == 200:
                    _logger.info("Product Priceliss Item Found")
                    json_data = response.json()
                    if isinstance(json_data, dict):
                        couchdb_product_pricelist_item = json_data
                    if isinstance(json_data, list):
                        couchdb_product_pricelist_item = json_data[0]
                    _logger.info(couchdb_product_pricelist_item)
                    product_pricelist_item_json = self._update_rev(self.product_pricelist_item_json, couchdb_product_pricelist_item['_rev'])
                    response = requests.put(f'http://server1601.weha-id.com:5984/s_{store_code}_product_pricelist_items/{couchdb_product_pricelist_item["_id"]}', auth=auth, headers=headers, data=product_pricelist_item_json)
                    if response.status_code == 200 or response.status_code == 201:
                        json_data = response.json()
                        vals = {
                            'product_pricelist_item_couchdb_rev': json_data['rev']
                        }
                        super(PricelistItem, self).write(vals)
                elif response.status_code == 404:
                    response = requests.post(f'http://server1601.weha-id.com:5984/s_{store_code}_product_pricelist_items', auth=auth, headers=headers, data=self.product_pricelist_item_json)
                    _logger.info("Not Found Create Document")
                    _logger.info(response.status_code)
                    if response.status_code == 200:
                        pass
                    if response.status_code == 201:
                        json_data = response.json()
                        _logger.info(json_data)
                        vals = {
                            'product_pricelist_item_couchdb_rev': json_data['rev']
                        }
                        super(PricelistItem, self).write(vals)
            else:
                _logger.info("Have no Product Couchdb ID")      
                response = requests.post(f'http://server1601.weha-id.com:5984/s_{store_code}_product_pricelist_items', auth=auth, headers=headers, data=self.product_category_json)        
                _logger.info(response.status_code)
                if response.status_code == 200:
                    pass
                if response.status_code == 201:
                    json_data = response.json()
                    _logger.info(json_data)
                    vals = {
                            'product_pricelist_item_couchdb_rev': json_data['rev']
                    }
                    super(ProductPricelist, self).write(vals)
        except requests.exceptions.HTTPError as errh:
            _logger.info("Error")    


    branch_id = fields.Many2one('res.branch',related='pricelist_id.branch_id')

    # CouchDB
    product_pricelist_item_couchdb_sync = fields.Boolean('Is Sync', default=False)
    product_pricelist_item_json = fields.Text('JSON')
    product_pricelist_item_couchdb_id = fields.Text('CouchDB ID')
    product_pricelist_item_couchdb_rev = fields.Text('CouchDB Rev')

    @api.model
    def create(self, vals):
        res = super(PricelistItem, self).create(vals) 
        res.action_sync()
        return res
    
    def write(self, vals):
        res = super(PricelistItem, self).write(vals)
        self.action_sync()
        return res

        
