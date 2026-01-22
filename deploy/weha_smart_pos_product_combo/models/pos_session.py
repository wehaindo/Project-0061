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
from odoo import models, fields
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].append('is_pack')
        result['search_params']['fields'].append('pack_ids')
        return result

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result.append('product.pack')            
        return result

    def _loader_params_product_pack(self):
        res = {
            'search_params': {
                'fields': ['product_ids', 'is_required', 'category_id','bi_product_product','bi_product_template','name'],
            },
        }
        return res
    

    def _get_pos_ui_product_pack(self, params):
        return self.env['product.pack'].search_read(**params['search_params'])
