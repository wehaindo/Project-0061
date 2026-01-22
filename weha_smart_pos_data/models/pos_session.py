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
from odoo.osv.expression import AND, OR
from odoo.service.common import exp_version
from odoo.addons.weha_smart_pos_data.libs.lzstring import LZString
import simplejson as json
import base64
# from lzstring import LZString
from datetime import datetime, date


import logging
_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _get_pos_ui_product_product_by_product_id(self, params):
        self = self.with_context(**params['context'])
        if not self.config_id.limited_products_loading:
            products = self.env['product.product'].search_read(**params['search_params'])
        else:
            products = self.config_id.get_limited_products_loading(params['search_params']['fields'])

        self._process_pos_ui_product_product(products)
        return products

    def _loader_params_product_product_by_product_id(self, product_id):
        domain = [
            '&', '&', '&', ('id','=', product_id), ('sale_ok', '=', True), ('available_in_pos', '=', True), '|',
            ('company_id', '=', self.config_id.company_id.id), ('company_id', '=', False)
        ]
        if self.config_id.limit_categories and self.config_id.iface_available_categ_ids:
            domain = AND([domain, [('pos_categ_id', 'in', self.config_id.iface_available_categ_ids.ids)]])
        if self.config_id.iface_tipproduct:
            domain = OR([domain, [('id', '=', self.config_id.tip_product_id.id)]])

        return {
            'search_params': {
                'domain': domain,
                'fields': [
                    'display_name', 'lst_price', 'standard_price', 'categ_id', 'pos_categ_id', 'taxes_id', 'barcode',
                    'default_code', 'to_weight', 'uom_id', 'description_sale', 'description', 'product_tmpl_id', 'tracking',
                    'write_date', 'available_in_pos', 'attribute_line_ids', 'active'
                ],
                'order': 'sequence,default_code,name',
            },
            'context': {'display_default_code': False},
        }

    @api.model
    def _pos_ui_models_to_load(self):
        models_to_load = super(PosSession, self)._pos_ui_models_to_load()
        models_to_load.remove('product.product')      
        return models_to_load


    pos_data_datetime = fields.Datetime('POS Data Datetime')
    pos_data_zip = fields.Binary('POS Data Zip')
    pos_data_base64 = fields.Text('POs Data (Base64)')

    def load_pos_data(self):
        loaded_data = {}
        self = self.with_context(loaded_data=loaded_data)
        for model in self._pos_ui_models_to_load():
            loaded_data[model] = self._load_model(model)
        self._pos_data_process(loaded_data)
        _logger.info("Load POS Data")
        # _logger.info(loaded_data)
        return loaded_data

    def load_pos_data_speed(self):
        lz_string_obj = LZString()

        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))
        loaded_data = {}
        self = self.with_context(loaded_data=loaded_data)
        pos_data_id = self.env['pos.data'].get_last_pos_data()
        if not pos_data_id:
            _logger.info('No Last Pos Data')
            loaded_data['product.product'] = []
            for model in self._pos_ui_models_to_load():
                loaded_data[model] = self._load_model(model)                
            self._pos_data_process(loaded_data)
            _logger.info("Load POS Data Speed")
            _logger.info(datetime.now())
            lzstring_loaded_data = lz_string_obj.compressToBase64(json.dumps(loaded_data, default=json_serial))
            _logger.info(datetime.now())
            self.pos_data_base64 = lzstring_loaded_data
            # self.pos_data_base64 = base64.b64encode(json.dumps(loaded_data, default=json_serial).encode('utf-8'))            
            return self.pos_data_base64
        else:
            if not self.pos_data_datetime:
                _logger.info('No Datetime')
                loaded_data['product.product'] = json.loads(pos_data_id.pos_data_str)
                for model in self._pos_ui_models_to_load():
                    loaded_data[model] = self._load_model(model)
                self._pos_data_process(loaded_data)
                _logger.info("Load POS Data Speed")
                _logger.info(datetime.now())
                lzstring_loaded_data = lz_string_obj.compressToBase64(json.dumps(loaded_data, default=json_serial))
                _logger.info(datetime.now())
                self.pos_data_base64 = lzstring_loaded_data
                # self.pos_data_base64 = base64.b64encode(json.dumps(loaded_data, default=json_serial).encode('utf-8'))
                self.pos_data_datetime = pos_data_id.name   
                return self.pos_data_base64
            elif pos_data_id.name > self.pos_data_datetime:
                _logger.info('Different Datetime')
                _logger.info(datetime.now())
                loaded_data['product.product'] = json.loads(pos_data_id.pos_data_str)
                for model in self._pos_ui_models_to_load():
                    loaded_data[model] = self._load_model(model)
                self._pos_data_process(loaded_data)
                _logger.info("Load POS Data Speed")
                #_logger.info(loaded_data)
                _logger.info(datetime.now())
                lzstring_loaded_data = lz_string_obj.compressToBase64(json.dumps(loaded_data, default=json_serial))
                _logger.info(datetime.now())
                self.pos_data_base64 = lzstring_loaded_data
                # self.pos_data_base64 = base64.b64encode(json.dumps(loaded_data, default=json_serial).encode('utf-8'))
                self.pos_data_datetime = pos_data_id.name   
                return self.pos_data_base64
            else:
                _logger.info('Direct from Session')
                return self.pos_data_base64
                
    def load_pos_data_zip(self):
        pass