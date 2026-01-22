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
    use_pos_data_speed_up = fields.Boolean(related="pos_config_id.use_pos_data_speed_up", readonly=False)
    # direct_pos_data_local_products_db = fields.Boolean(related="pos_config_id.direct_pos_data_local_products_db", readonly=False)
    save_pos_order = fields.Boolean(related="pos_config_id.save_pos_order", readonly=False)

