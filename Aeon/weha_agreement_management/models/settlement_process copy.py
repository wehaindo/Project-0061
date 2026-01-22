from odoo import _, api, fields, models
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import threading

import logging

_logger = logging.getLogger(__name__)


class SettlementProcess(models.Model):
    _name = "settlement.process"
    _description = "Settlement"

    def open_outrgiht_settlement(self):
        self.ensure_one()
        tree_view = self.env.ref("weha_agreement_management.view_outright_tree", raise_if_not_found=False)
        form_view = self.env.ref("weha_agreement_management.view_outright_form", raise_if_not_found=False)
        action = {
            "type": "ir.actions.act_window",
            "name": "Outright Settlement",
            "res_model": "contract.outright.settlement",
            "view_mode": "tree,kanban,form,calendar,pivot,graph,activity",
            "domain": [("settlement_id", "=", self.id)],
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action

    def open_invoice(self):
        self.ensure_one()
        tree_view = self.env.ref("account.view_invoice_tree", raise_if_not_found=False)
        form_view = self.env.ref("account.view_move_form", raise_if_not_found=False)
        action = {
            "type": "ir.actions.act_window",
            "name": "Invoices",
            "res_model": "account.move",
            "view_mode": "tree,kanban,form,calendar,pivot,graph,activity",
            "domain": [("settlement_id", "=", self.id)],
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action

    def generate_invoice(self):
        # CREATE INVOICE
        account_move_obj = self.env['account.move']
        rebate_product = self.env.user.company_id.rebate_product_id

        rebate_ids = self.env['contract.outright.settlement'].search([('state','=','draft')])
        for rebate in rebate_ids:
            supplier = rebate.supplier_id.id
            contract_id = rebate.agreement_contract_id.id
            rebate_list=[]
            for store in rebate.agreement_contract_id.branch_ids:
                settlement_sales_ids = self.env['contract.outright.settlement.sales'].search([('outright_settlement_id','=', rebate.id), ('store_id','=', store.id)])
                if len(settlement_sales_ids) != 0:
                    for rebate_sales in settlement_sales_ids:
                        rebate_list.append(
                            (0,0, {
                                'name': 'REBATE - ' + str(rebate_sales.rebate_id.code) + ' - ' + str(rebate_sales.expenses_type),
                                'account_id': rebate_sales.deduction_id.account_id.id,
                                'price_unit': rebate_sales.subtotal,
                                'quantity': 1.0,
                                'discount': 0.0,
                                'tax_ids': False,
                                'product_uom_id': rebate_product.uom_id.id,
                                'product_id': rebate_product.id
                            })
                        )
                settlement_purchase_ids = self.env['contract.outright.settlement.line'].search([('outright_settlement_id','=', rebate.id), ('store_id','=', store.id)])
                if len(settlement_purchase_ids) != 0:
                    for rebate_purchase in settlement_purchase_ids:
                        rebate_list.append(
                            (0,0, {
                                'name': 'REBATE - ' + str(rebate_purchase.rebate_id.code) + ' - ' + str(rebate_purchase.expenses_type),
                                'account_id': rebate_purchase.deduction_id.account_id.id,
                                'price_unit': rebate_purchase.subtotal,
                                'quantity': 1.0,
                                'discount': 0.0,
                                'tax_ids': False,
                                'product_uom_id': rebate_product.uom_id.id,
                                'product_id': rebate_product.id
                            })
                        )
                if len(rebate_list) != 0:
                    vals={}
                    vals.update({
                        'partner_id': supplier,
                        'currency_id': self.env.user.company_id.currency_id.id,
                        'move_type': 'in_refund',
                        'invoice_date': datetime.now(),
                        'journal_id': self.env.user.company_id.journal_id.id,
                        'settlement_id': self.id,
                        'branch_id': store.id,
                        'contract_id': contract_id,
                        'invoice_line_ids': rebate_list
                    })

                    _logger.info('.....DATA TO INVOICE')
                    _logger.info(vals)
                    resc = account_move_obj.sudo().create(vals)
        self.state = 'posted'
        return self.open_invoice()

    def calculate_rebate_sales(self, domain):

        # sql_sales="""SELECT d.id as rebate_code, sum(a.price_subtotal) as subtotal, d.expenses_type, d.rebate_value,
        #     CASE WHEN d.expenses_type = 'percent' THEN sum(a.price_subtotal*(d.rebate_value/100))
        #     WHEN d.expenses_type = 'amount' THEN (d.rebate_value)
        #     END AS total
        #     FROM pos_order_line a
        #     LEFT JOIN product_template b ON a.product_id=b.id
        #     LEFT JOIN agreement_contract c ON b.agreement_contract_id=c.id
        #     LEFT JOIN contract_rebate d ON c.id=d.contract_id
        #     WHERE a.is_settlement='f' AND d.calculate_from='sales' AND d.is_process='f' {}
        #     GROUP BY d.id, d.expenses_type, d.rebate_value""".format(domain)
        sql_sales="""SELECT b.supplier_id, b.agreement_contract_id, b.bu_id, b.branch_id as store_id, d.deduction_id, d.payment_periode, d.expenses_type,
            CASE WHEN d.expenses_type = 'percent' THEN sum(a.price_subtotal*(d.rebate_value/100))
            WHEN d.expenses_type = 'amount' THEN (d.rebate_value)
            END AS total
            FROM pos_order_line a
            LEFT JOIN product_template b ON a.product_id=b.id
            LEFT JOIN agreement_contract c ON b.agreement_contract_id=c.id
            LEFT JOIN contract_rebate d ON c.id=d.contract_id
            WHERE a.is_settlement='f' {}
            GROUP BY b.supplier_id, b.agreement_contract_id, b.bu_id, b.branch_id, d.expenses_type, d.rebate_value, d.deduction_id, d.payment_periode""".format(domain)
        self.env.cr.execute(sql_sales)
        orders = self.env.cr.dictfetchall()
        _logger.info(sql_sales)
        _logger.info(orders)
        return orders
    
    def calculate_rebate_purchase(self, contract_id=-1, store_id=-1):

        sql="""SELECT d.id as rebate_id, sum(b.qty_received * b.price_unit) as subtotal, d.expenses_type, d.rebate_value,
            CASE WHEN d.expenses_type = 'percent' THEN sum((b.qty_received*b.price_unit)*(d.rebate_value/100))
            WHEN d.expenses_type = 'amount' THEN (d.rebate_value)
            END AS total
            FROM purchase_order a
            LEFT JOIN purchase_order_line b ON a.id=b.order_id
            LEFT JOIN agreement_contract c ON a.agreement_contract_id=c.id
            LEFT JOIN contract_rebate d ON c.id=d.contract_id
            WHERE a.is_settlement='f' AND d.calculate_from='purchase' AND d.is_process='f' AND b.agreement_contract_id={} AND a.branch_id={}
            GROUP BY d.id, d.expenses_type, d.rebate_value""".format(contract_id, store_id)
        self.env.cr.execute(sql)
        orders = self.env.cr.dictfetchall()
        _logger.info(contract_id)
        _logger.info(store_id)
        _logger.info(orders)
        return orders
        
    def _domain_args(self):
        args = []
        sql = """ """
        if self.supplier_id:
            args.append((('supplier_id','=', self.supplier_id.id)))
            sql += """AND b.supplier_id = {} """.format(self.supplier_id.id)
        if self.contract_id:
            args.append((('agreement_contract_id','=', self.contract_id.id)))
            sql += """AND b.agreement_contract_id = {} """.format(self.contract_id.id)
        if self.store_id:
            args.append((('branch_id','=', self.store_id.id)))
            sql += """AND b.branch_id = '{}' """.format(self.store_id.id)
        if self.deduction_id:
            args.append((('deduction_id','=', self.deduction_id.id)))
            sql += """AND d.deduction_id = {} """.format(self.deduction_id.id)
        if self.payment_term_id:
            args.append((('payment_term_id','=', self.payment_term_id.id)))
            sql += """AND c.payment_term_id = {} """.format(self.payment_term_id.id)
        if self.payment_periode:
            args.append((('payment_periode','=', self.payment_periode)))
            sql += """AND d.payment_periode = '{}' """.format(self.payment_periode)

        _logger.info(sql)
        return sql
    
    def calculate(self):
        rebate_settlement_obj = self.env['contract.rebate.settlement']
        orders_sales = self.calculate_rebate_sales(self._domain_args())
        for rec in orders_sales:
            vals=[]
            vals.update({'supplier_id': rec['supplier_id.id']})
            vals.update({'contract_id': rec['agreement_contract_id']})
            vals.update({'bu_id': rec['bu_id']})
            vals.update({'store_id': rec['store_id']})
            vals.update({'payment_periode': rec['payment_periode']})
            vals.update({'deduction_id': rec['deduction_id']})
            if rec['deduction_id'] == 'percent':
                vals.update({'rebate_amount': rec['total']})
            else:
                vals.update({'net_purchase': rec['total']})
            _logger.info("____REBATE")
            _logger.info(vals)
            # CREATE OUTRIGHT SETTLEMENT
            res = rebate_settlement_obj.create(vals)
        

    def generate_settlement(self):
        outright_obj = self.env["contract.outright.settlement"]
        contract_obj = self.env["agreement.contract"]
        term_day = 1
        for term in self.payment_term_id.line_ids:
            term_day = term.days
        date_now = datetime.now()
        term_date = date_now + relativedelta(day=term_day)
        date_now =  fields.Date.to_string(date_now)

        # CHECK CONTRACT AND TERM CONDITION
        contract_ids = contract_obj.search([
            ('start_date','<=', date_now), ('end_date','>=', date_now)
            ])
        _logger.info('____CONTRACT')
        _logger.info(contract_ids)

        for contract in contract_ids:
            vals_line=[]
            vals_sales=[]
            vals={}
            for rebate in contract.rebate_ids:
                if rebate.calculate_from == "sales":
                    orders_sales = self.calculate_rebate_sales(self._domain_args())
                    for rec in orders_sales:
                        vals_sales.append((
                            (0,0, {
                                    'rebate_id': rec['rebate_code'],
                                    'total_sales': rec['subtotal'],
                                    'expenses_type': rec['expenses_type'],
                                    'rebate_value': rec['rebate_value'],
                                    'subtotal': rec['total']
                                })
                        ))
                    _logger.info("__orders_sales")
                    _logger.info(orders_sales)
                if rebate.calculate_from == "purchase":
                    orders = self.calculate_rebate_purchase(contract.id, rebate.store_id.id)
                    for order in orders:
                        vals_line.append((
                            (0,0, {
                                    'rebate_id': order['rebate_id'],
                                    'total_po': order['subtotal'],
                                    'expenses_type': order['expenses_type'],
                                    'rebate_value': order['rebate_value'],
                                    'subtotal': order['total']
                                })
                        ))
                    _logger.info("__orders_purchase")
                    _logger.info(orders)
            if len(vals_line) == 0 and len(vals_sales) == 0:
                pass
            else:
                vals.update({'supplier_id': contract.supplier_id.id})
                vals.update({'settlement_id': self.id})
                vals.update({'agreement_contract_id': contract.id})
                vals.update({'payment_term_id': contract.payment_term_id.id})
                vals.update({'outright_settlement_line_ids': vals_line})
                vals.update({'outright_settlement_sales_ids': vals_sales})
                _logger.info("____OUTRIGHT")
                _logger.info(vals)
                # CREATE OUTRIGHT SETTLEMENT
                res = outright_obj.sudo().create(vals)

        self.state = 'confirm'
        return self.open_outrgiht_settlement()

    def generate_settlement_confirm(self):
        contract_obj = self.env["agreement.contract"]
        term_day = 1
        for term in self.payment_term_id.line_ids:
            term_day = term.days
        date_now = datetime.now()
        term_date = date_now + relativedelta(day=term_day)
        date_now =  fields.Date.to_string(date_now)

        contract_ids = contract_obj.search([
            ('start_date','<=', date_now), ('end_date','>=', date_now)
            ])
        for contract in contract_ids:
            # flag ontime rebate
            sql_update="""UPDATE contract_rebate SET is_process='t'
                WHERE contract_id={} AND payment_periode='onetime'""".format(contract.id)
            self.env.cr.execute(sql_update)
            
            # flag purchase order
            order_line_ids = self.env['purchase.order'].search([('is_settlement','=', False),('agreement_contract_id','=', contract.id)])
            for order in order_line_ids:
                order.is_settlement=True
            # sql_update_order="""UPDATE purchase_order a SET a.is_settlement='t'
            #     LEFT JOIN purchase_order_line b ON a.id=b.order_id
            #     WHERE a.is_settlement='f' AND b.agreement_contract_id={}""".format(contract.id)
            # self.env.cr.execute(sql_update_order)

            # flag pos order line
            pos_order_line_ids = self.env['pos.order.line'].search([('is_settlement','=', False),])
            for posorder in pos_order_line_ids:
                if posorder.product_id.agreement_contract_id.id == contract.id:
                    posorder.is_settlement=True

            # sql_update_sales="""UPDATE pos_order_line a SET a.is_settlement='t'
            #     LEFT JOIN product_template b ON a.product_id=b.id
            #     WHERE a.is_settlement='f' AND b.agreement_contract_id={}""".format(contract.id)
            # self.env.cr.execute(sql_update_sales)

        self.state = 'inprogress'
        

    name = fields.Char(
        string='name'
    )
    start_date = fields.Date(required=True, )
    end_date = fields.Date(required=True, )
    date = fields.Date(default=fields.Date.today)
    contract_id = fields.Many2one(
        string='Supplier Contract',
        comodel_name='agreement.contract',
        ondelete='set null',
    )
    supplier_sub_type = fields.Selection(
        string='Supplier Type',
        selection=[('concessionaire', 'Concessionaire'), ('outright', 'Outright')],
    )
    payment_term_id = fields.Many2one(
        string='Credit Term',
        comodel_name='account.payment.term',
        ondelete='set null',
    )
    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
        ondelete='set null',
    )
    store_id = fields.Many2one(
        string='Store',
        comodel_name='res.branch',
        ondelete='set null',
    )
    deduction_id = fields.Many2one(
        string='Transaction Type',
        comodel_name='contract.deduction',
        ondelete='set null',
    )
    payment_periode = fields.Selection(
        string='Payment Periode',
        selection=[('onetime', 'One Time'), ('monthly', 'Monthly')]
    )
    state = fields.Selection(
        string='state',
        selection=[('draft', 'Draft'), ('confirm', 'Confirmed'), ('inprogress', 'Inprogress'), ('posted', 'Posted')],
        default="draft"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("rebate.process")
        return super(SettlementProcess, self).create(vals_list)
