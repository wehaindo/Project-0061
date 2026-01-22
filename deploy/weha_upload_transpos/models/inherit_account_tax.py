from odoo import models, fields, api, exceptions, _


class InheritAccountTax(models.Model):
    _inherit = 'account.tax'

    code = fields.Char(string='Code',)
    tax_type = fields.Selection([('ppn', 'PPN'), ('pb1','PB1')], string='IDN Tax Type', default='ppn')
    active = fields.Boolean('active')
    

    
