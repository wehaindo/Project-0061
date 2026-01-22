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

    #Admin
    use_pos_data_speed_up = fields.Boolean('User POS Data Speed Up')
    direct_pos_data_local_products_db = fields.Boolean('Direct Local Products DB')
    # pos_data_speed_up_method = fields.Selection([('normal','Normal'),('couchdb','CouchDB'),('pouchdb','PouchDB')], 'Speed Up Method', default='normal')
    save_pos_order = fields.Boolean('Save POS Order Locally')
    branch_code = fields.Char(related='res_branch_id.code')



    


