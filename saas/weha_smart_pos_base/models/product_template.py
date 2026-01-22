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
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def allow_create_product(self):
        domain = [
            'active','=', True
        ]
        product_template_ids = self.env['product.template'].search(domain)        
        if len(product_template_ids) >= 7:
            raise ValidationError("Product Limit Error")
        
    @api.model
    def create(self, vals):
        self.allow_create_product()
        res = super(ProductTemplate, self).create(vals)
        return res

    
