from odoo import fields, models
from odoo.exceptions import UserError, ValidationError


class WehaPurchaseApprovalRule(models.Model):
    _name = 'weha.purchase.approval.rule'
    _description = 'Purchase Approval Rule'

    _rec_name = 'res_partner_id'
    # _order = 'name ASC'

    
    approval_rule_seq = fields.Integer(
        string='Approval Rule Seq',
    )
    
    res_partner_id = fields.Many2one(
        string='User',
        comodel_name='res.partner',
        ondelete='restrict',
    )
    
    next_approval_id = fields.Many2one(
        string='Next Approval',
        comodel_name='weha.purchase.approval.rule',
        ondelete='restrict',
    )
    
    mail_tamplate_id = fields.Many2one(
        string='Mail Template',
        comodel_name='mail.template',
        ondelete='restrict',
    )
    