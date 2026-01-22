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

    #Couch DB Fields Support
    product_category_couchdb_sync = fields.Boolean('Is Sync', default=False)
    product_category_json = fields.Text('JSON')
    product_category_couchdb_id = fields.Text('CouchDB ID')
    product_category_couchdb_rev = fields.Text('CouchDB Rev')

