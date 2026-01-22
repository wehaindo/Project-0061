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
    is_set_control_button_position = fields.Boolean('Set Control Button Position')
    is_show_product_grid = fields.Boolean('Show Product Grid', default=False)




    


