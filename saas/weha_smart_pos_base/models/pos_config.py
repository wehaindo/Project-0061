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

class PosConfig(models.Model):
    _inherit = 'pos.config'

    def send_message(self):
        return {
            'name': _("Send Message"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.send.message',
            'target': 'new',
            'context': {'config_id': self.id}
        }

    #Admin
    is_set_control_button_position = fields.Boolean('Set Control Button Position')
    is_show_product_grid = fields.Boolean('Show Product Grid', default=False)

    #Payment
    is_only_one_payment_line = fields.Boolean('Set Only One Payment Line', default=True)

    #Data Backup
    is_backup_order_to_localstorage =  fields.Boolean('Backup Order to LocalStorage', default=False)

    #Order Refund
    is_show_refund_button = fields.Boolean('Show Refund Button')

    #POS Security
    use_store_access_rights = fields.Boolean("Store Rights")
    supervisor_ids = fields.Many2many('res.users','pos_base_res_users','supervisor_id','user_id','Supervisors')        

    #Bag Charge
    is_show_bag_charge = fields.Boolean('Show Bag Charge')
    bag_pos_category_id = fields.Many2one('pos.category', string="Bag Product Category")

    #Receipt Logo
    is_show_receipt_logo = fields.Boolean("Show POS Receipt Logo")
    is_show_pos_global_receipt_logo = fields.Boolean("Show POS Global Receipt Logo")
    is_show_pos_receipt_logo = fields.Boolean("Show POS Receipt Logo")
    pos_receipt_logo_img = fields.Binary("Receipt Logo Image")
    

