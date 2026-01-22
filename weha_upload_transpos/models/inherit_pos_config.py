from odoo import models, fields, api, exceptions, _


class InheritPosConfig(models.Model):
    _inherit = 'pos.config'

    code = fields.Char(string='Code',)

    

    
