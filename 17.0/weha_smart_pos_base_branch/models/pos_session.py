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

    #Branch Price
    def _process_pos_ui_product_product(self, products):
        """
        Modify the list of products to add the categories as well as adapt the lst_price
        :param products: a list of products
        """        
        super(PosSession,self)._process_pos_ui_product_product(products)
                
        for product in products:
            product_template_id = self.env['product.template'].browse(product['product_tmpl_id'][0])
            if product_template_id.is_enable_product_template_price:
                _logger.info('Enable Product Template Price')
                domain = [
                    ('branch_id','=',self.config_id.res_branch_id.id),
                    ('product_template_id', '=' , product_template_id.id),
                ]
                product_template_filtered = self.env['product.template.price'].search(domain, limit=1)
                if product_template_filtered:
                    _logger.info('Product Template Filtered was Found')
                    if self.config_id.currency_id != self.company_id.currency_id:         
                        product['lst_price'] = self.company_id.currency_id._convert(product_template_filtered.list_price, self.config_id.currency_id,self.company_id, fields.Date.today())
                    else:
                        product['lst_price'] = product_template_filtered.list_price
    
    #Branch
    branch_id = fields.Many2one('res.branch', related='config_id.res_branch_id',string="Branch", help='Allowed Branches', readonly=True)

