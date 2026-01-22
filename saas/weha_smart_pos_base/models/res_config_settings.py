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

    #Order Refund
    is_show_refund_button = fields.Boolean(related='pos_config_id.is_show_refund_button', readonly=False)

    #POS Security
    use_store_access_rights = fields.Boolean(related="pos_config_id.use_store_access_rights", readonly=False)
    supervisor_ids = fields.Many2many(related='pos_config_id.supervisor_ids', readonly=False)

    #Bag Charge
    is_show_bag_charge = fields.Boolean(related='pos_config_id.is_show_bag_charge', readonly=False)
    bag_pos_category_id = fields.Many2one(related='pos_config_id.bag_pos_category_id', readonly=False)

    #Receipt Logo
    is_show_receipt_logo = fields.Boolean(related="pos_config_id.is_show_receipt_logo", readonly=False)
    is_show_pos_global_receipt_logo = fields.Boolean(related="pos_config_id.is_show_pos_global_receipt_logo", readonly=False)
    pos_global_receipt_logo_img = fields.Binary(related="company_id.pos_global_receipt_logo_img", readonly=False)
    is_show_pos_receipt_logo = fields.Boolean(related="pos_config_id.is_show_pos_receipt_logo", readonly=False)
    pos_receipt_logo_img = fields.Binary(related="pos_config_id.pos_receipt_logo_img", readonly=False)
    