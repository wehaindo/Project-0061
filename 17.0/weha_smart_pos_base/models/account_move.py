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

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _stock_account_get_anglo_saxon_price_unit(self):
        price_unit = super(AccountMoveLine, self)._stock_account_get_anglo_saxon_price_unit()
        order = self.move_id.pos_order_ids
        if order:
            price_unit = order._get_pos_anglo_saxon_price_unit2(self.product_id, self.move_id.partner_id.id, self.quantity,self.product_uom_id)
        return price_unit
