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
from odoo import api, models, fields, registry
import logging

_logger = logging.getLogger(__name__)

class PosBranch(models.Model):
    _name = "pos.branch"
    _description = "Branch of shops"

    name = fields.Char('Name', required=1)
    user_id = fields.Many2one('res.users', 'Manager User', required=1)
    user_ids = fields.Many2many('res.users', 'pos_branch_res_users_rel', 'branch_id', 'user_id', string='POS Users')
    config_ids = fields.One2many('pos.config', 'pos_branch_id', string='POS Configs', readonly=1)