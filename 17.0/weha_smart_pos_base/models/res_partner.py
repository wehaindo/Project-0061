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
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    # POS Deposit
    @api.depends('deposit_lines')
    def _calc_remaining(self):
        for row in self:
            total = 0.00
            for line in row.deposit_lines:
                if line.state == 'done':
                    total += line.credit - line.debit
            row.remaining_deposit_amount = total

    #POS Loyatly
    def get_customer_point(self):
        for row in self:
            row.point_total = 0

    #POS Deposit
    deposit_lines = fields.One2many('pos.deposit', 'customer_id', string="Deposits", readonly=True)
    remaining_deposit_amount = fields.Float(compute="_calc_remaining", string="Remaining Amount", readonly=True, store=False)
    add_change_deposit = fields.Boolean('Add Change to Deposit')
    card_number = fields.Char("Card Number", size=100)
    # POS Voucher
    # pos_voucher_ids = fields.One2many('pos.voucher','customer_id','Vouchers')
    #POS Loyalty
    point_total = fields.Integer('Point', compute="get_customer_point")



class ResPartnerPoint(models.Model):
    _name = 'res.partner.point'
    _description = 'Customer Point Loyalty'

    name = fields.Char('Name', size=100)    
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)    
    type = fields.Selection([('add', 'Add'),('deduct','Deduct'),('adjust','Adjustment')], string="Type", required=True, default="add")
    point = fields.Integer("Point")    
    state = fields.Selection([('done','Close'),('cancel','Cancel')], 'Status', default="done")
