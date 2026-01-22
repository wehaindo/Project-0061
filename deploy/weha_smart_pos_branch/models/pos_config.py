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
    pos_branch_id = fields.Many2one(
        'pos.branch',
        'Branch',
        help='If you set branch here, only users have assigned of branch will see this pos config \n'
             'All products have branch the same with this branch will display in pos screen\n'
             'All pos category have branch the same with this branch will display in pos screen'
    )

    


