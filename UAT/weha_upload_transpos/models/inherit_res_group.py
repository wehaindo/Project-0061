from odoo import models, fields, api, exceptions, _


class InheritResGroup(models.Model):
    _inherit = 'res.group'

    code = fields.Char(string='Code',)
    active = fields.Boolean('active')

    def archive(self):
        vals = {}
        vals.update({'active': False})
        self.write(vals)