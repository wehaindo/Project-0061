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
    is_show_receipt_logo = fields.Boolean("Show POS Receipt Logo")
    is_show_pos_global_receipt_logo = fields.Boolean("Show POS Global Receipt Logo")
    is_show_pos_receipt_logo = fields.Boolean("Show POS Receipt Logo")
    pos_receipt_logo_img = fields.Binary("Receipt Logo Image")
    

    


