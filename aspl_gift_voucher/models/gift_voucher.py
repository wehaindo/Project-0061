# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
# You should have received a copy of the License along with this program.
#################################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
import time


class ASPLGiftVoucher(models.Model):
    _name = 'aspl.gift.voucher'
    _description = 'Used to Store Gift Voucher.'
    _rec_name = 'voucher_code'
    _order = 'id desc'

    @api.model
    def create(self, vals):
        currentDate = date.today().strftime('%Y-%m-%d')
        if vals.get('expiry_date') and currentDate > vals.get('expiry_date'):
            raise UserError(_("Expiry Date should be grater than today date."))

        if vals.get('minimum_purchase') <= 0:
            raise UserError(_('Minimum purchase should not be less then 0 amount'))

        if vals.get('minimum_purchase') >= vals.get('voucher_amount'):
            sequence_code = self.random_cardno()
            vals.update({'voucher_code': sequence_code})
            res = super(ASPLGiftVoucher, self).create(vals)
            return res
        else:
            raise UserError(_("Minimum purchase amount can't be less then the voucher amount"))

    def random_cardno(self):
        return int(time.time())

    def write(self, vals):
        currentDate = date.today().strftime('%Y-%m-%d')
        if vals.get('expiry_date') and currentDate > vals.get('expiry_date'):
            raise UserError(_("Expiry Date should be grater than today date."))

        if (vals.get('minimum_purchase') or self.minimum_purchase) >= (
                vals.get('voucher_amount') or self.voucher_amount):
            vals.update({'minimum_purchase': vals.get('minimum_purchase') or self.minimum_purchase})
            res = super(ASPLGiftVoucher, self).write(vals)
        else:
            raise UserError(_("Minimum purchase amount can't be less then the voucher amount"))
        return res

    voucher_name = fields.Char(string="Name")
    voucher_code = fields.Char(string="Code", readonly=True)
    voucher_amount = fields.Float(string="Amount")
    minimum_purchase = fields.Float(string="Minimum Purchase")
    expiry_date = fields.Date(string="Expiry Date")
    redemption_order = fields.Integer(string="Redemption Order")
    redemption_customer = fields.Integer(string="Redemption Customer")
    is_active = fields.Boolean(string="Active", default=True)
    redeem_voucher_count = fields.Integer(string="Count", compute="_redeem_voucher_total_count")

    def _redeem_voucher_total_count(self):
        for each in self:
            each.redeem_voucher_count = self.env['aspl.gift.voucher.redeem'].search_count([
                ('voucher_id', '=', self.id)])

    def action_view_redeem_voucher(self):
        action = {
            'name': _('Redeem voucher'),
            'type': 'ir.actions.act_window',
            'res_model': 'aspl.gift.voucher.redeem',
            'target': 'current',
        }
        redeem_voucher_ids = self.env['aspl.gift.voucher.redeem'].search([
            ('voucher_id', '=', self.id)])
        action['view_mode'] = 'tree,form'
        action['domain'] = [('id', 'in', redeem_voucher_ids.ids)]
        return action

    _sql_constraints = [
        ('unique_name', 'UNIQUE(voucher_code)',
         'You can only add one time each Barcode.')
    ]


class ASPLGiftVoucherRedeem(models.Model):
    _name = 'aspl.gift.voucher.redeem'
    _description = 'Used to Store Gift Voucher Redeem History.'
    _rec_name = 'voucher_id'
    _order = 'id desc'

    voucher_id = fields.Many2one('aspl.gift.voucher', string="Voucher", readonly=True)
    voucher_code = fields.Char(string="Code", readonly=True)
    order_name = fields.Char(string="Order", readonly=True)
    order_amount = fields.Float(string="Order Amount", readonly=True)
    voucher_amount = fields.Float(string="Voucher Amount", readonly=True)
    used_date = fields.Datetime(string="Used Date", readonly=True, default=fields.Datetime.now(), store=True)
    user_id = fields.Many2one("res.users", string="Sales Person", readonly=True)
    customer_id = fields.Many2one("res.partner", string="Customer", readonly=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
