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
import pytz

import re

import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update({'is_void': ui_order['is_void']})
        res.update({'is_refund': ui_order['is_refund']})
        res.update({'refund_parent_pos_reference': ui_order['refund_parent_pos_reference']})
        res.update({'void_parent_pos_reference': ui_order['void_parent_pos_reference']})
        return res


    def _export_for_ui(self, order):
        uid = re.search('([0-9]){9}', order.pos_reference)
        if not uid:
            uid = re.search('([0-9-]){14}', order.pos_reference)
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')    
        return {
            'lines': [[0, 0, line] for line in order.lines.export_for_ui()],
            'statement_ids': [[0, 0, payment] for payment in order.payment_ids.export_for_ui()],
            'name': order.pos_reference,
            # 'uid': re.search('([0-9-]){14,}', order.pos_reference).group(0),
            'uid': uid.group(0),
            'amount_paid': order.amount_paid,
            'amount_total': order.amount_total,
            'amount_tax': order.amount_tax,
            'amount_return': order.amount_return,
            'pos_session_id': order.session_id.id,
            'pricelist_id': order.pricelist_id.id,
            'partner_id': order.partner_id.id,
            'user_id': order.user_id.id,
            'sequence_number': order.sequence_number,
            'creation_date': str(order.date_order.astimezone(timezone)),
            'fiscal_position_id': order.fiscal_position_id.id,
            'to_invoice': order.to_invoice,
            'to_ship': order.to_ship,
            'state': order.state,
            'account_move': order.account_move.id,
            'id': order.id,
            'is_tipped': order.is_tipped,
            'tip_amount': order.tip_amount,
            'access_token': order.access_token,            
            'is_void': order.is_void,
            'is_refund': order.is_refund,            
            'has_refundable_lines ': order.has_refundable_lines,
        }
        
    is_void = fields.Boolean('Void', default=False) 
    is_refund = fields.Boolean('Refund', default=False) 
    refund_user = fields.Many2one('res.users','Refund User')
    void_user = fields.Many2one('res.users','Void User')
    refund_parent_pos_reference = fields.Char('Parent Pos Refund')
    void_parent_pos_reference = fields.Char('Parent Pos Void')
    # reason = fields.Char('Reason')

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    refund_user = fields.Many2one('res.users','Refund User')