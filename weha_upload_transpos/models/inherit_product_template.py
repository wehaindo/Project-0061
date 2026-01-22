from odoo import models, fields, api, exceptions, _


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    # active = fields.Boolean('active')

    def archive(self):
        vals = {}
        vals.update({'active': False})
        self.write(vals)