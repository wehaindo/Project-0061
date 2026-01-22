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
    use_combo = fields.Boolean('Use combo in POS')
    combo_pack_price = fields.Selection([('all_product', "Total of all combo items "), ('main_product', "Take Price from the Main product")], string='Total Combo Price', default='all_product')




    


