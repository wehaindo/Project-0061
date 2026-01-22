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
from odoo import models, fields, api


class PosDeposit(models.Model):
    _name = 'pos.deposit'
    _description = "POS Deposit Management"

    customer_id = fields.Many2one('res.partner', string='Customer')
    order_id = fields.Many2one('pos.order', string='Order')
    type = fields.Selection([('change', 'Change'), ('recharge', 'Recharge')], string="Type")
    debit = fields.Float("Debit")
    credit = fields.Float("Credit")
    cashier_id = fields.Many2one('res.users', string='Cashier')
