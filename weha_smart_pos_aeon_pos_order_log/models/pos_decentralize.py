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
from datetime import datetime, date, timedelta
from io import StringIO
import base64

import logging

from pytz import timezone
import pytz


_logger = logging.getLogger(__name__)



class PosDecentralizeOrderReceipt(models.Model):
    _name = 'pos.decentralize.order.receipt'    
    
    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = []
        for order in orders:
            order_id = self.env['pos.decentralize.order.receipt'].create(order)
            order_ids.append(order_id)                                                        
        return order_ids
    
    name = fields.Datetime('Date and Time', default=lambda self: fields.Datetime.now())    
    pos_config_id = fields.Integer('Pos Config')
    pos_session_id = fields.Integer('Pos Session')
    pos_reference = fields.Char("Pos Reference")
    pos_order_receipt_html = fields.Text('Order Receipt HTML')
    pos_order_receipt_base64 = fields.Text('Order Receipt')
    
    


