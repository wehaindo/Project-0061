from odoo import _, api, fields, exceptions, models


class ResBranch(models.Model):
    _inherit = 'res.branch'
    
    res_branch_supplier_ids = fields.One2many('res.branch.supplier','branch_id','Suppliers')

class ResBranchSupplier(models.Model):
    _name = 'res.branch.supplier'

    branch_id = fields.Many2one('res.branch', 'Branch #')
    partner_id = fields.Many2one('res.partner','Supplier')

    
