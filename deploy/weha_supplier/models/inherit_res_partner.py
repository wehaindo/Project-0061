from odoo import _, api, fields, exceptions, models

class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    def get_supplier_branch_status(self):
        if self.partner_id:
            self.is_supplier_branch = True
        else:
            self.is_supplier_branch = False

    partner_id = fields.Many2one(
        string='Parent',
        comodel_name='res.partner',
        ondelete='restrict',
    )

    is_supplier_branch = fields.Boolean(compute=get_supplier_branch_status)

    res_partner_ids = fields.One2many('res.partner','partner_id', 'Branch')
    
    res_branch_supplier_ids = fields.One2many('res.branch.supplier', 'partner_id', 'Stores')

    code_siup = fields.Char(
        string='SIUP',
    )

    supplier_code = fields.Char(
        string='Supplier Code',
    )
    
    agreement_ids = fields.One2many(
        string='Agreement',
        comodel_name='agreement',
        inverse_name='partner_id',
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

    def _get_next_supplier_code(self, vals=None):
        return self.env["ir.sequence"].next_by_code("res.partner")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("supplier_code") and self._needs_supplier_code(vals=vals):
                vals["supplier_code"] = self._get_next_supplier_code(vals=vals)
        return super(InheritResPartner, self).create(vals_list)

    def copy(self, default=None):
        default = default or {}
        if self._needs_supplier_code():
            default["supplier_code"] = self._get_next_supplier_code()
        return super(InheritResPartner, self).copy(default=default)

    def write(self, vals):
        for partner in self:
            partner_vals = vals.copy()
            if (
                not partner_vals.get("supplier_code")
                and partner._needs_supplier_code(vals=partner_vals)
                and not partner.supplier_code
            ):
                partner_vals["supplier_code"] = partner._get_next_supplier_code(vals=partner_vals)
            super(InheritResPartner, partner).write(partner_vals)
        return True

    def _needs_supplier_code(self, vals=None):
        """
        Checks whether a sequence value should be assigned to a partner's 'supplier_code'
        :param vals: known field values of the partner object
        :return: true iff a sequence value should be assigned to the\
                      partner's 'supplier_code'
        """
        if not vals and not self:  # pragma: no cover
            raise exceptions.UserError(
                _("Either field values or an id must be provided.")
            )
        # only assign a 'supplier_code' to commercial partners
        if self:
            vals = {"is_company": self.is_company, "parent_id": self.parent_id}
        return vals.get("is_company") or not vals.get("parent_id")

    @api.model
    def _commercial_fields(self):
        """
        Make the partner supplier_codeerence a field that is propagated
        to the partner's contacts
        """
        return super(InheritResPartner, self)._commercial_fields() + ["supplier_code"]
    