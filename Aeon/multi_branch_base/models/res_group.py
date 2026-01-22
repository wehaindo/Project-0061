import logging
from odoo import models, fields


_logger = logging.getLogger(__name__)


class ResGroup(models.Model):
    """res branch"""
    _name = "res.group"
    _description = 'Group'
    _order = 'name'

    def name_get(self):
        result = []            
        for rec in self:
            result.append((rec.id, '(%s) %s' % (rec.code,rec.name)))
        return result

    name = fields.Char(string='Group', required=True,)
    code = fields.Integer(string='Code',required=True)
    description = fields.Char(string='Description', required=False)
    division_id = fields.Many2one(
        string='Division',
        comodel_name='res.division',
        ondelete='restrict',
    )
    