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
        
    def action_update_store_product(self):
        for row in self:
            for branch_id in row.branch_ids:                
                domain = [
                    ('res_branch_id', '=', branch_id.id),
                    ('product_template_id', '=', row.id)
                ]
                product_template_price_id = self.env['product.template.price'].search(domain, limit=1)
                if not product_template_price_id:
                    vals  = {
                        'res_branch_id': branch_id.id,
                        'product_template_id': row.id,
                        'list_price': row.list_price
                    }
                    self.env['product.template.price'].create(vals)
                else:
                    product_template_price_id.list_price = row.list_price

    product_couchdb_sync = fields.Boolean('Is Sync', default=False)
    product_json = fields.Text('Product JSON')
    product_couchdb_id = fields.Text('CouchDB Id')
    product_couchdb_rev = fields.Text('CouchDB Rev')
    
    product_template_price_ids = fields.One2many('product.template.price','product_template_id','Product Prices')

class ProductTemplatePrice(models.Model):
    _name = 'product.template.price'

    res_branch_id = fields.Many2one('res.branch','Store')
    product_template_id = fields.Many2one('product.template','Product')
    list_price = fields.Float('Sale Price')

    # _sql_constraints = [ ('unique_product_template_price', 'unique(res_branch_id, product_template_id)', 'Price for Store or Product already exist!')	]

