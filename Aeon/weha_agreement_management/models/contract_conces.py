from odoo import _, api, fields, models
from datetime import datetime, timedelta, date

class ContractConces(models.Model):
    _name = "contract.conces"
    _description = "Contract Concesioner"
    


    code = fields.Char(string="Code",)
    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
        ondelete='restrict',
    )
    contract_id = fields.Many2one(
        string='Contract',
        comodel_name='agreement.contract',
        ondelete='restrict',
    )
    fixed_percent = fields.Float(string='Amount %',)
    conces_line_ids = fields.One2many(
        string='conces line',
        comodel_name='contract.conces.line',
        inverse_name='conces_id',
    )
    




class ContractConcesLine(models.Model):
    _name = "contract.conces.line"
    _description = "Contract Concesioner Line"


    amount_from = fields.Float(
        string='From Amount',
    )
    amount_to = fields.Float(
        string='From Amount',
    )
    percent = fields.Float(string='Amount %',)
    conces_id = fields.Many2one(
        string='conces',
        comodel_name='contract.conces',
        ondelete='restrict',
    )