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

    #Admin
    is_set_control_button_position = fields.Boolean('Set Control Button Position', default=True)
    is_show_product_grid = fields.Boolean('Show Product Grid', default=False)
    is_max_orderline = fields.Boolean('Max Orderline Screen', default=False)

    #Bag
    is_show_bag_charge = fields.Boolean('Show Bag Charge')
    bag_pos_category_id = fields.Many2one('pos.category', string="Bag Product Category")

    #Default Customer
    is_set_default_customer = fields.Boolean("Set POS Default Customer")
    customer_id = fields.Many2one('res.partner', string="Default Customer")

    #Access Rights
    use_store_access_rights = fields.Boolean("Store Rights")
    supervisor_ids = fields.Many2many('hr.employee', 'pos_config_hr_employee_supervisor_rel', 'pos_config_id', 'res_users_id', 'Supervisors')    
    access_rights_refund = fields.Boolean('Access Rights Refund', default=True)
    access_rights_clear_order = fields.Boolean('Access Rights Clear Order', default=True)
    access_rights_del_orderline = fields.Boolean('Access Rights Delete Orderline', default=True)

    #Item and Quantity Counter
    is_show_total_items = fields.Boolean(string="Total Items", default=False)
    is_show_total_quantity = fields.Boolean(string="Total Quantity", default=False)


    #Support Channel
    # support_channel_id = fields.Many2one('discuss.channel', 'Support Channel')    
    support_channel_ids = fields.Many2many('discuss.channel', 'pos_config_discuss_channel_rel', 'pos_config_id', 'discuss_channel_id', 'Supervisors')    

    #Pull and Sync Data
    last_write_date = fields.Datetime('Last Update')

    @api.model
    def prepare_sync_data(self, pos_config_id):
        pos_config = self.env['pos.config'].browse(pos_config_id)
        domain = [
            ('write_date', '>=',  pos_config.last_write_date)
        ]
        product_template_ids = self.env['product.template'].search(domain)        
        domain = [
            ('product_tmpl_id', 'in', product_template_ids.ids)
        ]
        params = self.env['pos.session']._loader_params_product_product()
        params['search_params']['domain'] = domain
        products = self.env['product.product'].with_context(active_test=False).search_read(**params['search_params'])
        if len(products) > 0:
            self.env['pos.session']._process_pos_ui_product_product(products)
        pos_config.last_write_date = datetime.now()
        return products

    #PouchDB
    is_save_pos_order_to_localdb = fields.Boolean('Save POS Order To localDB')

    #Direct Login
    def open_fast_login(self):
        self.ensure_one()
        domain = [
            ('state','in',['opening_control','opened','closing_control']),
            ('user_id','=', self.env.uid),
            ('config_id','=', self.id)
        ]
        pos_session_id = self.env['pos.session'].search(domain, limit=1)
        if not pos_session_id:
            self._check_before_creating_new_session()
        self._validate_fields(self._fields)
    
        # check if there's any product for this PoS
        # domain = [('available_in_pos', '=', True)]
        # if self.limit_categories and self.iface_available_categ_ids:
        #     domain.append(('pos_categ_id', 'in', self.iface_available_categ_ids.ids))
        # if not self.env['product.product'].search(domain):
        #     return {
        #         'name': _("There is no product linked to your PoS"),
        #         'type': 'ir.actions.act_window',
        #         'view_type': 'form',
        #         'view_mode': 'form',
        #         'res_model': 'pos.session.check_product_wizard',
        #         'target': 'new',
        #         'context': {'config_id': self.id}
        #     }

        return self._action_to_open_ui()

    def _action_to_open_ui(self):
        domain = [
            ('state','in',['opening_control','opened','closing_control']),
            ('user_id','=', self.env.uid),
            ('config_id','=', self.id)
        ]
        pos_session_id = self.env['pos.session'].search(domain, limit=1)
        if not pos_session_id:
            _logger.info("Session not found then create new session")
            self.env['pos.session'].create({'user_id': self.env.uid, 'config_id': self.id})
        else:
            _logger.info("Session found then continue with current session")
   
    def generate_code(self):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))  
        self.pos_config_code = code

    pos_config_code = fields.Char('Code #', size=20)

    #POS Deposit
    enable_deposit = fields.Boolean('Enable Deposit')
    deposit_product = fields.Many2one('product.product', string="Deposit Product")    

    #POS Voucher
    enable_voucher = fields.Boolean(string='Voucher')
    voucher_account_id = fields.Many2one("account.account","Account")
    voucher_payment_method_id = fields.Many2one("pos.payment.method", "Payment Method")

    #Payment Method Popup
    is_show_payment_method_popup = fields.Boolean('Show Payment Method Popup')
    

    @api.model
    def create(self, vals):
        res = super(PosConfig, self).create(vals)
        res.generate_code()
        return res

    def write(self, vals):
        super(PosConfig, self).write(vals)
        if not self.pos_config_code:
            self.generate_code()    


    