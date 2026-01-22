import logging
from odoo import models, fields


_logger = logging.getLogger(__name__)


class ResLine(models.Model):
    """res branch"""
    _name = "res.line"
    _description = 'Line'
    _order = 'name'

    def name_get(self):
        result = []            
        for rec in self:
            result.append((rec.id, '(%s) %s' % (rec.code,rec.name)))
        return result


    name = fields.Char(string='Line', required=True,)
    code = fields.Integer(string='Code',)
    code1 = fields.Char('Code', size=20)
    description = fields.Char(string='Description', required=True,)