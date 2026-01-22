# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractOutrightSettlement(models.Model):
    _name = "contract.outright.settlement"
    _description = "Contract Outright Settlement"


    def action_open_invoice(self):
        pass

    @api.depends('outright_settlement_line_ids')
    def _calculate_total(self):
        data = 0.0
        for line in self:
            query="""SELECT sum(subtotal) as total
                FROM contract_outright_settlement_sales
                WHERE outright_settlement_id={}
                GROUP BY outright_settlement_id""".format(line.id)
            self.env.cr.execute(query)
            total_ids = self.env.cr.dictfetchall()
            for rec in total_ids:
                line.total = rec['total']

    @api.depends('outright_settlement_sales_ids')
    def _calculate_total_rebate_sales(self):
        data = 0.0
        for line in self:
            query="""SELECT sum(subtotal) as total
                FROM contract_outright_settlement_line
                WHERE outright_settlement_id={}
                GROUP BY outright_settlement_id""".format(line.id)
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
        string='Total Rebate Purchase',
        compute='_calculate_total',
        store=True
    )
    total_rebate_sales = fields.Float(
        string='Total Rebate Sales',
        compute='_calculate_total_rebate_sales',
        store=True
    )
    settlement_id = fields.Many2one(
        string='settlement',
        comodel_name='settlement.process',
        ondelete='restrict',
    )
    outright_settlement_line_ids = fields.One2many(
        string='Outright Settlement Line',
        comodel_name='contract.outright.settlement.line',
        inverse_name='outright_settlement_id',
    )
    outright_settlement_sales_ids = fields.One2many(
        string='Outright Settlement Sales',
        comodel_name='contract.outright.settlement.sales',
        inverse_name='outright_settlement_id',
    )
    state = fields.Selection(
        string='state',
        selection=[('draft', 'Draft'), ('posted', 'Posted')],
        default="draft"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("contract.outright.settlement")
        return super(ContractOutrightSettlement, self).create(vals_list)
    

class ContractOutrightSettlementLine(models.Model):
    _name = "contract.outright.settlement.line"
    _description = "Contract Outright Settlement Purchase"

    Expenses = [("percent","Percentage"), ("amount","Amount")]
    
    purchase_id = fields.Many2one(
        string='Purchase Order',
        comodel_name='purchase.order',
        ondelete='restrict',
    )
    rebate_id = fields.Many2one(
        string='Rebate',
        comodel_name='contract.rebate',
        ondelete='restrict',
    )
    store_id = fields.Many2one(
        string='Store',
        comodel_name='res.branch',
        ondelete='restrict',
        related='rebate_id.store_id',
        readonly=True,
        store=True
    )
    deduction_id = fields.Many2one(
        string='Transaction Type',
        comodel_name='contract.deduction',
        ondelete='restrict',
        related='rebate_id.deduction_id',
        readonly=True,
        store=True
    )
    total_po = fields.Float(
        string='Total Purchase',
    )
    expenses_type = fields.Selection(
        string='Expenses Type',
        selection=Expenses
    )
    rebate_value = fields.Float(
        string='Value',
    )
    subtotal = fields.Float(
        string='Subtotal',
    )
    outright_settlement_id = fields.Many2one(
        string='Outright Settlement',
        comodel_name='contract.outright.settlement',
        ondelete='restrict',
    )

class ContractOutrightSettlementSales(models.Model):
    _name = "contract.outright.settlement.sales"
    _description = "Contract Outright Settlement Sales"

    Expenses = [("percent","Percentage"), ("amount","Amount")]
    
    
    rebate_id = fields.Many2one(
        string='Rebate',
        comodel_name='contract.rebate',
        ondelete='restrict',
    )
    store_id = fields.Many2one(
        string='Store',
        comodel_name='res.branch',
        ondelete='restrict',
        related='rebate_id.store_id',
        readonly=True,
        store=True
    )
    deduction_id = fields.Many2one(
        string='Transaction Type',
        comodel_name='contract.deduction',
        ondelete='restrict',
        related='rebate_id.deduction_id',
        readonly=True,
        store=True
    )
    total_sales = fields.Float(
        string='Total Sales',
    )
    expenses_type = fields.Selection(
        string='Expenses Type',
        selection=Expenses
    )
    rebate_value = fields.Float(
        string='Value',
    )
    subtotal = fields.Float(
        string='Subtotal',
    )
    outright_settlement_id = fields.Many2one(
        string='Outright Settlement',
        comodel_name='contract.outright.settlement',
        ondelete='restrict',
    )
    
    