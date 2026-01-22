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
import simplejson as json
import base64
from datetime import datetime, date


import logging
_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _get_pos_ui_product_product_for_multiple_barcode(self, params):
        self = self.with_context(**params['context'])
        products = []
        multiple_barcode_products = self.env['product.product'].search_read(**params['search_params'])
        _logger.info(multiple_barcode_products)
        for product in multiple_barcode_products:
            barcode_ids = self.env['product.product.barcode'].search([('product_id','=',product['id'])])
            for barcode_id in barcode_ids:
                new_product = product.copy()
                new_product.update({'barcode': barcode_id.barcode})
                if self.config_id.is_multiple_barcode_price:
                    new_product.update({'lst_price': barcode_id.lst_price})
                _logger.info('New Product')
                _logger.info(new_product)
                products.append(new_product)
                _logger.info(products)
        _logger.info('Products')
        _logger.info(products)
        self._process_pos_ui_product_product(products)        
        return products

    def _loader_params_product_product_for_multiple_barcode(self):
        domain = [
            '&', '&', '&', ('has_multiple_barcode','=', True), ('sale_ok', '=', True), ('available_in_pos', '=', True), '|',
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

    def _get_pos_ui_product_product(self, params):
        self = self.with_context(**params['context'])
        current_products = super(PosSession, self)._get_pos_ui_product_product(params)
        _logger.info(len(current_products))
        multiple_barcode_params = self._loader_params_product_product_for_multiple_barcode()
        products = self._get_pos_ui_product_product_for_multiple_barcode(multiple_barcode_params)
        _logger.info(len(products))
        new_products = current_products + products
        _logger.info(len(new_products))

        _logger.info(new_products)
        return new_products