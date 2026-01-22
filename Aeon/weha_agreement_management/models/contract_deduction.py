from odoo import _, api, fields, models
from datetime import datetime, timedelta, date

class ContractDeduction(models.Model):
    _name = "contract.deduction"
    _description = "Contract Deduction"

    receipt = [("distributor","Distributor"), ("principal","Principal")]
    method = [("auto","Auto Deduct Payment"), ("collection","Payment Collection")]

    name = fields.Char(string="Name",)
    receipt = fields.Selection(string='Receipt to', selection=receipt)
    method = fields.Selection(string='Payment Method', selection=method)
    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
        ondelete='set null',
    )
    contract_id = fields.Many2one(
        string='Contract',
        comodel_name='agreement.contract',
        ondelete='set null',
    )
    journal_id = fields.Many2one(
        string='Journal',
        comodel_name='account.journal',
        ondelete='set null',
    )
    account_id = fields.Many2one(
        string='Account',
        comodel_name='account.account',
        ondelete='set null',
    )

    
    