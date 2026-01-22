# -*- coding: utf-8 -*-

import logging
from datetime import timedelta
from functools import partial
import psycopg2
from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
import odoo.addons.decimal_precision as dp
from itertools import groupby
from odoo.tools.misc import formatLang, get_lang
import json

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config' 

    allow_multi_uom = fields.Boolean('Product Multi Uom', default=True)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_multi_uom = fields.Boolean(related='pos_config_id.allow_multi_uom', readonly=False)


class ProductMultiUom(models.Model):
    _name = 'product.multi.uom'
    _order = "sequence desc"

    multi_uom_id = fields.Many2one('uom.uom','Unit of measure')
    price = fields.Float("Sale Price",default=0)
    sequence = fields.Integer("Sequence",default=1)
    barcode = fields.Char("Barcode")
    uom_name = fields.Char("UOM Product Name")
    product_tmp_id = fields.Many2one("product.template",string="Product")
    product_id = fields.Many2one("product.product",string="Product")

    # @api.depends('product_tmp_id')
    # def _compute_product_tmp_id(self):
    #     for record in self:
    #         if record.product_tmp_id:
    #             record.product_id = record.product_tmp_id.product_tmp_id.ids[0]

    # @api.multi
    @api.onchange('multi_uom_id')
    def unit_id_change(self):
        domain = {'multi_uom_id': [('category_id', '=', self.product_tmp_id.uom_id.category_id.id)]}        
        return {'domain': domain}

    # @api.model
    # def create(self, vals):
    #     if 'barcode' in vals:
    #         barcodes = self.env['product.product'].sudo().search([('barcode','=',vals['barcode'])])
    #         barcodes2 = self.search([('barcode','=',vals['barcode'])])
    #         if barcodes or barcodes2:
    #             raise UserError(_('A barcode can only be assigned to one product !'))
    #     return super(ProductMultiUom, self).create(vals)

    # # @api.multi
    # def write(self, vals):
    #     if 'barcode' in vals:
    #         barcodes = self.env['product.product'].sudo().search([('barcode','=',vals['barcode'])])
    #         barcodes2 = self.search([('barcode','=',vals['barcode'])])
    #         if barcodes or barcodes2:
    #             raise UserError(_('A barcode can only be assigned to one product !'))
    #     return super(ProductMultiUom, self).write(vals)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    has_multi_uom = fields.Boolean('Has multi UOM')
    multi_uom_ids = fields.One2many('product.multi.uom','product_tmp_id')
    new_barcode = fields.Text("New Barcode", compute="_compute_new_barcode")

    def _compute_new_barcode(self):
        for record in self:
            if record.multi_uom_ids:
                multi_uom_list = []
                for multi_uom in record.multi_uom_ids:
                    multi_uom_list.append(multi_uom.barcode)
                record.new_barcode = json.dumps(multi_uom_list)
            else:
                record.new_barcode = json.dumps([])

    # @api.model
    # def create(self, vals):
    #     if 'barcode' in vals:
    #         barcodes = self.env['product.multi.uom'].search([('barcode','=',vals['barcode'])])
    #         if barcodes:
    #             raise UserError(_('A barcode can only be assigned to one product !'))
    #     return super(ProductTemplate, self).create(vals)

    # # @api.multi
    # def write(self, vals):
    #     if 'barcode' in vals:
    #         barcodes = self.env['product.multi.uom'].search([('barcode','=',vals['barcode'])])
    #         if barcodes:
    #             raise UserError(_('A barcode can only be assigned to one product !'))
    #     return super(ProductTemplate, self).write(vals)

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

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _stock_account_get_anglo_saxon_price_unit(self):
        price_unit = super(AccountMoveLine, self)._stock_account_get_anglo_saxon_price_unit()
        order = self.move_id.pos_order_ids
        if order:
            price_unit = order._get_pos_anglo_saxon_price_unit2(self.product_id, self.move_id.partner_id.id, self.quantity,self.product_uom_id)
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


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    new_uom_domin = fields.Many2many("uom.uom")

    def _get_pricelist_price(self):
        """Compute the price given by the pricelist for the given line information.

        :return: the product sales price in the order currency (without taxes)
        :rtype: float
        """
        self.ensure_one()
        self.product_id.ensure_one()

        pricelist_rule = self.pricelist_item_id
        order_date = self.order_id.date_order or fields.Date.today()
        product = self.product_id.with_context(**self._get_product_price_context())
        qty = self.product_uom_qty or 1.0
        uom = self.product_uom or self.product_id.uom_id
        temp = True
        for wuom_id in self.product_id.multi_uom_ids:
            if wuom_id.multi_uom_id.id == uom.id:
                temp = False
                price = wuom_id.price
        if temp:
            price = pricelist_rule._compute_price(
                product, qty, uom, order_date, currency=self.currency_id)

        return price


class StockPicking(models.Model):
    _inherit='stock.picking'

    def _prepare_stock_move_vals(self, first_line, order_lines):
        res = super(StockPicking, self)._prepare_stock_move_vals(first_line, order_lines)
        res['product_uom'] = first_line.product_uom.id or first_line.product_id.uom_id.id,
        return res

    def _create_move_from_pos_order_lines(self, lines):
        self.ensure_one()
        # lines_by_product = groupby(sorted(lines, key=lambda l: l.product_id.id), key=lambda l: l.product_id.id)
        lines_by_product = groupby(sorted(lines, key=lambda l: l.product_id.id), key=lambda l: (l.product_id.id,l.product_uom.id))

        move_vals = []
        for dummy, olines in lines_by_product:
            order_lines = self.env['pos.order.line'].concat(*olines)
            move_vals.append(self._prepare_stock_move_vals(order_lines[0], order_lines))
        moves = self.env['stock.move'].create(move_vals)
        confirmed_moves = moves._action_confirm()
        confirmed_moves._add_mls_related_to_order(lines, are_qties_done=True)


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        if self.config_id.allow_multi_uom:
            loaded_data['multi_uom_id'] = {multi_uom['id']: multi_uom for multi_uom in loaded_data['product.multi.uom']}

    @api.model
    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if self.config_id.allow_multi_uom:
            new_model = 'product.multi.uom'
            if new_model not in result:
                result.append(new_model)
        return result

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend(['has_multi_uom','multi_uom_ids','new_barcode'])
        return result

    def _loader_params_product_multi_uom(self):
        return {'search_params': {'domain': [], 'fields': ['multi_uom_id','price','barcode','uom_name'], 'load': False}}

    def _get_pos_ui_product_multi_uom(self, params):
        result = self.env['product.multi.uom'].search_read(**params['search_params'])
        for res in result:
            uom_id = self.env['uom.uom'].browse(res['multi_uom_id'])
            res['multi_uom_id'] = [uom_id.id,uom_id.name] 
        return result