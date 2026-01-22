# -- coding: utf-8 --
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from odoo import models, fields
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _get_split_receivable_vals(self, payment, amount, amount_converted):
        accounting_partner = self.env["res.partner"]._find_accounting_partner(payment.partner_id)
        if not accounting_partner:
            raise UserError(_("You have enabled the \"Identify Customer\" option for %s payment method,"
                              "but the order %s does not contain a customer.") % (payment.payment_method_id.name,
                                                                                  payment.pos_order_id.name))
        partial_vals = {
            'account_id': accounting_partner.property_account_receivable_id.id,
            'move_id': self.move_id.id,
            'partner_id': accounting_partner.id,
            'name': '%s - %s' % (self.name, payment.payment_method_id.name),
        }
        if payment.payment_method_id.allow_for_gift_voucher:
            partial_vals.update({'account_id': self.config_id.gift_voucher_account_id.id})
        return self._debit_amounts(partial_vals, amount, amount_converted)

    def _get_combine_receivable_vals(self, payment_method, amount, amount_converted):
        partial_vals = {
            'account_id': self._get_receivable_account(payment_method).id,
            'move_id': self.move_id.id,
            'name': '%s - %s' % (self.name, payment_method.name)
        }
        if payment_method.allow_for_gift_voucher:
            partial_vals.update({'account_id': self.config_id.gift_voucher_account_id.id})
        return self._debit_amounts(partial_vals, amount, amount_converted)

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if self.config_id.enable_gift_voucher:
            result.append('aspl.gift.voucher')
            result.append('pos.payment.method')
        return result

    def _loader_params_pos_payment_method(self):
        res = {
            'search_params': {
                'fields': ['id', 'is_cash_count', 'name', 'journal_id', 'allow_for_gift_voucher'],
            },
        }
        return res

    def _loader_params_aspl_gift_voucher(self):
        rec = {
            'search_params': {
                'domain': [('is_active', '=', 'true')],
                'fields': ['id', 'voucher_name', 'voucher_amount', 'minimum_purchase', 'expiry_date',
                           'redemption_order',
                           'redemption_customer', 'voucher_code', 'is_active'],
            },
        }
        return rec

    def _get_pos_ui_aspl_gift_voucher(self, params):
        return self.env['aspl.gift.voucher'].search_read(**params['search_params'])

    def _get_pos_ui_pos_payment_method(self, params):
        return self.env['pos.payment.method'].search_read(**params['search_params'])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
