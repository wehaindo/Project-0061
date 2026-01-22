from odoo import models, fields, api, exceptions, _


class InheritUom(models.Model):
    _inherit = 'uom.uom'

    code = fields.Char(string='Code',)
    active = fields.Boolean('active')
    

    
