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
    

    def _get_pos_ui_product_product(self, params):
        if self.config_id.use_pos_data_speed_up:
            return []
        else:
            return super(PosSession, self)._get_pos_ui_product_product(params)

    def _process_pos_ui_product_product_by_product_id(self, products):
        """
        Modify the list of products to add the categories as well as adapt the lst_price
        :param products: a list of products
        """
        # if self.config_id.currency_id != self.company_id.currency_id:
        #     for product in products:
        #         product['lst_price'] = self.company_id.currency_id._convert(product['lst_price'], self.config_id.currency_id,
        #                                                                     self.company_id, fields.Date.today())
       
        # categories = self._get_pos_ui_product_category(self._loader_params_product_category())
        categories = self._get_pos_ui_product_category(self._loader_params_product_category_by_id())
        product_category_by_id = {category['id']: category for category in categories}        
        for product in products:             
            _logger.info(product['categ_id'][0])
            product['categ'] = product_category_by_id[product['categ_id'][0]]

    def _get_pos_ui_product_product_by_product_id(self, params):
        self = self.with_context(**params['context'])
        products = self.env['product.product'].search_read(**params['search_params'])
        self._process_pos_ui_product_product_by_product_id(products)
        return products

    def _loader_params_product_product_by_product_id(self):
        _logger.info("_loader_params_product_product_by_product_id")
        result = self._loader_params_product_product()        
        product_id = self.env.context.get('product_id')
        domain = [('id','=', product_id)]
        result['search_params']['domain'] = domain                
        return result

    def _get_pos_ui_product_category(self, params):
        if self.config_id.use_pos_data_speed_up:
            return []
        else:
           return super(PosSession, self)._get_pos_ui_product_category(params)

    def _loader_params_product_category_by_id(self):        
        result = self._loader_params_product_category()
        product_category_id = self.env.context.get('product_category_id')
        domain = [('id','=',product_category_id)]
        result['search_params']['domain'] = domain
        return result

    def _get_pos_ui_product_category_by_id(self, params):        
        # self = self.with_context(**params['context'])
        categories = self.env['product.category'].search_read(**params['search_params'])
        return categories

    def _get_pos_ui_product_pricelist(self, params):
        _logger.info('_get_pos_ui_product_pricelist')
        if self.config_id.use_pos_data_speed_up:
            _logger.info('use_pos_data_speed_up')
            pricelists = self.env['product.pricelist'].search_read(**params['search_params'])
            for pricelist in pricelists:
                pricelist['items'] = []
            return pricelists
        else:
            return super(PosSession, self)._get_pos_ui_product_pricelist(params)

    @api.model
    def _pos_ui_models_to_load(self):
        models_to_load = super(PosSession, self)._pos_ui_models_to_load()
        if self.config_id.use_pos_data_speed_up:
            models_to_load.remove('product.product')      
        return models_to_load

    pos_data_datetime = fields.Datetime('POS Data Datetime')
    pos_data_zip = fields.Binary('POS Data Zip')
    pos_data_base64 = fields.Text('POs Data (Base64)')

