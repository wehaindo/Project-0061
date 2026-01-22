import logging
from odoo import models, fields


_logger = logging.getLogger(__name__)


class ResDivision(models.Model):
    """res branch"""
    _name = "res.division"
    _description = 'Division'
    _order = 'name'

    def name_get(self):
        result = []            
        for rec in self:
            result.append((rec.id, '(%s) %s' % (rec.code,rec.name)))
        return result                     

    name = fields.Char(string='Division', required=True,)
    code = fields.Integer(string='Code')    
    code1 = fields.Char('Code', size=20, required=True)
    description = fields.Char(string='Description', required=True,)
    line_id = fields.Many2one(
        string='Line',
        comodel_name='res.line',
        ondelete='restrict',
    )
    