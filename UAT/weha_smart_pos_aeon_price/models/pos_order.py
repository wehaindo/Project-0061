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


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    list_price = fields.Float('List Price')
    price_override_user = fields.Many2one('res.users','Override User')
    pos_pricelist_id = fields.Many2one('product.pricelist','Pricelist')
    prc_no = fields.Char('Price Change #', size=20)
    