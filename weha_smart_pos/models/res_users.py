from odoo import models, fields, api
import uuid


class ResUsers(models.Model):
    _inherit = 'res.users'

    couch_id = fields.Char('Couch ID', size=100)

    @api.model
    def create(self, vals):
        vals['couch_id'] = str(uuid.uuid4())
        return super(ResUsers, self).create(vals)


    def write(self, vals):
        if not self.couch_id:
            vals['couch_id'] = str(uuid.uuid4())
        return super(ResUsers, self).write(vals)