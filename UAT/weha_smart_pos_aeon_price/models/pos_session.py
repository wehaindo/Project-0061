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
# from odoo.addons.weha_smart_pos_data.libs.lzstring import LZString
import simplejson as json
import base64
# from lzstring import LZString
from datetime import datetime, date


import logging
_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product_by_product_id(self):
        result = super(PosSession, self)._loader_params_product_product_by_product_id()
        return result

    # need to improve performance
    def _process_pos_ui_product_product_01(self, products):
        """
        Modify the list of products to add the categories as well as adapt the lst_price
        :param products: a list of products
        """
        # if not self.config_id.use_pos_data_speed_up:
        if self.config_id.currency_id != self.company_id.currency_id:
            for product in products:
                product_template_price_id = self.env['product.template.price'].search([('product_template_id','=',product['product_tmpl_id'][0]),('res_branch_id','=',self.config_id.res_branch_id.id)],limit=1)   
                if product_template_price_id:
                    product['lst_price'] = self.company_id.currency_id._convert(product_template_price_id.list_price, self.config_id.currency_id,self.company_id, fields.Date.today())
        else:
            for product in products:
                _logger.info(product)                
                product_template_price_id = self.env['product.template.price'].search([('product_template_id','=',product['product_tmpl_id'][0]),('res_branch_id','=',self.config_id.res_branch_id.id)],limit=1)                                
                if product_template_price_id:
                    product['lst_price'] = product_template_price_id.list_price
                    # product['member_lst_price'] = product_template_price_id.member_price

        categories = self._get_pos_ui_product_category(self._loader_params_product_category())
        product_category_by_id = {category['id']: category for category in categories}
        _logger.info("product_category_by_id")
        _logger.info(product_category_by_id)
        for product in products:        
            _logger.info(product['categ_id'])
            product['categ'] = product_category_by_id[product['categ_id'][0]]

    def _process_pos_ui_product_product(self, products):
        """
        Modify the list of products to add the categories as well as adapt the lst_price
        :param products: a list of products
        """
        # if not self.config_id.use_pos_data_speed_up:
        if self.config_id.currency_id != self.company_id.currency_id:
            for product in products:
                product_template_price_id = self.env['product.template.price'].search([('product_template_id','=',product['product_tmpl_id'][0]),('res_branch_id','=',self.config_id.res_branch_id.id)],limit=1)                
                product['lst_price'] = self.company_id.currency_id._convert(product_template_price_id.list_price, self.config_id.currency_id,
                                                                                    self.company_id, fields.Date.today())
                # product['member_lst_price']  = self.company_id.currency_id._convert(product_template_price_id.member_price, self.config_id.currency_id,
                #                                                                     self.company_id, fields.Date.today())
        else:
            for product in products:
                _logger.info(product)
                product_template_price_id = self.env['product.template.price'].search([('product_template_id','=',product['product_tmpl_id'][0]),('res_branch_id','=',self.config_id.res_branch_id.id)],limit=1)                                
                product['lst_price'] = product_template_price_id.list_price
                # product['member_lst_price'] = product_template_price_id.member_price

        categories = self._get_pos_ui_product_category(self._loader_params_product_category())
        product_category_by_id = {category['id']: category for category in categories}
        for product in products:
            product['categ'] = product_category_by_id[product['categ_id'][0]]

    # def _get_pos_ui_product_product(self, params):
    #     self = self.with_context(**params['context'])
    #     if not self.config_id.limited_products_loading:
    #         products = self.env['product.product'].search_read(**params['search_params'])
    #     else:
    #         products = self.config_id.get_limited_products_loading(params['search_params']['fields'])

    #     self._process_pos_ui_product_product(products)
    #     return products

    def _get_pos_ui_product_product(self, params):
        _logger.info("price_get_pos_ui_product_product")
        if self.config_id.use_pos_data_speed_up:
            return []
        else:        
            self = self.with_context(**params['context'])
            if not self.config_id.limited_products_loading:
                products = self.env['product.product'].search_read(**params['search_params'])
            else:
                products = self.config_id.get_limited_products_loading(params['search_params']['fields'])

            self._process_pos_ui_product_product(products)
            return products

    def _loader_params_product_pricelist(self):
        result = super(PosSession, self)._loader_params_product_pricelist()
        result['search_params']['fields'].append('price_type')
        return result

    def _product_pricelist_item_fields(self):
        result = super(PosSession, self)._product_pricelist_item_fields()
        result.append('prc_no')
        return result

    # def _loader_params_product_pricelist(self):
    #     if self.config_id.use_pricelist:
    #         domain = [('id', 'in', self.config_id.available_pricelist_ids.ids)]
    #     else:
    #         domain = [('id', '=', self.config_id.pricelist_id.id)]
    #     return {'search_params': {'domain': domain, 'fields': ['name', 'display_name', 'discount_policy']}}

    # def _get_pos_ui_product_pricelist(self, params):
    #     _logger.info('_get_pos_ui_product_pricelist')
    #     _logger.info(params)
    #     if self.config_id.use_pos_data_speed_up:
    #         _logger.info('use_pos_data_speed_up')
    #         pricelists = self.env['product.pricelist'].search_read(**params['search_params'])
    #         _logger.info(pricelists)
    #         for pricelist in pricelists:
    #             pricelist['items'] = []
    #         return pricelists
    #     else:
    #         return super(PosSession, self)._get_pos_ui_product_pricelist(params)
