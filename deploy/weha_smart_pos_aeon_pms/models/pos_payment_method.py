# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    allow_pms_voucher = fields.Boolean("Allow For PMS Voucher")

    @api.constrains('allow_pms_voucher', 'split_transactions', 'journal_id')
    def _check_valid_method(self):
        for record in self:
            if record.allow_pms_voucher:
                # if not record.split_transactions:
                #     raise UserError(_('Please enable Identify Customer !'))
                if record.journal_id:
                    raise UserError(_('You can not select any journal in case of %s !') % record.name)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('config_jr'):
            if self._context.get('pos_payment_method_ids') and \
                    self._context.get('pos_payment_method_ids')[0] and \
                    self._context.get('pos_payment_method_ids')[0][2]:
                args += [['id', 'in', self._context.get('pos_payment_method_ids')[0][2]]]
            else:
                return False
        return super(PosPaymentMethod, self).name_search(name, args=args, operator=operator, limit=limit)