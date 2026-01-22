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
    enable_prima_session_report = fields.Boolean(related='pos_config_id.enable_prima_session_report', readonly=False)
    prima_partner_id = fields.Char(related='pos_config_id.prima_partner_id', readonly=False)
    prima_merchant_id = fields.Char(related='pos_config_id.prima_merchant_id', readonly=False)
    prima_terminal_id = fields.Char(related='pos_config_id.prima_terminal_id', readonly=False)
    
