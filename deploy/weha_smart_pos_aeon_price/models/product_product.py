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


class ProductTemplate(models.Model):
    _inherit = 'product.template'
        
    #Inherit from weha_smart_pos_aeon_pos_data
    def _prepare_product_json(self, branch_id):
        _logger.info("Prepare Product JSON")
        product_template_couchdb_id, product_couchdb_id, product = super(ProductTemplate, self)._prepare_product_json(branch_id)
        #Update Store Price
        domain  = [
            ('res_branch_id','=', branch_id.id),
            ('product_template_id','=', self.id)
        ]
        product_template_price_id = self.env['product.template.price'].search(domain,limit=1)
        if product_template_price_id:
            product['member_lst_price'] =  product_template_price_id.member_price
                
        return product_template_couchdb_id, product_couchdb_id, product

    def action_update_store_product(self):
        _logger.info('action_update_store_product')
        for row in self:
            for branch_id in row.branch_ids:    
                _logger.info("branch_id")            
                domain = [
                    ('res_branch_id', '=', branch_id.id),
                    ('product_template_id', '=', row.id)
                ]
                _logger.info(domain)
                product_template_price_id = self.env['product.template.price'].search(domain, limit=1)
                if not product_template_price_id:
                    _logger.info('create product template price')
                    vals  = {
                        'res_branch_id': branch_id.id,
                        'product_template_id': row.id,
                        'list_price': row.list_price,                        
                    }
                    _logger.info(vals)
                    self.env['product.template.price'].create(vals)

    member_lst_price = fields.Float("Member Price")
    product_couchdb_sync = fields.Boolean('Is Sync', default=False)
    product_json = fields.Text('Product JSON')
    product_couchdb_id = fields.Text('CouchDB Id')
    product_couchdb_rev = fields.Text('CouchDB Rev')
    
    product_template_price_ids = fields.One2many('product.template.price','product_template_id','Product Prices')

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        #res.action_update_store_product()
        return res
    
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        #self.action_update_store_product()
        return True

class ProductTemplatePrice(models.Model):
    _name = 'product.template.price'

    res_branch_id = fields.Many2one('res.branch','Store', index=True)
    product_template_id = fields.Many2one('product.template','Product', index=True)
    list_price = fields.Float('Sale Price')
    member_price = fields.Float('Member Price')

    # _sql_constraints = [ ('unique_product_template_price', 'unique(res_branch_id, product_template_id)', 'Price for Store or Product already exist!')	]

