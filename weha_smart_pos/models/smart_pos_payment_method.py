from odoo import models, fields, api
import uuid


class SmartPosPaymentMethod(models.Model):
    _name = 'smart.pos.payment.method'

    name = fields.Char('Name', size=100, required=True)
    couch_id = fields.Char('Couch ID', size=100)
    code = fields.Char('Code', size=4, required=True)
    type = fields.Selection([('cash','Cash'),('bank','Bank'),('wallet','Wallet'),('voucher','Voucher'),('point','Point')], 'Type', default='cash', required=True)


    @api.model
    def create(self, vals):
        vals['couch_id'] = str(uuid.uuid4())
        return super(SmartPosPaymentMethod, self).create(vals)


    def write(self, vals):
        if not self.couch_id:
            vals['couch_id'] = str(uuid.uuid4())
        return super(SmartPosPaymentMethod, self).write(vals)