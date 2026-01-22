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

import logging
_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'
        
    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()        
        result.append('product.brand')
        return result
        
    def _loader_params_product_brand(self):
        res = {
            'search_params': {
                'domain': [],
                'fields': ['name','description','partner_id'],
            },
        }
        return res

    def _get_pos_ui_product_brand(self, params):
        return self.env['product.brand'].search_read(**params['search_params'])
    
    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].append('product_brand_id')
        return result