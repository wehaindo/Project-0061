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

    price_source = fields.Selection(
        [
            ('list_price','Store Price'),
            ('pdc','PDC'),
            ('pdcm','PDCM'),
            ('override','Price Overide'),
            ('member_day','Member Day'),
            ('manual_discount', 'Manual Discount'),
            ('mix_and_match','Mix and Match')
        ],'Price Source', 
        default='list_price'
    )
