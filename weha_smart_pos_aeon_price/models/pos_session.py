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


    def _prepare_line(self, order_line):
        """ Derive from order_line the order date, income account, amount and taxes information.

        These information will be used in accumulating the amounts for sales and tax lines.
        """
        def get_income_account(order_line):
            product = order_line.product_id
            income_account = product.with_company(order_line.company_id)._get_product_accounts()['income']
            if not income_account:
                raise UserError(_('Please define income account for this product: "%s" (id:%d).')
                                % (product.name, product.id))
            return order_line.order_id.fiscal_position_id.map_account(income_account)

        tax_ids = order_line.tax_ids_after_fiscal_position\
                    .filtered(lambda t: t.company_id.id == order_line.order_id.company_id.id)
        sign = -1 if order_line.qty >= 0 else 1
        price = sign * order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
        # The 'is_refund' parameter is used to compute the tax tags. Ultimately, the tags are part
        # of the key used for summing taxes. Since the POS UI doesn't support the tags, inconsistencies
        # may arise in 'Round Globally'.
        check_refund = lambda x: x.qty * x.price_unit < 0
        is_refund = check_refund(order_line)
        
        if  order_line.order_id.session_id.config_id.enable_aeon_currency:
            currency_id = order_line.order_id.session_id.config_id.aeon_currency_id
            tax_data = tax_ids.compute_all(price_unit=price, quantity=abs(order_line.qty), currency=currency_id, is_refund=is_refund, fixed_multiplicator=sign)
        else:            
            tax_data = tax_ids.compute_all(price_unit=price, quantity=abs(order_line.qty), currency=self.currency_id, is_refund=is_refund, fixed_multiplicator=sign)
            
        taxes = tax_data['taxes']
        # For Cash based taxes, use the account from the repartition line immediately as it has been paid already
        for tax in taxes:
            tax_rep = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
            tax['account_id'] = tax_rep.account_id.id
        date_order = order_line.order_id.date_order
        taxes = [{'date_order': date_order, **tax} for tax in taxes]
        return {
            'date_order': order_line.order_id.date_order,
            'income_account_id': get_income_account(order_line).id,
            'amount': order_line.price_subtotal,
            'taxes': taxes,
            'base_tags': tuple(tax_data['base_tags']),
        }


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
                product['lst_price'] = self.company_id.currency_id._convert(product_template_price_id.list_price, self.config_id.currency_id,self.company_id, fields.Date.today())                
        else:
            for product in products:
                _logger.info('_process_pos_ui_product_product')
                _logger.info(product)
                product_template_price_id = self.env['product.template.price'].search([('product_template_id','=',product['product_tmpl_id'][0]),('res_branch_id','=',self.config_id.res_branch_id.id)],limit=1)                                
                product['lst_price'] = product_template_price_id.list_price
                # product['member_lst_price'] = product_template_price_id.member_price

        categories = self._get_pos_ui_product_category(self._loader_params_product_category())
        product_category_by_id = {category['id']: category for category in categories}
        for product in products:
            product['categ'] = product_category_by_id[product['categ_id'][0]]

    def _get_pos_ui_product_product(self, params):
        _logger.info("price_get_pos_ui_product_product")
        if self.config_id.use_pos_data_speed_up:
            _logger.info('use_pos_data_speed_up 3')
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

