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
from odoo import api, fields, models, tools, _, registry
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import odoo
import logging
import openerp.addons.decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import threading

_logger = logging.getLogger(__name__)


class pos_order(models.Model):
    _inherit = "pos.order"

    pos_branch_id = fields.Many2one('pos.branch', string='Branch', readonly=1)


class pos_order_line(models.Model):
    _inherit = "pos.order.line"

    pos_branch_id = fields.Many2one('pos.branch', string='Branch', readonly=1)
