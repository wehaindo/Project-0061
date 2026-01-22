from odoo import models, fields, api
import uuid


class SmartPosProductCategory(models.Model):
    _name = 'smart.pos.product.category'

    name = fields.Char("Name", size=200, required=True)
    code = fields.Char("Code", size=4, required=True)
    couch_id = fields.Char('Couch ID', size=100)

    @api.model
    def create(self, vals):
        vals['couch_id'] = str(uuid.uuid4())
        return super(SmartPosProductCategory, self).create(vals)


    def write(self, vals):
        if not self.couch_id:
            vals['couch_id'] = str(uuid.uuid4())
        return super(SmartPosProductCategory, self).write(vals)