# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class ContractSettlementWiz(models.TransientModel):
    _name = "contract.settlement.wiz"
    _description = "Contract settlement create wizard"

    date = fields.Date(default=fields.Date.today)
    date_from = fields.Date(string="From", required=False)
    date_to = fields.Date(string="To", required=False)
    supplier_sub_type = fields.Selection(
        string='Supplier Type',
        selection=[('concessionaire', 'Concessionaire'), ('outright', 'Outright')],
        required=False
    )
    payment_term_id = fields.Many2one(
        string='Credit Term',
        comodel_name='account.payment.term',
        ondelete='restrict',
    )

    def action_create_settlement(self):
        rebate_obj = self.env["contract.rebate"]
        contract_obj = self.env["agreement.contract"]
        outright_obj = self.env["contract.outright.settlement"]
        po_obj = self.env["purchase.order"]

        if self.supplier_sub_type == 'outright':
            term_day = 1
            for term in self.payment_term_id.line_ids:
                term_day = term.days
            date_now = datetime.now()
            term_date = date_now + relativedelta(day=term_day)
            date_now =  fields.Date.to_string(date_now)

            # CHECK CONTRACT AND TERM CONDITION
            contract_ids = contract_obj.search([
                ('start_date','<=', date_now), ('end_date','>=', date_now), ('payment_term_id','=', self.payment_term_id.id)
                ])

            outright = []
            for ct in contract_ids:
                contract_id = ct.id
                vals = {}
                vals_line = []
                if contract_id:
                    # CHECK PURCHASE ORDER BY CONTRACT AND TERM CONDITION
                    po_ids = po_obj.search([('is_settlement','=', False), ('agreement_contract_id','=', contract_id), ('create_date','<=', fields.Date.to_string(term_date))])
                    supplier = False
                    for po in po_ids:
                        supplier = po.partner_id
                        total = 0.0
                        for line in po.order_line:
                            price = line.price_unit
                            qty = line.qty_received
                            subtotal = (price*qty)
                            total += subtotal
                        # CHECK REBATE
                        rebate_ids = rebate_obj.search([('contract_id','=', contract_id)])
                        price_total = 0.0
                        for rbt in rebate_ids:
                            if rbt.expenses_type == "percent":
                                rebate_disc = (rbt.rebate_value/100)
                                price_total = total - (rebate_disc*total)
                            else:
                                price_total = rbt.rebate_value
                            vals_line.append((
                                (0,0, {
                                        'purchase_id': po.id,
                                        'total_po': total,
                                        'expenses_type': rbt.expenses_type,
                                        'rebate_value': rbt.rebate_value,
                                        'subtotal': price_total,
                                    })
                            ))
                        # po.is_settlement = True

                    vals.update({
                        "supplier_id": supplier.id,
                        "agreement_contract_id": contract_id,
                        "payment_term_id": self.payment_term_id.id,
                        "outright_settlement_line_ids": vals_line
                    })
                
                _logger.info("____OUTRIGHT")
                _logger.info(vals)
                # CREATE OUTRIGHT SETTLEMENT
                res = outright_obj.create(vals)
                outright.append(res.id)

            return self.action_show_outright_settlement(outright)
        
        else:
            pass
        


    def action_show_outright_settlement(self, settlement):
        self.ensure_one()
        tree_view = self.env.ref("weha_agreement_management.view_outright_tree", raise_if_not_found=False)
        form_view = self.env.ref("weha_agreement_management.view_outright_form", raise_if_not_found=False)
        action = {
            "type": "ir.actions.act_window",
            "name": "Outright Settlement",
            "res_model": "contract.outright.settlement",
            "view_mode": "tree,kanban,form,calendar,pivot,graph,activity",
            "domain": [("id", "in", settlement)],
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action

    
    # term_day = 1
        # for term in self.payment_term_id.line_ids:
        #     term_day = term.days
        # date_now = datetime.now()
        # term_date = date_now + relativedelta(day=term_day)

        # domain_group = [
        #     ("create_date","<=", fields.Date.to_string(term_date)),
        #     ("agreement_contract_id","!=", False)
        #     ]
        # _logger.info("____DOMAIN GROUP")
        # _logger.info(domain_group)

        # groups = po_obj.read_group(domain=domain_group, 
        #             fields=['agreement_contract_id'],
        #             groupby=['agreement_contract_id'],
        #             lazy=False,)
        # _logger.info(groups)
        # for group in groups:
        #     # contract_ids = contract_obj.search([('payment_term_id','=', self.payment_term_id.id)])
        #     # for rec in contract_ids:
        #     query = '''
        #         SELECT a.id, a.agreement_contract_id, b.product_id, sum(b.qty_received) as qty, sum(b.price_unit) as price
        #         FROM purchase_order a
        #         LEFT JOIN purchase_order_line b ON a.id = b.order_id
        #         WHERE a.is_settlement='f' AND a.create_date<='{}' AND a.agreement_contract_id={}
        #         GROUP BY a.id, a.agreement_contract_id, b.product_id
        #     '''.format(fields.Date.to_string(term_date), group.get('agreement_contract_id')[0])
        #     self.env.cr.execute(query)
        #     _logger.info(query)
        #     po_ids = self.env.cr.dictfetchall()
        #     total = 0.0
        #     for po in po_ids:
        #         price = po['price']
        #         qty = po['qty']
        #         subtotal = (price*qty)
        #         total += subtotal

        #         vals_line.append((
        #             (0,0, {
        #                     'purchase_id': po['id'],
        #                     'total_po': total,
        #                     'expenses_type': rbt.expenses_type,
        #                     'rebate_value': rbt.rebate_value,
        #                     'subtotal': price_total,
        #                 })
        #         ))

        # domain_group = [
        #     ("create_date","<=", fields.Date.to_string(term_date)),
        #     ("agreement_contract_id","!=", False)
        #     ]
        # _logger.info("____DOMAIN GROUP")
        # _logger.info(domain_group)

        # groups = po_obj.read_group(domain=domain_group, 
        #             fields=['agreement_contract_id'],
        #             groupby=['agreement_contract_id'],
        #             lazy=False,)
        # _logger.info(groups)

