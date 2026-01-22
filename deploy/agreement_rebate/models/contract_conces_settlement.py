# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractConcesSettlement(models.Model):
    _name = "contract.conces.settlement"
    _description = "Contract Conces Settlement"

    name = fields.Char(required=True, default="/")
    date = fields.Date(default=fields.Date.today)
    date_from = fields.Date()
    date_to = fields.Date()
    conces_settlement_line_ids = fields.One2many(
        string='Consigment Settlement Line',
        comodel_name='contract.conces.settlement.line',
        inverse_name='conces_settlement_id',
    )
    
    is_po = fields.Boolean(
        string='is_po',
        default=False
    )
    

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") != "/":
                continue
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "contract.conces.settlement"
            )
        return super(ContractConcesSettlement, self).create(vals_list)

    def action_show_settlement(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "agreement_rebate.action_conces_act_window"
        )
        if len(self) == 1:
            form = self.env.ref("agreement_rebate.view_conces_form")
            action["views"] = [(form.id, "form")]
            action["res_id"] = self.id
        else:
            action["domain"] = [("id", "in", self.ids)]
        return action


class ContractConcesSettlementLine(models.Model):
    _name = "contract.conces.settlement.line"
    _description = "Contract Conces Settlement"
    _rec_name = "partner_id"

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
    conces_settlement_id = fields.Many2one(
        string='Consigment Settlement',
        comodel_name='contract.conces.settlement',
        ondelete='restrict',
    )
    conces_settlement_product_ids = fields.One2many(
        string='Consigment Settlement Product',
        comodel_name='contract.conces.settlement.product',
        inverse_name='conces_settlement_line_id',
    )
    
    calculate_rebate_amoun = fields.Float(
        string='Rebate Amount',
        compute="calculate_rebate_amount",
        store=True,
    )
    is_po = fields.Boolean(
        string='is po',
        default=False
    )
    

    @api.depends('conces_settlement_product_ids.amount_rebate')
    def calculate_rebate_amount(self):
        data = 0.0
        for val in self:
            for line in val.conces_settlement_product_ids:
                datas = self.env['contract.conces.settlement.product'].browse(line.id)
                data += datas.amount_rebate
            val.calculate_rebate_amoun = data


class ContractConcesSettlementProduct(models.Model):
    _name = "contract.conces.settlement.product"
    _description = "Contract conces Settlement Product"
    _rec_name = "product_id"

    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        ondelete='restrict',
    )
    name = fields.Char(
        string='Description',
    )
    
    qty = fields.Float(
        string='Qty',
    )
    amount_po = fields.Float(
        string='Unit Price',
        
    )
    discount = fields.Float(
        string='Margin Discount',
    )
    amount_rebate = fields.Float(
        string='Amount Rebate',
    )
    conces_settlement_line_id = fields.Many2one(
        string='Consigment Settlement Line',
        comodel_name='contract.conces.settlement.line',
        ondelete='restrict',
    )