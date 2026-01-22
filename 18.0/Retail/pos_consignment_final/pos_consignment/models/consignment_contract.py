
from odoo import fields, models

class ConsignmentContract(models.Model):
    _name = "consignment.contract"
    _description = "Consignment Contract"

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner', domain=[('supplier_rank','>',0)], required=True)
    start_date = fields.Date()
    end_date = fields.Date()
    commission_type = fields.Selection([('percent','Percent'),('fixed','Fixed')], default='percent')
    commission_value = fields.Float(default=0.0)
    product_line_ids = fields.One2many('consignment.contract.line','contract_id', string="Products")
    state = fields.Selection([('draft','Draft'),('active','Active'),('cancel','Cancelled')], default='draft')

    def action_activate(self):
        self.state = 'active'

class ConsignmentContractLine(models.Model):
    _name = "consignment.contract.line"
    _description = "Consignment Contract Line"

    contract_id = fields.Many2one('consignment.contract', ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Product", required=True)
    consignment_price = fields.Float(string="Agreed Price")
    commission_rate = fields.Float(string="Commission %", help="Overrides contract commission if set")
