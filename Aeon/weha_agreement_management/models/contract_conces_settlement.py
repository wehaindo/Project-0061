# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractConcesSettlement(models.Model):
    _name = "contract.conces.settlement"
    _description = "Contract Conces Settlement"


    @api.depends('conces_settlement_line_ids')
    def _calculate_total(self):
        data = 0.0
        for line in self:
            query="""SELECT sum(subtotal) as total
                FROM contract_conces_settlement_line
                WHERE conces_settlement_id={}
                GROUP BY conces_settlement_id""".format(line.id)
            self.env.cr.execute(query)
            total_ids = self.env.cr.dictfetchall()
            for rec in total_ids:
                line.total = rec['total']


    name = fields.Char(string="Code", readonly=True)
    date = fields.Date(default=fields.Date.today)
    payment_term_id = fields.Many2one(
        string='Credit Term',
        comodel_name='account.payment.term',
        ondelete='restrict',
    )
    agreement_contract_id = fields.Many2one(
        string='Agreement Contract',
        comodel_name='agreement.contract',
        ondelete='restrict',
    )
    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
        ondelete='restrict',
    )
    total = fields.Float(
        string='Total',
        compute='_calculate_total',
        store=True
    )
    settlement_id = fields.Many2one(
        string='settlement',
        comodel_name='settlement.process',
        ondelete='restrict',
    )
    conces_settlement_line_ids = fields.One2many(
        string='Conces Settlement Line',
        comodel_name='contract.conces.settlement.line',
        inverse_name='conces_settlement_id',
    )
    state = fields.Selection(
        string='state',
        selection=[('draft', 'Draft'), ('posted', 'Posted')],
        default="draft"
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("contract.conces.settlement")
        return super(ContractConcesSettlement, self).create(vals_list)


class ContractConcesSettlementLine(models.Model):
    _name = "contract.conces.settlement.line"
    _description = "Contract Conces Settlement"

    Expenses = [("percent","Percentage"), ("amount","Amount")]

    
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        ondelete='restrict',
    )
    store_id = fields.Many2one(
        string='Store',
        comodel_name='res.branch',
        ondelete='restrict',
        related='product_id.branch_id',
        readonly=True,
        store=True
    )
    name = fields.Char(
        string='Description',
    )
    qty = fields.Float(
        string='Qty',
    )
    unit_price = fields.Float(
        string='Unit Price',
    )
    discount = fields.Float(
        string='Margin Discount',
    )
    subtotal = fields.Float(
        string='Subtotal',
    )
    conces_settlement_id = fields.Many2one(
        string='Consigment Settlement',
        comodel_name='contract.conces.settlement',
        ondelete='restrict',
    )