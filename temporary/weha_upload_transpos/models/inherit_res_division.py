from odoo import models, fields, api, exceptions, _


class InheritResDivision(models.Model):
    _inherit = 'res.division'

    active = fields.Boolean('active')

    def archive(self):
        vals = {}
        vals.update({'active': False})
        self.write(vals)