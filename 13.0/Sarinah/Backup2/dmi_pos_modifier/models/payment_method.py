# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    is_note = fields.Boolean('Note', default=False)

    def update_note(self):
        for res in self:
            self.env.cr.execute(
                "UPDATE pos_payment_method SET is_note = %s WHERE id = %s",
                (not res.is_note, res.id)
            )

class PosPayment(models.Model) :
    _inherit = 'pos.payment'

    memo = fields.Char('Appr Code / Reff No' , default='')
