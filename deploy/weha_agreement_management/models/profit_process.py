from odoo import _, api, fields, models
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class ProfitProcess(models.Model):
    _name = "profit.process"
    _description = "Process Profit"


    def open_profit_details(self):
        self.ensure_one()
        tree_view = self.env.ref("weha_agreement_management.view_conces_tree", raise_if_not_found=False)
        form_view = self.env.ref("weha_agreement_management.view_conces_form", raise_if_not_found=False)
        action = {
            "type": "ir.actions.act_window",
            "name": "Conces Settlement",
            "res_model": "contract.conces.settlement",
            "view_mode": "tree,kanban,form,calendar,pivot,graph,activity",
            "domain": [("settlement_id", "=", self.id)],
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action

    def open_purchase_order(self):
        self.ensure_one()
        tree_view = self.env.ref("purchase.purchase_order_kpis_tree", raise_if_not_found=False)
        form_view = self.env.ref("purchase.purchase_order_form", raise_if_not_found=False)
        action = {
            "type": "ir.actions.act_window",
            "name": "Purchase Order",
            "res_model": "purchase.order",
            "view_mode": "tree,kanban,form,calendar,pivot,graph,activity",
            "domain": [("settlement_id", "=", self.id)],
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action

    def generate_profit(self):
        profit_obj = self.env['contract.conces.settlement']
        term_day = 1
        for term in self.payment_term_id.line_ids:
            term_day = term.days
        date_now = datetime.now()
        term_date = date_now + relativedelta(day=term_day)
        date_now =  fields.Date.to_string(date_now)

        # CHECK CONTRACT AND TERM CONDITION
        query="""SELECT c.supplier_id, b.agreement_contract_id
            FROM pos_order_line a
            LEFT JOIN product_template b ON a.product_id=b.id
            LEFT JOIN agreement_contract c ON b.agreement_contract_id=c.id
            WHERE a.is_profit='f' AND c.payment_term_id={}
            GROUP BY b.agreement_contract_id, c.supplier_id
            ORDER BY b.agreement_contract_id""".format(self.payment_term_id.id)
        self.env.cr.execute(query)
        contracts = self.env.cr.dictfetchall()
        _logger.info(contracts)
        vals={}
        vals_product=[]
        for contract in contracts:
            # CALCULATE
            sql="""SELECT a.product_id, b.agreement_contract_id, sum(a.qty) as qty, a.price_unit, (a.price_unit-a.price_unit*(c.fixed_percent/100)) as unit_price, c.fixed_percent,
                sum((a.price_unit-a.price_unit*(c.fixed_percent/100))*a.qty) as subtotal
                FROM pos_order_line a
                LEFT JOIN product_template b ON a.product_id=b.id
                LEFT JOIN agreement_contract c ON b.agreement_contract_id=c.id
                WHERE a.is_profit='f' AND b.agreement_contract_id={}
                GROUP BY b.agreement_contract_id, a.product_id, a.price_unit, c.fixed_percent
                ORDER BY b.agreement_contract_id
                """.format(contract['agreement_contract_id'])
            self.env.cr.execute(sql)
            profits = self.env.cr.dictfetchall()
            _logger.info(profits)
            for profit in profits:
                vals_product.append((
                    (0,0, {
                            'product_id': profit['product_id'],
                            'qty': profit['qty'],
                            'unit_price': profit['unit_price'],
                            'discount': profit['fixed_percent'],
                            'subtotal': profit['subtotal']
                        })
                ))

            vals.update({
                "supplier_id": contract['supplier_id'],
                "settlement_id": self.id,
                "agreement_contract_id": contract['agreement_contract_id'],
                "payment_term_id": self.payment_term_id.id,
                "conces_settlement_line_ids": vals_product
            })

            _logger.info('____VALS')
            _logger.info(vals)
            # CREATE PROFIT
            res = profit_obj.create(vals)

        self.state='confirm'
        return self.open_profit_details()

    def confirm_profit(self):
        # FLAG UPDATE
        pos_order_line_ids = self.env['pos.order.line'].search([('is_profit','=', False),])
        for order in pos_order_line_ids:
            if order.product_id.agreement_contract_id.payment_term_id.id == self.payment_term_id.id:
                order.is_profit=True

        # sql_update="""UPDATE pos_order_line a SET a.is_profit='t'
        #     LEFT JOIN product_template b ON a.product_id=b.id
        #     LEFT JOIN agreement_contract c ON b.agreement_contract_id=c.id
        #     WHERE c.payment_term_id={}""".format(self.payment_term_id.id)
        # self.env.cr.execute(sql_update)
        self.state = 'inprogress'

    def generate_po(self):
        purchase_obj = self.env['purchase.order']
        sql="""SELECT agreement_contract_id
            FROM contract_conces_settlement
            WHERE state='draft' AND settlement_id={}
            GROUP BY agreement_contract_id""".format(self.id)
        self.env.cr.execute(sql)
        contracts = self.env.cr.dictfetchall()
        _logger.info(contracts)
        for contract in contracts:
            query_store="""SELECT b.store_id FROM contract_conces_settlement a
                LEFT JOIN contract_conces_settlement_line b ON a.id=b.conces_settlement_id
                WHERE a.state='draft' AND a.settlement_id={} AND a.agreement_contract_id={}
                GROUP BY b.store_id""".format(self.id, contract['agreement_contract_id'])
            self.env.cr.execute(query_store)
            store_ids = self.env.cr.dictfetchall()
            for store in store_ids:
                query="""SELECT a.name as profit_code, a.supplier_id, a.agreement_contract_id, b.product_id, b.qty, b.unit_price, b.subtotal
                    FROM contract_conces_settlement a
                    LEFT JOIN contract_conces_settlement_line b ON a.id=b.conces_settlement_id
                    WHERE a.state='draft' AND a.settlement_id={} AND a.agreement_contract_id={} AND b.store_id={}""".format(self.id, contract['agreement_contract_id'], store['store_id'])
                self.env.cr.execute(query)
                profits = self.env.cr.dictfetchall()
                supplier_id = -1
                contract_id = -1
                products=[]
                _logger.info(profits)
                for profit in profits:
                    supplier_id = profit['supplier_id']
                    contract_id = profit['agreement_contract_id']
                    products.append((
                        (0,0, {
                            'product_id': profit['product_id'],
                            'name': 'Profit : ' + profit['profit_code'],
                            'product_qty': profit['qty'],
                            'price_unit': profit['unit_price'],
                            'price_subtotal': profit['subtotal']
                        })
                    ))
                vals={}
                vals.update({
                    'company_id': self.env.user.company_id.id,
                    'currency_id': self.env.user.company_id.currency_id.id,
                    'date_order': datetime.now(),
                    'picking_type_id': 1,
                    'partner_id': supplier_id,
                    'settlement_id': self.id,
                    'agreement_contract_id': contract_id,
                    'branch_id': store['store_id'],
                    'order_line': products
                })
                _logger.info('____VALSPO')
                _logger.info(vals)
                res = purchase_obj.sudo().create(vals)
                res.button_confirm()
                stock_picking_ids = self.env['stock.picking'].search([('purchase_id','=', res.id)])
                for stock in stock_picking_ids:
                    for move in stock.move_ids:
                        move.quantity_done = move.product_uom_qty
                stock_picking_ids.button_validate()
                res.action_create_invoice()


        # button_confirm() -> stock.picking -> button_validate()
        self.state='posted'
        return self.open_purchase_order()


    name = fields.Char(
        string='name'
    )
    date = fields.Date(default=fields.Date.today)
    payment_term_id = fields.Many2one(
        string='Credit Term',
        comodel_name='account.payment.term',
        ondelete='restrict',
    )
    state = fields.Selection(
        string='state',
        selection=[('draft', 'Draft'), ('confirm', 'Confirmed'), ('inprogress', 'Inprogress'), ('posted', 'Posted')],
        default="draft"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("profit.process")
        return super(ProfitProcess, self).create(vals_list)