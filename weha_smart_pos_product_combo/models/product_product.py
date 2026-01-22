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


class ProductProduct(models.Model):
	_inherit = 'product.template'

	is_pack = fields.Boolean(string='Is Combo Product')
	pack_ids = fields.One2many('product.pack', 'bi_product_template', 'Product pack')
