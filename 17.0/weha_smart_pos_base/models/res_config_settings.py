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
    is_set_control_button_position = fields.Boolean(related='pos_config_id.is_set_control_button_position', readonly=False)
    is_show_product_grid = fields.Boolean(related='pos_config_id.is_show_product_grid', readonly=False)
    is_max_orderline = fields.Boolean(related='pos_config_id.is_max_orderline', readonly=False)

    #Bag
    is_show_bag_charge = fields.Boolean(related='pos_config_id.is_show_bag_charge', readonly=False)
    bag_pos_category_id = fields.Many2one(related='pos_config_id.bag_pos_category_id', readonly=False)

    #Default Customer
    is_set_default_customer = fields.Boolean(related="pos_config_id.is_set_default_customer", readonly=False)
    customer_id = fields.Many2one(related="pos_config_id.customer_id", readonly=False)
    
    #Access Rights
    use_store_access_rights = fields.Boolean(related="pos_config_id.use_store_access_rights", readonly=False)
    supervisor_ids = fields.Many2many(related='pos_config_id.supervisor_ids', readonly=False)
    access_rights_refund = fields.Boolean(related="pos_config_id.access_rights_refund", readonly=False)
    access_rights_clear_order = fields.Boolean(related="pos_config_id.access_rights_clear_order", readonly=False)
    access_rights_del_orderline = fields.Boolean(related="pos_config_id.access_rights_del_orderline", readonly=False)

    #Item and Quantity Counter
    is_show_total_items = fields.Boolean(related="pos_config_id.is_show_total_items", readonly=False)
    is_show_total_quantity = fields.Boolean(related="pos_config_id.is_show_total_quantity", readonly=False)

    #Support Channel
    # support_channel_id = fields.Many2one(related="pos_config_id.support_channel_id", readonly=False)    
    support_channel_ids = fields.Many2many(related="pos_config_id.support_channel_ids", readonly=False)    


    #PouchDB
    is_save_pos_order_to_localdb = fields.Boolean(related="pos_config_id.is_save_pos_order_to_localdb", readonly=False)

    #Pos Deposit
    enable_deposit = fields.Boolean(related="pos_config_id.enable_deposit", readonly=False)
    deposit_product = fields.Many2one(related="pos_config_id.deposit_product", readonly=False)        

    #POS Voucher
    enable_voucher = fields.Boolean(related="pos_config_id.enable_voucher", readonly=False)
    voucher_account_id = fields.Many2one(related="pos_config_id.voucher_account_id", readonly=False)
    voucher_payment_method_id = fields.Many2one(related="pos_config_id.voucher_payment_method_id", readonly=False)

    #Payment Method Popup
    is_show_payment_method_popup = fields.Boolean(related="pos_config_id.is_show_payment_method_popup", readonly=False)
    