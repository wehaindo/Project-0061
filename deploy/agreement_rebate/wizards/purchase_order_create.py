# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AgreementSettlementInvoiceCreateWiz(models.TransientModel):
    _name = "agreement.purchase.order.create.wiz"
    _description = "Agreement Purchase Order create wizard"

    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")


    def _prepare_settlement_domain(self):
        domain = []
        if self.date_from:
            domain.extend([("date_to", ">=", self.date_from)])
        if self.date_to:
            domain.extend([("date_to", "<=", self.date_to)])

        return domain

    def action_create_purchase_order(self):
        outright_obj = self.env["contract.outright.settlement"]
        po_obj = self.env["purchase.order"]

        outright_ids = outright_obj.search(self._prepare_settlement_domain())
        vals = {}
        for line in outright_ids:
            vals.update({
                ''
            })
        
        po_obj.create(vals)
