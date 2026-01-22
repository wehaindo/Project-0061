from odoo import _, api, fields, models, tools
import uuid

class ResPartner(models.Model):
    _inherit = 'res.partner'

    couch_id = fields.Char('Couch ID', size=100)
    barcode = fields.Char('Barcode', size=50)
    
    wallet_ids = fields.One2many('smart.pos.wallet','customer_id', 'Wallets')


    @api.model
    def create(self, vals):
        vals['couch_id'] = str(uuid.uuid4())
        return super(ResPartner, self).create(vals)

    def write(self, vals):
        if not self.couch_id:
            vals['couch_id'] = str(uuid.uuid4())
        return super(ResPartner, self).write(vals)

