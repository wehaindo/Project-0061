from odoo import _, api, fields, models
from datetime import datetime, timedelta, date

import logging

_logger = logging.getLogger(__name__)

# Subset of partner fields: sync all or none to avoid mixed addresses
PARTNER_ADDRESS_FIELDS_TO_SYNC = [
    'street',
    'street2',
    'city',
    'zip',
    'state_id',
    'country_id',
]

class AgreementContract(models.Model):
    _name = "agreement.contract"
    _description = "Agreement Contract"
    _rec_name = "code"
    _order = "code asc"

    @api.depends('supplier_id')
    def _compute_partner_address_values(self):
        """ Sync all or none of address fields """
        for lead in self:
            lead.update(lead._prepare_address_values_from_partner(lead.supplier_id))

    def _prepare_address_values_from_partner(self, partner):
        # Sync all address fields from partner, or none, to avoid mixing them.
        if any(partner[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC):
            values = {f: partner[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC}
        else:
            values = {f: self[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC}
        return values

    
    @api.onchange('supplier_contract_type')
    def _onchange_contract_holder_type(self):
        for res in self:
            if res.supplier_contract_type == 'general':
                res.contract_holder_type = 'distributor'


    code = fields.Char(string="Code", )
    signature_date = fields.Date(tracking=True, default=lambda self: fields.datetime.now(), readonly=True)
    start_date = fields.Date(tracking=True, default=lambda self: fields.datetime.now())
    end_date = fields.Date(tracking=True)
    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
        ondelete='set null',
    )
    supplier_code = fields.Char(
        string='Supplier Code',
        related='supplier_id.supplier_code',
        readonly=True,
        store=True
    )
    # Address fields
    street = fields.Char('Street', compute='_compute_partner_address_values', readonly=False, store=True)
    street2 = fields.Char('Street2', compute='_compute_partner_address_values', readonly=False, store=True)
    zip = fields.Char('Zip', change_default=True, compute='_compute_partner_address_values', readonly=False, store=True)
    city = fields.Char('City', compute='_compute_partner_address_values', readonly=False, store=True)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        compute='_compute_partner_address_values', readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        compute='_compute_partner_address_values', readonly=False, store=True)
    
    # principle Address fields
    new_supplier_id = fields.Many2one(
        string='Principle',
        comodel_name='res.partner',
        ondelete='set null',
    )
    new_supplier_code = fields.Char(
        string='Principle Code',
        related='new_supplier_id.supplier_code',
        readonly=True,
        store=True
    )
    new_street = fields.Char('Street', related='new_supplier_id.street', readonly=False, store=True)
    new_street2 = fields.Char('Street2', related='new_supplier_id.street2', readonly=False, store=True)
    new_zip = fields.Char('Zip', change_default=True, related='new_supplier_id.zip', readonly=False, store=True)
    new_city = fields.Char('City', related='new_supplier_id.city', readonly=False, store=True)
    new_state_id = fields.Many2one(
        "res.country.state", string='State',
        related='new_supplier_id.state_id', readonly=False, store=True,)
    new_country_id = fields.Many2one(
        'res.country', string='Country',
        related='new_supplier_id.country_id', readonly=False, store=True)
    
    supplier_contract_type = fields.Selection(
        string='Supplier Contract Type',
        selection=[('general', 'General Yearly Contract Form'), ('ab', 'Form A & B')],
        default='general'
    )
    supplier_sub_type = fields.Selection(
        string='Supplier Sub-Type',
        selection=[('consignment', 'Consignment'), ('outright', 'Outright')],
    )
    contract_holder_type = fields.Selection(
        string='Contract Holder',
        selection=[('distributor', 'Distributor'), ('principal', 'Principal')],
        default='distributor'
    )
    supplier_source = fields.Selection(
        string='Supplier Sourch',
        selection=[('local', 'Local'), ('indent', 'Indent')],
    )
    payment_term_id = fields.Many2one(
        string='Credit Term',
        comodel_name='account.payment.term',
        ondelete='set null',
    )
    tax_id = fields.Many2one(
        string='Tax',
        comodel_name='account.tax',
        ondelete='set null',
    )
    target = fields.Float(
        string='Net Purchase / Sales Target (Exclusive Tax)',
    )
    description = fields.Text(
        string='Description',
    )
    guarantee_min_monthly = fields.Float(string="Monthly Minimum Guarantee")
    guarantee_min_yearly = fields.Float(string="Yearly Minimum Guarantee")
    guarantee_total = fields.Float(string="Total Guarantee Margin (GP%)")
    # consignment fixed margin
    fixed_percent = fields.Float(string='Fixed Margin %',)
    
    line_ids = fields.Many2many(
        string='Line',
        comodel_name='res.line'
    )
    branch_ids = fields.Many2many(
        string='Store',
        comodel_name='res.branch'
    )
    deduction_ids = fields.One2many(
        string='Deduction',
        comodel_name='contract.deduction',
        inverse_name='contract_id',
    )
    
    rebate_ids = fields.One2many(
        string='Rebate',
        comodel_name='contract.rebate',
        inverse_name='contract_id',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            ir_sequence_obj = self.env["ir.sequence"]
            partner_id = self.env["res.partner"].browse(vals.get("supplier_id"))
            code = "{}.{}".format(vals.get("supplier_sub_type"), partner_id.supplier_code)
            _logger.info(code)
            ir_sequences = ir_sequence_obj.search([('code','=', code)])

            if len(ir_sequences) != 0:
                vals["code"] = ir_sequence_obj.next_by_code(code) or _('New')
            else:
                if vals.get("supplier_sub_type") == 'consignment':
                    prefix = 'CS-'
                else:
                    prefix = 'OS-'
                value = {
                    'name': code,
                    'code': code,
                    'prefix': prefix,
                    'padding': 3
                }
                ir_sequence_obj.sudo().create(value)
                vals["code"] = ir_sequence_obj.next_by_code(code) or _('New')
        return super(AgreementContract, self).create(vals_list)
    