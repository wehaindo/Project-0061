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
    is_allow_delete_unpaid_order = fields.Boolean('Allow Delete Unpaid Order')
    is_allow_delete_paid_order = fields.Boolean('Allow Delete Paid Order')
    is_allow_export_unpaid_order = fields.Boolean('Allow Export Unpaid Order')
    is_allow_export_paid_order = fields.Boolean('Allow Export Paid Order')
    is_allow_import_order = fields.Boolean('Allow Import Order')



    


