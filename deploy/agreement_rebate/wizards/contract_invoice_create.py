# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict
from datetime import datetime
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class ContractInvoiceCreateWiz(models.TransientModel):
    _name = "contract.invoice.create.wiz"
    _description = "Contract invoice create wizard"

    date = fields.Date(default=fields.Date.today)
    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)
    supplier_sub_type = fields.Selection(
        string='Supplier Type',
        selection=[('concessionaire', 'Concessionaire'), ('outright', 'Outright')],
        store=True,
        required=True
    )

    def _prepare_settlement_domain(self):
        domain = []
        if self.date_from:
            domain.extend(
                ["|", ("date", "=", False), ("date", ">=", self.date_from)]
            )
        if self.date_to:
            domain.extend([("date", "<=", self.date_to)])

        return domain
    
    def action_create(self):
        if not self.env.user.company_id.rebate_product_id:
            raise ValidationError("Set Product Rebate in Company Settings!")

        if self.supplier_sub_type == "outright":
            # CREATE INVOICE
            outright_obj = self.env['contract.outright.settlement']
            outright_line_obj = self.env['contract.outright.settlement.line']
            account_move_obj = self.env['account.move']
            datefrom = fields.Date.to_string(self.date_from)
            dateto = fields.Date.to_string(self.date_to)

            query = """SELECT b.partner_id, SUM(a.amount_rebate) as amount
                FROM contract_outright_settlement_product a
                LEFT JOIN contract_outright_settlement_line b ON a.outright_settlement_line_id = b.id
                WHERE b.create_date BETWEEN '{}' AND '{}'
                GROUP BY b.partner_id""".format(datefrom,dateto)
            self.env.cr.execute(query)
            data_ids = self.env.cr.dictfetchall()

            _logger.info('.....QUERY')
            _logger.info(data_ids)
            rebate_product = self.env.user.company_id.rebate_product_id
            invoice=[]
            value={}
            for line in data_ids:
                value.update({
                    'partner_id': line['partner_id'],
                    'currency_id': self.env.user.company_id.currency_id.id,
                    'name': 'Customer Invoice Rebate',
                    'move_type': 'out_invoice',
                    'invoice_date': datetime.now(),
                    'journal_id': self.env.user.company_id.journal_id.id,
                    'invoice_line_ids': [(0, 0, {
                        'name': rebate_product.name,
                        'account_id': self.env.user.company_id.account_id.id,
                        'price_unit': line['amount'],
                        'quantity': 1.0,
                        'discount': 0.0,
                        'product_uom_id': rebate_product.uom_id.id,
                        'product_id': rebate_product.id
                    })],
                })
                _logger.info('.....DATA TO INVOICE')
                _logger.info(value)
                resc = account_move_obj.sudo().create(value)
                invoice.append(resc.id)
                if resc:
                    domain = [
                        ("create_date",">=", fields.Date.to_string(self.date_from)),
                        ("create_date","<=", fields.Date.to_string(self.date_to)),
                        ("partner_id","=", line['partner_id'])
                        ]
                    res = outright_line_obj.search(domain)
                    if res:
                        po = ""
                        for up in res:
                            up.is_invoice=True
                            po += str(up.purchase_id.name) + " , "
                    resc.write({
                        'ref': po
                    })
                else:
                    raise UserError(_("Error Create Invoice!."))

            return self.action_show_invoices(invoice)
            
        else:
            conces_obj = self.env['contract.conces.settlement.line']
            purchase_obj = self.env['purchase.order']
            datefrom = fields.Date.to_string(self.date_from)
            dateto = fields.Date.to_string(self.date_to)
            domain_group = [
                ("create_date",">=", fields.Date.to_string(self.date_from)),
                ("create_date","<=", fields.Date.to_string(self.date_to)),
                ]
            groups = conces_obj.read_group(domain=domain_group, fields=['partner_id'],
                        groupby=['partner_id'],
                        lazy=False,)
            purchase=[]
            vals={}
            for group in groups:
                domain = [
                    ("create_date",">=", fields.Date.to_string(self.date_from)),
                    ("create_date","<=", fields.Date.to_string(self.date_to)),
                    ("partner_id","=", group.get('partner_id')[0])
                    ]
                conces_ids = conces_obj.search(domain)
                lis=[]
                for conces in conces_ids:
                    for product in conces.conces_settlement_product_ids:
                        lis.append((
                            (0,0, {
                                'product_id': product.product_id.id,
                                'name': product.product_id.name,
                                'product_qty': product.qty,
                                'price_unit': product.amount_po,
                                'price_subtotal': product.amount_rebate
                            })
                        ))
                
                vals.update({
                    'company_id': self.env.user.company_id.id,
                    'currency_id': self.env.user.company_id.currency_id.id,
                    'date_order': datetime.now(),
                    'name': 'Purchase Rebate',
                    'picking_type_id': 1,
                    'partner_id': group.get('partner_id')[0],
                    'order_line': lis
                })
                _logger.info(vals)
                resc = purchase_obj.sudo().create(vals)
                purchase.append(resc.id)
                if resc:
                    domain = [
                            ("create_date",">=", fields.Date.to_string(self.date_from)),
                            ("create_date","<=", fields.Date.to_string(self.date_to))]
                    conces_ids = conces_obj.search(domain)
                    conces_ids.write({'is_po': True})
                else:
                    raise UserError(_("Error Create PO!."))
            
            _logger.info(purchase)
            return self.action_show_po(purchase)

            # query = """SELECT b.partner_id, a.product_id, sum(a.qty) as qty, sum(a.amount_po) as unit_price, sum(a.amount_rebate) as amount
            #         FROM contract_conces_settlement_product a
            #         LEFT JOIN contract_conces_settlement_line b ON a.conces_settlement_line_id = b.id
            #         WHERE b.create_date BETWEEN '{}' AND '{}'
            #         GROUP BY b.partner_id, a.product_id ORDER BY b.partner_id""".format(datefrom,dateto)
            # self.env.cr.execute(query)
            # data_ids = self.env.cr.dictfetchall()
            # _logger.info('.....QUERY')
            # _logger.info(data_ids)
            # vals={}
            # purchase=""
            # partner= 0
            # lis=[]
            # for line in data_ids:
            #     if partner == line['product_id']:
            #         lis.append((
            #             (0,0, {
            #                 'product_id': line['product_id'],
            #                 'name': 'Purchase Rebate',
            #                 'product_qty': line['qty'],
            #                 'price_unit': line['unit_price'],
            #                 'price_subtotal': line['amount']
            #             })
            #         ))
            #         partner = line['product_id']
            #     else:

            #     vals.update({
            #         'company_id': self.env.user.company_id.id,
            #         'currency_id': self.env.user.company_id.currency_id.id,
            #         'date_order': datetime.now(),
            #         'name': 'Purchase Rebate',
            #         'picking_type_id': 1,
            #         'partner_id': line['partner_id'],
            #         'order_line': lis
            #     })
            #     _logger.info('.....DATA')
            #     _logger.info(vals)
            #         resc = purchase_obj.sudo().create(vals)
            #         if resc:
            #             domain = [
            #                     ("create_date",">=", fields.Date.to_string(self.date_from)),
            #                     ("create_date","<=", fields.Date.to_string(self.date_to))]
            #             conces_ids = conces_obj.search(domain)
            #             # for up in res:
            #             #     up.is_po = True
            #             conces_ids.write({'is_po': True})
            #             purchase += str(resc.id)+","
            #         else:
            #             raise UserError(_("Error Create PO!."))

            # purchase = "["+purchase+"]"
            # return self.action_show_po(purchase)

    def action_show_invoices(self, invoices):
        self.ensure_one()
        tree_view = self.env.ref("account.view_invoice_tree", raise_if_not_found=False)
        form_view = self.env.ref("account.view_move_form", raise_if_not_found=False)
        action = {
            "type": "ir.actions.act_window",
            "name": "Invoices",
            "res_model": "account.move",
            "view_mode": "tree,kanban,form,calendar,pivot,graph,activity",
            "domain": [("id", "in", invoices)],
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action

    def action_show_po(self, purchase):
        self.ensure_one()
        tree_view = self.env.ref("purchase.purchase_order_kpis_tree", raise_if_not_found=False)
        form_view = self.env.ref("purchase.purchase_order_form", raise_if_not_found=False)
        action = {
            "type": "ir.actions.act_window",
            "name": "Purchase Order",
            "res_model": "purchase.order",
            "view_mode": "tree,kanban,form,calendar,pivot,graph,activity",
            "domain": [("id", "in", purchase)],
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action