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
from odoo.exceptions import UserError
from datetime import datetime, date
import time
from random import randint



class PosVoucherOrder(models.Model):
    _name = 'pos.voucher.order'
    _description = 'Manage Voucher Order for Point of Sale'
    
    def create_pos_voucher_sequence(self):
        company_id = self.env.company.id
        result = self.env['ir.sequence'].sudo().create({
                'name': _("Voucher Order Sequence"),
                'padding': 5,
                'code': f'pos.voucher.order.{self.name}',
                'number_next': 1,
                'number_increment': 1,
                'company_id': company_id,
            })

        self.voucher_sequence = result      

    def action_generate_voucher(self):
        for i in range(self.voucher_count):
            vals = {
                'voucher_seq': self.voucher_sequence.next_by_id(),
                'pos_voucher_order_id': self.id,
                'voucher_amount': self.voucher_amount,
                'minimum_purchase': 0,
                'expiry_date': self.expiry_date
            }
            self.env['pos.voucher'].create(vals)

    name = fields.Char('Name', size=100)
    customer_id = fields.Many2one("res.partner", string="Customer", readonly=True)
    description= fields.Char('Description', size=250)
    date_order = fields.Datetime('Date', default=datetime.now())
    voucher_type = fields.Selection(
        [('physical','Physical'),('electronic','Electronic')],
        'Type',
        default='physical'
    )
    voucher_prefix = fields.Char('Voucher Prefix', size=3)
    voucher_sequence = fields.Many2one('ir.sequence', 'Voucher Sequence', readonly=True)
    voucher_amount = fields.Float('Voucher Amount', default=0.0)
    voucher_count = fields.Integer('Voucher Count', default=1)
    minimum_purchase = fields.Float(string="Minimum Purchase")
    expiry_date = fields.Date(string="Expiry Date")
    state = fields.Selection(
        [('draft','New'),('open','Open'),('done','Complete')],
        'Status',
        default='draft'
    )
    pos_voucher_ids = fields.One2many('pos.voucher','pos_voucher_order_id','Vouchers')

    @api.model
    def create(self, vals):
        currentDate = date.today().strftime('%Y-%m-%d')
        if vals.get('expiry_date') and currentDate > vals.get('expiry_date'):
            raise UserError(_("Expiry Date should be grater than today date."))

        # if vals.get('minimum_purchase') < 0:
        #     raise UserError(_('Minimum purchase should not be less then 0 amount'))

        vals['name'] = self.env['ir.sequence'].next_by_code('pos.voucher.order') or _("New")
        result = super(PosVoucherOrder,self).create(vals)
        result.create_pos_voucher_sequence()
        return result

    def write(self, vals):
        currentDate = date.today().strftime('%Y-%m-%d')
        if vals.get('expiry_date') and currentDate > vals.get('expiry_date'):
            raise UserError(_("Expiry Date should be grater than today date."))
    
        super(PosVoucherOrder, self).write(vals)


class PosVoucher(models.Model):
    _name = 'pos.voucher'
    _description = 'Manage Voucher for Point of sale'
    _order = 'id desc'

    def _redeem_voucher_total_count(self):
        for each in self:
            each.redeem_voucher_count = self.env['pos.voucher.redeem'].search_count([
                ('pos_voucher_id', '=', self.id)])

    def action_view_redeem_voucher(self):
        action = {
            'name': _('Redeem voucher'),
            'type': 'ir.actions.act_window',
            'res_model': 'aspl.gift.voucher.redeem',
            'target': 'current',
        }
        redeem_voucher_ids = self.env['pos.voucher.redeem'].search([
            ('pos_voucher_id', '=', self.id)])
        action['view_mode'] = 'tree,form'
        action['domain'] = [('id', 'in', redeem_voucher_ids.ids)]
        return action

    def random_with_N_digits(self, n):
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return randint(range_start, range_end)

    def random_cardno(self):
        return str(int(time.time()))

    def action_set_open(self):
        for row in self:
            row.state = 'open'
        
    pos_voucher_order_id = fields.Many2one('pos.voucher.order', 'Voucher Order', ondelete='set null')
    name = fields.Char(string="Name")
    voucher_seq = fields.Char('Voucher Sequence', readonly=False)
    voucher_code = fields.Char(string="Code", readonly=False)
    voucher_amount = fields.Float(string="Amount")
    minimum_purchase = fields.Float(string="Minimum Purchase")
    expiry_date = fields.Date(string="Expiry Date")
    redemption_order = fields.Integer(string="Redemption Order")
    redemption_customer = fields.Integer(string="Redemption Customer")
    is_active = fields.Boolean(string="Active", default=True)
    redeem_voucher_count = fields.Integer(string="Count", compute="_redeem_voucher_total_count")
    state= fields.Selection(
        [
            ('draft','New'),
            ('open','Open'),
            ('used','Used'),
            ('damage','Damage'),
        ],
        'Status',
        default='draft'
    )

    @api.model
    def create(self, vals):       
        sequence_code = self.random_with_N_digits(12)
        vals.update({'voucher_code': sequence_code})
        res = super(PosVoucher, self).create(vals)
        return res

    def write(self, vals):       
        # vals.update({'minimum_purchase': vals.get('minimum_purchase') or self.minimum_purchase})
        res = super(PosVoucher, self).write(vals)
        return res
    
    _sql_constraints = [
        ('unique_name', 'UNIQUE(voucher_code)',
         'You can only add one time each Barcode.')
    ]


class PosVoucherRedeem(models.Model):
    _name = 'pos.voucher.redeem'
    _description = 'Pos Voucher Redeem Transaction'
    _rec_name = 'pos_voucher_id'
    _order = 'id desc'

    pos_voucher_id = fields.Many2one('pos.voucher', string="Voucher", readonly=True)
    voucher_code = fields.Char(string="Code", readonly=True)
    order_name = fields.Char(string="Order", readonly=True)
    order_amount = fields.Float(string="Order Amount", readonly=True)
    voucher_amount = fields.Float(string="Voucher Amount", readonly=True)
    used_date = fields.Datetime(string="Used Date", readonly=True, default=fields.Datetime.now(), store=True)
    user_id = fields.Many2one("res.users", string="Sales Person", readonly=True)
    customer_id = fields.Many2one("res.partner", string="Customer", readonly=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
