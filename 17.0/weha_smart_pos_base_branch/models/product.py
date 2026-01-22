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
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from itertools import groupby
from operator import itemgetter
from datetime import date


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    #Branch Price
    is_enable_product_template_price = fields.Boolean('Enable Branch Price', default=False)
    product_template_price_ids = fields.One2many('product.template.price','product_template_id','Prices')

  
#Branch Price
class ProductTemplatePrice(models.Model):
    _name = 'product.template.price'

    product_template_id = fields.Many2one('product.template', 'Product')
    branch_id = fields.Many2one('res.branch', 'Branch', required=True)
    list_price = fields.Float('List Price', default=0)

