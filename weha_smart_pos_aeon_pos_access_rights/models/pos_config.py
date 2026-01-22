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

class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    supervisor_ids = fields.Many2many(related='res_branch_id.supervisor_ids')
    use_store_access_rights = fields.Boolean("Store Rights")
    


