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
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)        
        res.update({'is_refund': ui_order['is_refund']})
        res.update({'refund_parent_pos_reference': ui_order['refund_parent_pos_reference']})        
        return res
    
    is_refund = fields.Boolean('Refund', default=False) 
    refund_user = fields.Many2one('res.users','Refund User')
    refund_parent_pos_reference = fields.Char('Parent Pos Refund')

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    refund_user = fields.Many2one('res.users','Refund User')