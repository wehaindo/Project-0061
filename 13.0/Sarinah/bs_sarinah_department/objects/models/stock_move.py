# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'


    @api.depends('move_line_ids.qty_done', 'move_line_ids.product_uom_id', 'move_line_nosuggest_ids.qty_done')
    def _quantity_done_compute(self):
        from collections import defaultdict

        # moves = self.filtered(lambda m: not m._origin._in_onchange)  
        moves = self

        move_ids = [m.id for m in moves if m.id]
        if not move_ids:
            for move in self:
                move.quantity_done = 0
            return
        
        # move_lines = self.mapped('_get_move_lines')

        # Use raw SQL for speed
        self._cr.execute("""
            SELECT move_id, product_uom_id, SUM(qty_done)
            FROM stock_move_line
            WHERE move_id = ANY(%s)
            GROUP BY move_id, product_uom_id
        """, [move_ids])
        rows = self._cr.fetchall()

        rec = defaultdict(list)
        for move_id, uom_id, qty in rows:
            rec[move_id].append((uom_id, qty))

        uom_cache = {}
        for move in self:
            uom = move.product_uom
            lines = rec.get(move.id, [])
            total = 0.0
            for line_uom_id, qty in lines:
                if line_uom_id not in uom_cache:
                    uom_cache[line_uom_id] = self.env['uom.uom'].browse(line_uom_id)
                total += uom_cache[line_uom_id]._compute_quantity(qty, uom, round=False)
            move.quantity_done = total


    def _create_out_svl(self, forced_quantity=None):
        return super(StockMove, self.with_context({
            'department_id': self[0].location_id.department_id.id,
            'branch_id': self[0].location_id.branch_id.id,
        }))._create_out_svl(forced_quantity=forced_quantity)

    def _create_in_svl(self, forced_quantity=None):
        return super(StockMove, self.with_context({
            'department_id': self[0].location_dest_id.department_id.id,
            'branch_id': self[0].location_dest_id.branch_id.id,
        }))._create_in_svl(forced_quantity=forced_quantity)
