import logging
from odoo import models, fields


_logger = logging.getLogger(__name__)


class BusinessUnit(models.Model):
    """res branch"""
    _name = "business.unit"
    _description = 'Branch Business Unit'
    _order = 'name'

    def name_get(self):
        result = []            
        for rec in self:
            result.append((rec.id, '(%s) %s' % (rec.code,rec.name)))
        return result

    name = fields.Char(string='Bussines Unit', required=True,)
    code = fields.Integer(
        string='Code',
    )
    description = fields.Char(string='Description', required=True,)
    company_id = fields.Many2one('res.company', required=True, string='Company')