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


class ResBranch(models.Model):
    _inherit = 'res.branch'

    couchdb_server_url = fields.Char('CouchDB Server')
    couchdb_product_db = fields.Char('Products')
    couchdb_product_pricelist_items_db = fields.Char("Pricelists")
