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
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError,Warning
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID
from functools import partial
from itertools import groupby


class ProductPack(models.Model):
	_name = 'product.pack'

	bi_product_template = fields.Many2one(comodel_name='product.template', string='Product pack')
	bi_product_product = fields.Many2one(comodel_name='product.product', string='Product pack',related='bi_product_template.product_variant_id')
	name = fields.Char(related='category_id.name', readonly="1")
	is_required = fields.Boolean('Required')
	category_id = fields.Many2one('pos.category','Category',required=True)
	product_ids = fields.Many2many(comodel_name='product.product', string='Product', required=True,domain="[('pos_categ_id','=', category_id)]")
