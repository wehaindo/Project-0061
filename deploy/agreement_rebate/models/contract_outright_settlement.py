# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractOutrightSettlement(models.Model):
    _name = "contract.outright.settlement"
    _description = "Contract Outright Settlement"

    name = fields.Char(required=True, default="/")
    date = fields.Date(default=fields.Date.today)
    date_from = fields.Date()
    date_to = fields.Date()
    outright_settlement_line_ids = fields.One2many(
        string='Outright Settlement Line',
        comodel_name='contract.outright.settlement.line',
        inverse_name='outright_settlement_id',
    )
    
    is_invoice = fields.Boolean(
        string='is invoice',
    )
    

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") != "/":
                continue
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "contract.outright.settlement"
            )
        return super(ContractOutrightSettlement, self).create(vals_list)

    def action_show_settlement(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "agreement_rebate.action_outright_act_window"
        )
        if len(self) == 1:
            form = self.env.ref("agreement_rebate.view_outright_form")
            action["views"] = [(form.id, "form")]
            action["res_id"] = self.id
        else:
            action["domain"] = [("id", "in", self.ids)]
        return action


class ContractOutrightSettlementLine(models.Model):
    _name = "contract.outright.settlement.line"
    _description = "Contract Outright Settlement"

    
    partner_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
        ondelete='restrict',
    )
    agreement_id = fields.Many2one(
        string='Agreement',
        comodel_name='agreement',
        ondelete='restrict',
    )
    
    purchase_id = fields.Many2one(
        string='Purchase Order',
        comodel_name='purchase.order',
        ondelete='restrict',
    )
    
    outright_settlement_id = fields.Many2one(
        string='Outright Settlement',
        comodel_name='contract.outright.settlement',
        ondelete='restrict',
    )
    outright_settlement_product_ids = fields.One2many(
        string='Outright Settlement Product',
        comodel_name='contract.outright.settlement.product',
        inverse_name='outright_settlement_line_id',
    )
    is_invoice = fields.Boolean(
        string='is invoice',
        default=False
    )
    
    
    
    
class ContractOutrightSettlementProduct(models.Model):
    _name = "contract.outright.settlement.product"
    _description = "Contract Outright Settlement Product"

    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        ondelete='restrict',
    )
    name = fields.Char(
        string='Description',
        related='product_id.default_code',
        readonly=True,
        store=True
    )
    
    qty = fields.Float(
        string='qty',
    )
    
    amount_po = fields.Float(
        string='Amount PO',
        
    )
    discount = fields.Float(
        string='Margin Discount',
    )
    amount_rebate = fields.Float(
        string='Amount Rebate',
    )
    outright_settlement_line_id = fields.Many2one(
        string='Outright Settlement Line',
        comodel_name='contract.outright.settlement.line',
        ondelete='restrict',
    )
    
    
    