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

class PosOrder(models.Model):
    _inherit = 'pos.order'

    #Branch
    branch_id = fields.Many2one('res.branch', related='session_id.branch_id', string='Branch', help='Branches allowed', store=True)
    
