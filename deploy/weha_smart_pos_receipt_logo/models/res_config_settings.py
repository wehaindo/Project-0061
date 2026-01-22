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


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    #Admin
    is_show_receipt_logo = fields.Boolean(related="pos_config_id.is_show_receipt_logo", readonly=False)
    is_show_pos_global_receipt_logo = fields.Boolean(related="pos_config_id.is_show_pos_global_receipt_logo", readonly=False)
    pos_global_receipt_logo_img = fields.Binary(related="company_id.pos_global_receipt_logo_img", readonly=False)
    is_show_pos_receipt_logo = fields.Boolean(related="pos_config_id.is_show_pos_receipt_logo", readonly=False)
    pos_receipt_logo_img = fields.Binary(related="pos_config_id.pos_receipt_logo_img", readonly=False)
    
