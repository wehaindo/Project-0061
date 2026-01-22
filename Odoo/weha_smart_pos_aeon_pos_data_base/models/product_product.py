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

    product_template_data_ids  = fields.One2many('product.template.couchdb', 'product_template_id', 'Product Template Couchdbs')

class ProductTemplateCouchdb(models.Model):
    _name = 'product.template.couchdb'
        
    product_template_id = fields.Many2one('product.template', 'Product Template #')
    # branch_id = fields.Many2one('res.branch','Store')
    product_couchdb_sync = fields.Boolean('Is Sync', default=False)
    product_json = fields.Text('Product JSON')
    product_couchdb_id = fields.Text('CouchDB Id')
    product_couchdb_rev = fields.Text('CouchDB Rev')
    
