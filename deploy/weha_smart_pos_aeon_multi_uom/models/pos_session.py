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

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        if self.config_id.allow_multi_uom:
            loaded_data['multi_uom_id'] = {multi_uom['id']: multi_uom for multi_uom in loaded_data['product.multi.uom']}

    @api.model
    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if self.config_id.allow_multi_uom:
            new_model = 'product.multi.uom'
            if new_model not in result:
                result.append(new_model)
        return result

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend(['has_multi_uom','multi_uom_ids','new_barcode'])
        return result

    def _loader_params_product_multi_uom(self):
        return {'search_params': {'domain': [], 'fields': ['multi_uom_id','price','barcode','uom_name'], 'load': False}}

    def _get_pos_ui_product_multi_uom(self, params):
        result = self.env['product.multi.uom'].search_read(**params['search_params'])
        for res in result:
            uom_id = self.env['uom.uom'].browse(res['multi_uom_id'])
            res['multi_uom_id'] = [uom_id.id,uom_id.name] 
        return result