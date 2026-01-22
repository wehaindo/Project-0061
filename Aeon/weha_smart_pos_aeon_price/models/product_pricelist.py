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


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    price_type = fields.Selection(
        [
            ('Store', 'Store'),
            ('PDC','PDC'),
            ('PDCM','PDCM'),
        ],
        "Price Type",
        default='pdc'      
    )

class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    prc_no = fields.Char('Price Change #', size=20)


        
