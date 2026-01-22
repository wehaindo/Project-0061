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

    def _loader_params_product_product(self):
        
        # domain = [
        #     '&', '&', '&',('branch_ids','in',[self.config_id.res_branch_id.id]), ('sale_ok', '=', True), ('available_in_pos', '=', True), '|',
        #     ('company_id', '=', self.config_id.company_id.id), ('company_id', '=', False)
        # ]
        # # domain = AND ([domain,[('branch_ids','in',[self.config_id.res_branch_id.id])]])
        # if self.config_id.limit_categories and self.config_id.iface_available_categ_ids:
        #     domain = AND([domain, [('pos_categ_id', 'in', self.config_id.iface_available_categ_ids.ids)]])
        # if self.config_id.iface_tipproduct:
        #     domain = OR([domain, [('id', '=', self.config_id.tip_product_id.id)]])
        domain = [('branch_ids','in',[self.config_id.res_branch_id.id])]
        _logger.info(domain)
        return {
            'search_params': {
                'domain': domain,
                'fields': [
                    'display_name', 'lst_price', 'standard_price', 'categ_id', 'pos_categ_id', 'taxes_id', 'barcode',
                    'default_code', 'to_weight', 'uom_id', 'description_sale', 'description', 'product_tmpl_id', 'tracking',
                    'available_in_pos', 'attribute_line_ids', 'active', '__last_update', 'branch_ids', 'optional_product_ids'
                ],
                'order': 'sequence,default_code,name',
            },
            'context': {'display_default_code': False},
        }

    def _process_pos_ui_product_product(self, products):
        """
        Modify the list of products to add the categories as well as adapt the lst_price
        :param products: a list of products
        """
        if self.config_id.currency_id != self.company_id.currency_id:
            for product in products:
                # _logger.info(product)
                product_template_price_id = self.env['product.template.price'].search([('product_template_id','=',product['product_tmpl_id'][0]),('res_branch_id','=',self.config_id.res_branch_id.id)],limit=1)                
                product['lst_price'] = self.company_id.currency_id._convert(product_template_price_id.list_price, self.config_id.currency_id,
                                                                            self.company_id, fields.Date.today())
        else:
            for product in products:
                _logger.info(product)
                product_template_price_id = self.env['product.template.price'].search([('product_template_id','=',product['product_tmpl_id'][0]),('res_branch_id','=',self.config_id.res_branch_id.id)],limit=1)                                
                product['lst_price'] = product_template_price_id.list_price

        categories = self._get_pos_ui_product_category(self._loader_params_product_category())
        product_category_by_id = {category['id']: category for category in categories}
        for product in products:
            product['categ'] = product_category_by_id[product['categ_id'][0]]

    def _get_pos_ui_product_product(self, params):
        self = self.with_context(**params['context'])
        if not self.config_id.limited_products_loading:
            products = self.env['product.product'].search_read(**params['search_params'])
        else:
            products = self.config_id.get_limited_products_loading(params['search_params']['fields'])

        self._process_pos_ui_product_product(products)
        return products
