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


class PosConfig(models.Model):
    _inherit = 'pos.config'

    #Admin
    #Prima
    enable_prima_session_report = fields.Boolean('Enable Prima Session Report', default=False)
    prima_partner_id = fields.Char('Prima Partner Id')
    prima_merchant_id = fields.Char('Prima Merchant Id')
    prima_terminal_id = fields.Char('Prima Terminal Id')
    


    


