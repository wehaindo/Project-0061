from odoo import fields, models


class PosReceipt(models.Model):
    _name = 'pos.receipt'

    name = fields.Char(string='Name')
    setu_design_receipt = fields.Text(string='Receipt XML', help='Add your customised receipts for pos')
