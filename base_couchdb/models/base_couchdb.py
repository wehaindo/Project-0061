from odoo import _, api, fields, models
import uuid

class BaseCouchdb(models.AbstractModel):
    _name = "base.couchdb"
    _description = "Couchdb Relation (abstract)"

    couch_id = fields.Char('Couch ID', size=100, readonly=True)

    @api.model
    def create(self, vals):
        vals['couch_id'] = str(uuid.uuid4())
        return super(BaseCouchdb, self).create(vals)

    def write(self, vals):
        if not self.couch_id:
            vals['couch_id'] = str(uuid.uuid4())
        return super(BaseCouchdb, self).write(vals)