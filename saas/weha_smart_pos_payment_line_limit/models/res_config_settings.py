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
    is_set_control_button_position = fields.Boolean(related='pos_config_id.is_set_control_button_position', reaonly=False)
    is_show_product_grid = fields.Boolean(related='pos_config_id.is_show_product_grid', readonly=False)

    #Payment
    is_only_one_payment_line = fields.Boolean(related='pos_config_id.is_only_one_payment_line', readonly=False)
    
    #Data Backup
    is_backup_order_to_localstorage =  fields.Boolean(related='pos_config_id.is_backup_order_to_localstorage', readonly=False)