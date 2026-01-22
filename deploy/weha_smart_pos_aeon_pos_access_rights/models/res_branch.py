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

class ResBranch(models.Model):
    _inherit = 'res.branch'

    supervisor_ids = fields.Many2many('res.users', 'res_branch_res_users_supervisor_rel', 'res_branch_id', 'res_users_id', 'Supervisors')
