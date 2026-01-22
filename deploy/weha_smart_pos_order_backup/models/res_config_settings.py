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


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    #Admin
    is_allow_delete_unpaid_order = fields.Boolean(related='pos_config_id.is_allow_delete_unpaid_order', readonly=False)
    is_allow_delete_paid_order = fields.Boolean(related='pos_config_id.is_allow_delete_paid_order', readonly=False)
    is_allow_export_unpaid_order = fields.Boolean(related='pos_config_id.is_allow_export_unpaid_order', readonly=False)
    is_allow_export_paid_order = fields.Boolean(related='pos_config_id.is_allow_export_paid_order', readonly=False)
    is_allow_import_order = fields.Boolean(related='pos_config_id.is_allow_import_order', readonly=False)
