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


AVAILABLE_REASONS = [
    ('001', 'P-System not update'),
    ('002', 'P-Price Card not update'),
    ('003', 'P-Expire POP'),
    ('004', 'P-Wrong POP'),
    ('005', 'P-Seito/Price checker issue'),
    ('006', 'Scanning'),
    ('007', 'Wrong Purchase'),
    ('008', 'Expired'),
    ('009', 'Damage'),
    ('010', 'Discount'),
    ('011', 'Cancel Item'),
    ('012', 'Exchange'),
    ('013', 'Payment'),
    ('014', 'VAT'),
    ('015', 'Others'),
]

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    def _export_for_ui(self, orderline):
        result = super(PosOrderLine, self)._export_for_ui(orderline)
        result['list_price'] = orderline.list_price
        result['price_override_user'] = orderline.price_override_user
        result['price_override_reason'] = orderline.price_override_reason
        result['pos_pricelist_id'] = orderline.pos_pricelist_id        
        result['price_source'] = orderline.price_source
        result['prc_no'] = orderline.prc_no
        result['discount_type'] = orderline.discount_type
        result['discount_amount'] = orderline.discount_amount        
        return result

    list_price = fields.Float('List Price')
    price_override_user = fields.Many2one('res.users','Override User')
    price_override_reason = fields.Selection(AVAILABLE_REASONS, 'Override Reason')
    pos_pricelist_id = fields.Many2one('product.pricelist','Pricelist')
    prc_no = fields.Char('Price Change #', size=20)
    discount_type = fields.Selection([('percentage','Percentage'),('fixed','Fixed')], 'Discount Type')
    discount_amount = fields.Float('Discount Amount')
