from odoo import api, fields, models


class ContractRebateSettlement(models.Model):
    _name = "contract.rebate.settlement"
    _description = "Contract Rebate Settlement"

    
    name = fields.Char(
        string='Batch ID',
    )
    date = fields.Date(default=fields.Date.today)
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
    contract_id = fields.Many2one(
        string='Agreement Contract',
        comodel_name='agreement.contract',
        ondelete='set null',
    )
    bu_id = fields.Many2one(
        string='Branch',
        comodel_name='business.unit',
        ondelete='set null',
    )
    store_id = fields.Many2one(
        string='Store',
        comodel_name='res.branch',
        ondelete='set null',
    )
    payment_periode = fields.Selection(
        string='Rebate Type',
        selection=[('onetime', 'One Time'), ('monthly', 'Monthly')]
    )
    deduction_id = fields.Many2one(
        string='Rebate Trans Type',
        comodel_name='contract.deduction',
        ondelete='set null',
    )
    net_purchase = fields.Float(
        string='Net Purchase',
    )
    rebate_amount = fields.Float(
        string='Rebate Amount',
    )
    settlement_id = fields.Many2one(
        string='settlement',
        comodel_name='settlement.process',
        ondelete='set null',
    )
    state = fields.Selection(
        string='state',
        selection=[('draft', 'Draft'), ('posted', 'Posted')],
        default="draft"
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("contract.rebate.settlement")
        return super(ContractRebateSettlement, self).create(vals_list)