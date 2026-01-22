from odoo import _, api, fields, models
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import time
import threading

import logging

_logger = logging.getLogger(__name__)


class SettlementProcess(models.Model):
    _name = "settlement.process"
    _description = "Settlement"

    def open_rebate_settlement(self):
        self.ensure_one()
        tree_view = self.env.ref("weha_agreement_management.view_contract_rebate_settlement_tree", raise_if_not_found=False)
        form_view = self.env.ref("weha_agreement_management.view_contract_rebate_settlement_form", raise_if_not_found=False)
        action = {
            "type": "ir.actions.act_window",
            "name": "Rebate Settlement",
            "res_model": "contract.rebate.settlement",
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

        sql="""SELECT supplier_id, contract_id, bu_id, store_id
                FROM contract_rebate_settlement
                WHERE settlement_id={}
                GROUP BY supplier_id, contract_id, bu_id, store_id
                ORDER BY supplier_id""".format(self.id)
        self.env.cr.execute(sql)
        groups = self.env.cr.dictfetchall()
        for group in groups:
            args = [('settlement_id','=', self.id), ('supplier_id','=', group['supplier_id']), 
                    ('contract_id','=', group['contract_id']), ('bu_id','=', group['bu_id']), ('store_id','=', group['store_id']),]
            rebate_ids = self.env['contract.rebate.settlement'].search(args)
            if len(rebate_ids) != 0:
                rebate_list=[]
                for rebate in rebate_ids:
                    if rebate.net_purchase != 0:
                        subtotal = rebate.net_purchase
                    else:
                        subtotal = rebate.rebate_amount
                    rebate_list.append(
                        (0,0, {
                            'name': 'REBATE - ' + str(rebate.name) + ' - ' + str(rebate.deduction_id.name),
                            'account_id': rebate.deduction_id.account_id.id,
                            'price_unit': subtotal,
                            'quantity': 1.0,
                            'discount': 0.0,
                            'tax_ids': False,
                            'product_uom_id': rebate_product.uom_id.id,
                            'product_id': rebate_product.id
                        })
                    )

                vals={}
                vals.update({
                    'partner_id': group['supplier_id'],
                    'currency_id': self.env.user.company_id.currency_id.id,
                    'move_type': 'in_refund',
                    'invoice_date': datetime.now(),
                    'journal_id': self.env.user.company_id.journal_id.id,
                    'settlement_id': self.id,
                    'bu_id': group['bu_id'],
                    'branch_id': group['store_id'],
                    'contract_id': group['contract_id'],
                    'invoice_line_ids': rebate_list
                })

                _logger.info('.....DATA TO INVOICE')
                _logger.info(vals)
                resc = account_move_obj.sudo().create(vals)
        self.state = 'posted'
        return self.open_invoice()
     
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
        time.sleep(3)
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            rebate_settlement_obj = self.env['contract.rebate.settlement']
            from_date = self.start_date
            to_date = self.end_date
            start_date = str(from_date.year) + "-" + str(from_date.month).zfill(2) + "-" + str(from_date.day).zfill(2) + " 00:00:00"
            end_date = str(to_date.year) + "-" + str(to_date.month).zfill(2) + "-" + str(to_date.day).zfill(2) + " 23:59:59"
            date_today = datetime.now().date()
            domain = self._domain_args()
            sql_sales="""SELECT b.supplier_id, b.agreement_contract_id, b.bu_id, b.branch_id as store_id, d.deduction_id, d.payment_periode, d.expenses_type,
                CASE WHEN d.expenses_type = 'percent' THEN sum(a.price_subtotal*(d.rebate_value/100))
                WHEN d.expenses_type = 'amount' THEN (d.rebate_value)
                END AS total
                FROM pos_order_line a
                LEFT JOIN product_template b ON a.product_id=b.id
                LEFT JOIN agreement_contract c ON b.agreement_contract_id=c.id
                LEFT JOIN contract_rebate d ON c.id=d.contract_id
                WHERE a.is_settlement='f' {} AND d.start_date<='{}' AND d.end_date>='{}' AND a.create_date BETWEEN '{}' AND '{}'
                GROUP BY b.supplier_id, b.agreement_contract_id, b.bu_id, b.branch_id, d.expenses_type, 
                d.rebate_value, d.deduction_id, d.payment_periode""".format(domain, date_today, date_today, start_date, end_date)
            self.env.cr.execute(sql_sales)
            orders_sales = self.env.cr.dictfetchall()
            _logger.info(sql_sales)
            _logger.info(orders_sales)

            # orders_sales = self.calculate_rebate_sales(self._domain_args())
            if len(orders_sales) != 0:
                for rec in orders_sales:
                    vals={}
                    vals.update({'supplier_id': rec['supplier_id']})
                    vals.update({'contract_id': rec['agreement_contract_id']})
                    vals.update({'bu_id': rec['bu_id']})
                    vals.update({'store_id': rec['store_id']})
                    vals.update({'payment_periode': rec['payment_periode']})
                    vals.update({'deduction_id': rec['deduction_id']})
                    if rec['expenses_type'] == 'percent':
                        vals.update({'rebate_amount': rec['total']})
                    else:
                        vals.update({'net_purchase': rec['total']})
                    vals.update({'settlement_id': self.id})
                    _logger.info("____REBATE")
                    _logger.info(vals)
                    # CREATE OUTRIGHT SETTLEMENT
                    res = rebate_settlement_obj.sudo().create(vals)
                    self.state = 'confirm'
            new_cr.commit()
        # return self.open_rebate_settlement()
        # return {}

    def generate_settlement(self):
        _logger.info("Start Processing.")
        start_time = time.time()
        thread = threading.Thread(target=self.calculate,)
        thread.start()
        end_time = time.time()
        _logger.info("List processing complete.")
        total_time = end_time - start_time
        _logger.info("multithreading time=")
        _logger.info(str(total_time))
        # self.state = 'confirm'

    def generate_settlement_confirm(self):
        from_date = self.start_date
        to_date = self.end_date
        start_date = str(from_date.year) + "-" + str(from_date.month).zfill(2) + "-" + str(from_date.day).zfill(2) + " 00:00:00"
        end_date = str(to_date.year) + "-" + str(to_date.month).zfill(2) + "-" + str(to_date.day).zfill(2) + " 23:59:59"
        date_today = datetime.now().date()
        domain = self._domain_args()

        # flag rebate onetime
        sql_update="""SELECT b.agreement_contract_id
            FROM pos_order_line a
            LEFT JOIN product_template b ON a.product_id=b.id
            LEFT JOIN agreement_contract c ON b.agreement_contract_id=c.id
            LEFT JOIN contract_rebate d ON c.id=d.contract_id
            WHERE a.is_settlement='f' {} AND d.start_date<='{}' AND d.end_date>='{}' AND a.create_date BETWEEN '{}' AND '{}'
            GROUP BY b.agreement_contract_id""".format(domain, date_today, date_today, start_date, end_date)
        self.env.cr.execute(sql_update)
        orders = self.env.cr.dictfetchall()
        if len(orders) != 0:
            for order in orders:
                sql="""UPDATE contract_rebate SET is_process='t' WHERE is_process='f' AND payment_periode='onetime' AND contract_id={}""".format(order['agreement_contract_id'])
                self.env.cr.execute(sql)

        # flag pos order
        sql_update="""UPDATE pos_order_line z
                    SET is_settlement='t'
                    FROM pos_order_line a
                    LEFT JOIN product_template b ON a.product_id=b.id
                    LEFT JOIN agreement_contract c ON b.agreement_contract_id=c.id
                    LEFT JOIN contract_rebate d ON c.id=d.contract_id
                    WHERE a.is_settlement='f' {} AND d.start_date<='{}' AND d.end_date>='{}' AND a.create_date BETWEEN '{}' AND '{}' AND z.product_id=b.id 
                    AND b.agreement_contract_id=c.id AND c.id=d.contract_id""".format(domain, date_today, date_today, start_date, end_date)
        self.env.cr.execute(sql_update)
        self.env.cr.commit()

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
