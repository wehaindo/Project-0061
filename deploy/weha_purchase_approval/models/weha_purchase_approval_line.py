from odoo import fields, models
from odoo.exceptions import UserError, ValidationError


class WehaPurchaseApprovalLine(models.Model):
    _name = 'weha.purchase.approval.line'
    _description = 'Purchase Approval Line'

    # _rec_name = 'name'
    # _order = 'name ASC'

    res_partner_id = fields.Many2one(
        string='res partner',
        comodel_name='res.partner',
        ondelete='restrict',
    )
    is_approve = fields.Boolean(
        string='is_approve',
    )
    
    

    
