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
from odoo import models, fields, tools, api, _
from odoo.exceptions import UserError, ValidationError
import simplejson as json
from datetime import datetime, date
import uuid
import requests
from requests.auth import HTTPBasicAuth
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # def _compute_promotions(self):
    #     for row in self:
    #         # Dynamically generate record values (not stored in DB)
    #         strSQL = """
    #             select c.id as product_template_id, b.id as product_product_id, c.name, e.id, e.promotion_code, e.promotion_description from partial_quantity_fixed_price_product_product_rel a 
    #             left join product_product b on a.product_product_id = b.id 
    #             left join product_template c on b.product_tmpl_id = c.id 
    #             left join partial_quantity_fixed_price d on a.partial_quantity_fixed_price_id = d.id 
    #             left join pos_promotion e on d.pos_promotion_id = e.id
    #             where c.id={}; 
    #         """.format(row.id)
    #         # _logger.info(strSQL)
    #         self.env.cr.execute(strSQL)
    #         results = self.env.cr.fetchall()
    #         product_promotion_ids = [(0, 0, {'product_template_id': result[0], 'product_product_id': result[1], 'pos_promotion_id': result[3]}) for result in results]                   
    #         _logger.info(product_promotion_ids)
    #         row.product_promotion_ids = product_promotion_ids
            
    # product_promotion_ids = fields.One2many('product.promotion', compute="_compute_promotions", string='Promotions', store=False, readonly=True)
    product_promotion_ids = fields.One2many('product.promotion', 'product_template_id', string='Promotions', store=False, readonly=True)
    
    
class ProductPromotion(models.Model):
    _name = 'product.promotion'
    _auto = False
        
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute("""create or replace view {} AS 
            SELECT row_number() OVER () AS id, c.id AS product_template_id, b.id AS product_product_id, e.id AS pos_promotion_id 
            FROM partial_quantity_fixed_price_product_product_rel a 
            LEFT JOIN product_product b on a.product_product_id = b.id 
            LEFT JOIN product_template c on b.product_tmpl_id = c.id 
            LEFT JOIN partial_quantity_fixed_price d on a.partial_quantity_fixed_price_id = d.id 
            LEFT JOIN pos_promotion e on d.pos_promotion_id = e.id
        """.format(self._table))
    
    product_template_id = fields.Many2one('product.template','Product')
    product_template_name = fields.Char(related="product_template_id.name")
    product_product_id = fields.Many2one('product.product','Product Variants')
    product_product_name = fields.Char(related="product_product_id.name")
    pos_promotion_id = fields.Many2one('pos.promotion', 'Promotion')
    pos_promotion_name = fields.Char(related="pos_promotion_id.promotion_code")
    pos_promotion_description = fields.Char(related="pos_promotion_id.promotion_description")


