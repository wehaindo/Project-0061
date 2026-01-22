# -*- coding: utf-8 -*-
import string
import random
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GiftVoucherPos(models.Model):
    _name = 'gift.voucher.pos'

    name = fields.Char(string="Name", required=True)
    voucher_type = fields.Selection(
        selection=[
            ('product', 'Product'),
            ('category', 'POS Category'),
            ('all', 'All Products'),
        ], string="Applicable on ", default='product'
    )
    product_id = fields.Many2one('product.product', string="Product")
    product_categ = fields.Many2one('pos.category', string="Product Category")
    min_value = fields.Integer(string="Minimum Voucher Value", required=True)
    max_value = fields.Integer(string="Maximum Voucher Value", required=True)
    expiry_date = fields.Date(string="Expiry Date", required=True, help='The expiry date of Voucher.')


class GiftCouponPos(models.Model):
    _name = 'gift.coupon.pos'

    def get_code(self):
        size = 7
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(size))

    _sql_constraints = [
        ('name_uniq', 'unique (code)', "Code already exists !"),
    ]

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", default=get_code)
    voucher = fields.Many2one('gift.voucher.pos', string="Voucher", required=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    partner_id = fields.Many2one('res.partner', string="Limit to a Single Partner", help='Limit to a Single Partner')
    limit = fields.Integer(string="Total Available For Each User", default=1, help='Total Available For Each User')
    total_avail = fields.Integer(string="Total Available", default=1)

    voucher_val = fields.Float(string="Voucher Value", help='The amount for the voucher.')
    type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage'),
        ], store=True, default='fixed')

    @api.onchange('voucher_val')
    def check_val(self):
        if self.voucher_val > self.voucher.max_value or self.voucher_val < self.voucher.min_value:
            raise UserError(_("Please check the voucher value"))


class CouponPartnerPos(models.Model):
    _name = 'partner.coupon.pos'

    partner_id = fields.Many2one('res.partner', string="Partner")
    coupon_pos = fields.Char(string="Coupon Applied")
    number_pos = fields.Integer(string="Number of Times Used")

    def update_history(self, vals):
        if vals:
            h_obj = self.env['partner.coupon.pos']
            history = h_obj.search([('coupon_pos', '=', vals['coupon_pos']),('partner_id', '=', vals['partner_id'])], limit=1)
            coupon = self.env['gift.coupon.pos'].search([('code', '=', vals['coupon_pos'])], limit=1)
            if history:
                history.number_pos += 1
                coupon.total_avail -= 1
            else:
                coupon.total_avail -= 1
                rec = {
                    'partner_id': vals['partner_id'],
                    'number_pos': 1,
                    'coupon_pos': vals['coupon_pos']
                }
                h_obj.create(rec)
            return True


class PartnerExtendedPos(models.Model):
    _inherit = 'res.partner'

    applied_coupon_pos = fields.One2many('partner.coupon.pos', 'partner_id', string="Coupons Applied From POS")
