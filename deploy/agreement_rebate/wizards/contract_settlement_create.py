# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

import logging

_logger = logging.getLogger(__name__)


class ContractSettlementCreateWiz(models.TransientModel):
    _name = "contract.settlement.create.wiz"
    _description = "Contract settlement create wizard"

    date = fields.Date(default=fields.Date.today)
    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)
    supplier_sub_type = fields.Selection(
        string='Supplier Type',
        selection=[('concessionaire', 'Concessionaire'), ('outright', 'Outright')],
        store=True,
        required=True
    )
    jurnal_id = fields.Many2one(
        string='jurnal',
        comodel_name='account.journal',
        ondelete='restrict',
        required=False
    )

    def _prepare_agreement_domain(self, partner=False):
        domain = []
        if self.date_from:
            domain.extend(
                ["|", ("end_date", "=", False), ("end_date", ">=", self.date_from)]
            )
        if self.date_to:
            domain.extend([("start_date", "<=", self.date_to)])

        if self.supplier_sub_type:
            domain.extend([("supplier_sub_type", "=", self.supplier_sub_type)])
            
        if partner:
            domain.extend([("partner_id", "=", partner)])

        return domain

    def _prepare_agreement_conces_domain(self):
        domain = []
        if self.date_from:
            domain.extend(
                ["|", ("end_date", "=", False), ("end_date", ">=", self.date_from)]
            )
        if self.date_to:
            domain.extend([("start_date", "<=", self.date_to)])

        if self.supplier_sub_type:
            domain.extend([("supplier_sub_type", "=", self.supplier_sub_type)])

        return domain
 
    def action_create_settlement(self):
        agreement_obj = self.env["agreement"]
        outright_obj = self.env["contract.outright.settlement"]
        conces_obj = self.env["contract.conces.settlement"]

        if self.supplier_sub_type == 'outright':
            po_obj = self.env["purchase.order"]
            vals_list = {}
            domain = [
                    ("date_planned",">=", fields.Date.to_string(self.date_from)),
                    ("date_planned","<=", fields.Date.to_string(self.date_to)),
                    ("is_settlement","=", False)
                    ]
            po_ids = po_obj.search(domain)
            vals = []
            for po in po_ids:
                partner = po.partner_id.id
                agreement_ids = agreement_obj.search(self._prepare_agreement_domain(partner))
                for agr in agreement_ids:
                    domain_order = [('order_id','=', po.id),('product_id','in', agr.rebate_product_product_ids.ids)] 
                    po_order_line_ids = self.env["purchase.order.line"].search(domain_order)
                    # self.env.cr.execute(query)
                    # po_order_line_ids = self.env.cr.dictfetchall()
                    vals_product = []
                    pro = False
                    for line in po_order_line_ids:
                        if line:
                            price = line.price_unit
                            qty = line.qty_received
                            total = (price*qty)
                            disc = (agr.rebate_discount/100)
                            subtotal = (disc*total)
                            vals_product.append((
                                    (0,0, {
                                            'product_id': line.product_id.id,
                                            'amount_po': total,
                                            'discount': agr.rebate_discount,
                                            'amount_rebate': subtotal
                                        })
                                ))
                            pro = True
                        else:
                            pro = False

                    if pro != False: 
                        vals.append((
                            (0,0, {
                            'purchase_id': po.id,
                            'partner_id': po.partner_id.id,
                            'agreement_id': agr.id,
                            'is_invoice': False,
                            'outright_settlement_product_ids': vals_product})
                        ))
                
                po.is_settlement=True

            vals_list.update({
                "date": self.date,
                "date_from": self.date_from,
                "date_to": self.date_to,
                "outright_settlement_line_ids": vals
            })
            res = outright_obj.create(vals_list)
            if res:
                _logger.info("......OUTRIGHT")
                _logger.info(vals_list)
                return self.action_show_outrght(res.id)
            else:
                raise UserError(_("Can not create settlement outright!."))

        else:
            pos_order_line_obj = self.env["pos.order.line"]
            agreement_ids = agreement_obj.search(self._prepare_agreement_conces_domain())
            vals_list = {}
            vals = []
            for agr in agreement_ids:
                domain = [
                    ("create_date",">=", fields.Date.to_string(self.date_from)),
                    ("create_date","<=", fields.Date.to_string(self.date_to)),
                    ("product_id","in", agr.rebate_product_product_ids.ids)
                    ]
                val = True
                lis=""
                for line in agr.rebate_product_product_ids:
                    if val: 
                        data=""
                        val = False
                    else: 
                        data=" or "
                    lis += data+"product_id="+str(line.id)
                _logger.info('......DATA')
                _logger.info(lis)
                query = '''
                    SELECT product_id, sum(qty) as qty_total, sum(price_subtotal) as subtotal
                    FROM pos_order_line
                    WHERE is_settlement='f' AND {}
                    GROUP BY product_id
                    ORDER BY product_id
                '''.format(lis)
                self.env.cr.execute(query)
                _logger.info(query)
                pos_order_line_ids = self.env.cr.dictfetchall()
                # for val in query_result:
                # #     date = val['date']
                # pos_order_line_ids = pos_order_line_obj.read_group(domain=domain,
                #         fields=['product_id','qty_total:sum(qty)'],
                #         groupby=['product_id'],
                #         lazy=False,)
                _logger.info("......LIST DOMAIN PRODUCT")
                _logger.info(pos_order_line_ids)
                pro = False
                vals_product = []
                for group in pos_order_line_ids:
                    product_id=group['product_id']
                    product_ids=self.env['product.product'].browse(product_id)
                    if product_ids:
                        qty=group['qty_total']
                        subtotal=group['subtotal']
                        total = (subtotal/qty)
                        rebate_disc = (agr.rebate_discount/100)
                        grand_total = total - (rebate_disc*total)
                        # _logger.info(product_ids.list_price)
                        vals_product.append((
                                (0,0, {
                                        'product_id': product_id,
                                        'qty': qty,
                                        'amount_po': total,
                                        'discount': agr.rebate_discount,
                                        'amount_rebate': grand_total
                                    })
                            ))
                        pro = True
                    else:
                        pro = False

                if pro != False: 
                    vals.append((
                        (0,0, {
                        'partner_id': agr.partner_id.id,
                        'agreement_id': agr.id,
                        'is_po': False,
                        'conces_settlement_product_ids': vals_product})
                    ))

                order_line = pos_order_line_obj.search(domain)
                order_line.write({'is_settlement': True})

            vals_list.update({
                "date": self.date,
                "date_from": self.date_from,
                "date_to": self.date_to,
                "conces_settlement_line_ids": vals
            })
            res = conces_obj.create(vals_list)
            if res:
                _logger.info("......CONCES")
                _logger.info(vals_list)
                return self.action_show_conces(res.id)
            else:
                raise UserError(_("Can not create settlement consigment!."))
    
    def action_show_conces(self, conces):
        self.ensure_one()
        tree_view = self.env.ref("agreement_rebate.view_conces_tree", raise_if_not_found=False)
        form_view = self.env.ref("agreement_rebate.view_conces_form", raise_if_not_found=False)
        action = {
            "type": "ir.actions.act_window",
            "name": "Consigment Settlement",
            "res_model": "contract.conces.settlement",
            "view_mode": "tree,kanban,form,calendar,pivot,graph,activity",
            "res_id": conces,
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action

    def action_show_outrght(self, outright):
        self.ensure_one()
        tree_view = self.env.ref("agreement_rebate.view_outright_tree", raise_if_not_found=False)
        form_view = self.env.ref("agreement_rebate.view_outright_form", raise_if_not_found=False)
        action = {
            "type": "ir.actions.act_window",
            "name": "Outright Settlement",
            "res_model": "contract.outright.settlement",
            "view_mode": "tree,kanban,form,calendar,pivot,graph,activity",
            "res_id": outright,
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action





    