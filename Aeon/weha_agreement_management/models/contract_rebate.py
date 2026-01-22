from odoo import _, api, fields, models
from datetime import datetime, timedelta, date

import logging

_logger = logging.getLogger(__name__)

class ContractRebate(models.Model):
    _name = "contract.rebate"
    _description = "Contract Rebate"
    _rec_name = "code"
    _sql_constraints = [
        ('contract_value_unique', 'unique(supplier_id, contract_id, deduction_id, store_id)', "Can't be duplicate value for this supplier, contract, deduction & store!")
    ]

    Expenses = [("percent","Percentage"), ("amount","Amount")]

    @api.onchange('contract_id.branch_ids')
    def _filter_store(self):
        active_id = self.env.context.get('default_active_id')
        contract_ids= self.env['agreement.contract'].browse(active_id)
        domain =[('id', '=', -1)]
        store=[]
        for each in contract_ids.branch_ids:
            store.append(each.id)
        if store:
            domain =[('id', 'in', store)]
            return domain
        return domain
    
    @api.onchange('contract_id.deduction_ids')
    def _filter_deduction(self):
        active_id = self.env.context.get('default_active_id')
        contract_ids= self.env['agreement.contract'].browse(active_id)
        domain =[('id', '=', -1)]
        deduction=[]
        for each in contract_ids.deduction_ids:
            deduction.append(each.id)
        if deduction:
            domain =[('id', 'in', deduction)]
            return domain
        return domain

    code = fields.Char(string="Code", )
    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
        ondelete='set null', 
        related='contract_id.supplier_id',
        readonly=True,
        store=True
    )
    contract_id = fields.Many2one(
        string='Contract',
        comodel_name='agreement.contract',
        ondelete='set null',
    )
    date_year = fields.Date(
        string='Rebate Year',
    )
    start_date = fields.Date(tracking=True, default=lambda self: fields.datetime.now())
    end_date = fields.Date(tracking=True)
    store_id = fields.Many2one(
        string='Store',
        comodel_name='res.branch',
        ondelete='set null',
        domain=_filter_store
    )
    
    rebate_line_ids = fields.One2many(
        string='rebate line',
        comodel_name='contract.rebate.line',
        inverse_name='rebate_id',
    )
    deduction_id = fields.Many2one(
        string='Transaction Type',
        comodel_name='contract.deduction',
        ondelete='set null',
        domain=_filter_deduction
    )
    expenses_type = fields.Selection(
        string='Expenses Type',
        selection=Expenses
    )
    rebate_value = fields.Float(
        string='Value',
    )
    is_process = fields.Boolean(
        string='is process',
        default=False,
        index=True
        
    )
    calculate_from = fields.Selection(
        string='Calculate From',
        selection=[('sales', 'Total Sales'), ('purchase', 'Total Purchase')]
    )
    payment_periode = fields.Selection(
        string='Rebate Type',
        selection=[('onetime', 'One Time'), ('monthly', 'Monthly')]
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["code"] = self.env["ir.sequence"].next_by_code(
                "contract.rebate"
            )
        return super(ContractRebate, self).create(vals_list)


class ContractRebateLine(models.Model):
    _name = "contract.rebate.line"
    _description = "Contract Rebate Line"


    amount_from = fields.Float(
        string='From Amount',
    )
    amount_to = fields.Float(
        string='To Amount',
    )
    percent = fields.Float(string='Amount %',)
    rebate_id = fields.Many2one(
        string='rebate',
        comodel_name='contract.rebate',
        ondelete='set null',
    )
    