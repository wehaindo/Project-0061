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
from datetime import datetime
from uuid import uuid4
import pytz
import string
import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


import logging
_logger = logging.getLogger(__name__)



class PosConfig(models.Model):
    _inherit = 'pos.config'


    # Branch
    res_branch_id = fields.Many2one('res.branch')
    branch_name = fields.Char(string="Branch Name", store=True, related='res_branch_id.name')
