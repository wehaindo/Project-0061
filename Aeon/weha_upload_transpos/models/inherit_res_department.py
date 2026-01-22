from odoo import models, fields, api, exceptions, _


class InheritResDepartment(models.Model):
    _inherit = 'res.department'

    code = fields.Char(string='Code',)
    active = fields.Boolean('active')
    # group_id = fields.Many2one('res.group', required=False)
    # division_id = fields.Many2one('res.division', required=False)

    def archive(self):
        vals = {}
        vals.update({'active': False})
        self.write(vals)