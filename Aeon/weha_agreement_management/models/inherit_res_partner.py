from email.policy import default
from odoo import _, api, fields, models
from datetime import datetime, timedelta, date


class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    parent_supplier_id = fields.Many2one(
        string='Parent',
        comodel_name='res.partner',
        ondelete='restrict',
    )
    reg_number = fields.Char(string="Registration Number")
    code_siup = fields.Char(
        string='SIUP',
    )
    supplier_code = fields.Char(
        string='Supplier Code',
    )
    supplier_contract_type = fields.Selection(
        string='Supplier Contract Type',
        selection=[('general', 'General Yearly Contract Form'), ('ab', 'Form A & B')],
        default='general'
    )
    supplier_sub_type = fields.Selection(
        string='Supplier Sub-Type',
        selection=[('consignment', 'Consignment'), ('outright', 'Outright')]
    )
    supplier_type = fields.Selection(
        string='Supplier Type',
        selection=[('trade', 'Trade'), ('nontrade', 'Non-trade')]
    )
    supplier_source = fields.Selection(
        string='Supplier Sourch',
        selection=[('local', 'Local'), ('indent', 'Indent')]
    )
    supplier_utility = fields.Boolean(
        string='Supplier Utility', default=False,
    )
    supplier_problem = fields.Boolean(
        string='Supplier Problem', default=False,
    )
    supplier_entity_type = fields.Selection(
        string='Supplier Entity Type',
        selection=[('3rd', '3rd Imposrter'), ('foreign', 'Foreign'), ('local', 'Local')]
    )
    type_of_entity = fields.Selection(
        string='Type Of Entity',
        selection=[('cv', 'CV Firm and Maatschap'), ('perorangan', 'Perusahaan Perorangan'), ('pt', 'PT and Cooperative')]
    )
    # tax_supplier = fields.Boolean(
    #     string='Taxable Supplier',
    #     default=False
    # )
    tax_supplier = fields.Selection(
        string='Taxable Supplier',
        selection=[('yes', 'Yes'), ('no', 'No')],
        default='no'
    )
    vat_reg_number = fields.Char(
        string='Vat Registration Number',
    )
    pb1_taxable_supplier = fields.Char(
        string='PB1 Taxable Supplier',
    )
    pb1_reg_number = fields.Char(
        string='PB1 Registration Number',
    )
    agreement_contract_ids = fields.One2many(
        string='Agreement Contract',
        comodel_name='agreement.contract',
        inverse_name='supplier_id',
    )
    account_tax_ids = fields.One2many(
        string='Account Tax',
        comodel_name='account.tax',
        inverse_name='supplier_id',
    )
    
    
    
    

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["supplier_code"] = self.env["ir.sequence"].next_by_code("res.partner")
        return super(InheritResPartner, self).create(vals_list)
