from odoo import models, fields, api


class ProductTemplate(models.Model):
    """inherited product"""
    _inherit = 'product.template'

    
    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
        ondelete='restrict',
        required=False
    )
    agreement_contract_id = fields.Many2one(
        string='Agreement Contract',
        comodel_name='agreement.contract',
        ondelete='restrict',
        required=False
    )
    
    