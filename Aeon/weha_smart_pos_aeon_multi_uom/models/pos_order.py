# -*- coding: utf-8 -*-
#################################################################################
# Author      : WEHA Consultant (<www.weha-id.com>)
# Copyright(c): 2015-Present WEHA Consultant.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from itertools import groupby


import logging

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _prepare_invoice_line(self, order_line):
        result = super()._prepare_invoice_line(order_line)
        result['product_uom_id'] = order_line.product_uom.id or order_line.product_uom_id.id
        return result

    def _get_pos_anglo_saxon_price_unit2(self, product, partner_id, quantity,product_uom_id):
        moves = self.filtered(lambda o: o.partner_id.id == partner_id)\
            .mapped('picking_ids.move_ids')\
            ._filter_anglo_saxon_moves(product)\
            .sorted(lambda x: x.date)
        price_unit = product.with_company(self.company_id)._compute_average_price(0, quantity, moves)
        if product_uom_id:
            price_unit = product.uom_id.with_company(self.company_id)._compute_price(price_unit, product_uom_id)
        return price_unit


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    product_uom = fields.Many2one('uom.uom','Unit of measure')

    def _export_for_ui(self, orderline):
        res = super(PosOrderLine, self)._export_for_ui(orderline)
        if orderline.product_uom:
            res['product_uom'] = orderline.product_uom.id;
        else:
            res['product_uom'] = orderline.product_uom_id.id;
        return res


    def _launch_stock_rule_from_pos_order_lines(self):

        procurements = []
        for line in self:
            line = line.with_company(line.company_id)
            if not line.product_id.type in ('consu','product'):
                continue

            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
                line.order_id.procurement_group_id = group_id

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.qty

            # procurement_uom = line.product_id.uom_id
            procurement_uom = line.product_uom or line.product_uom_id
            procurements.append(self.env['procurement.group'].Procurement(
                line.product_id, product_qty, procurement_uom,
                line.order_id.partner_id.property_stock_customer,
                line.name, line.order_id.name, line.order_id.company_id, values))
        if procurements:
            self.env['procurement.group'].run(procurements)

        # This next block is currently needed only because the scheduler trigger is done by picking confirmation rather than stock.move confirmation
        orders = self.mapped('order_id')
        for order in orders:
            pickings_to_confirm = order.picking_ids
            if pickings_to_confirm:
                # Trigger the Scheduler for Pickings
                pickings_to_confirm.action_confirm()
                tracked_lines = order.lines.filtered(lambda l: l.product_id.tracking != 'none')

                lines_by_tracked_product = groupby(sorted(tracked_lines, key=lambda l: l.product_id.id), key=lambda l: (l.product_id.id,l.product_uom.id))
                
                for product_id, lines in lines_by_tracked_product:
                    lines = self.env['pos.order.line'].concat(*lines)
                    moves = pickings_to_confirm.move_ids.filtered(lambda m: m.product_id.id == product_id)
                    moves.move_line_ids.unlink()
                    moves._add_mls_related_to_order(lines, are_qties_done=False)
                    moves._recompute_state()
        return True
