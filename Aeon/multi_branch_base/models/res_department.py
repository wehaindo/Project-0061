import logging
from odoo import models, fields


_logger = logging.getLogger(__name__)


class ResDepartment(models.Model):
    """res branch"""
    _name = "res.department"
    _description = 'Department'
    _order = 'name'

    def name_get(self):
        result = []            
        for rec in self:
            result.append((rec.id, '(%s) %s' % (rec.code,rec.name)))
        return result


    name = fields.Char(string='Department', required=True)
    code = fields.Integer(string='Code', required=True)
    description = fields.Char(string='Description', required=False)
    group_id = fields.Many2one(
        string='Group',
        comodel_name='res.group',
        ondelete='restrict',
        required=True
    )
    