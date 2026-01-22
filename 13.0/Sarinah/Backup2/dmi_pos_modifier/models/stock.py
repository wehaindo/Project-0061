# # -*- coding: utf-8 -*-
#
# from odoo import models, fields, api
#
#
# class InheritStockPicking(models.Model):
#     _inherit = 'stock.picking'
#
#     type_warehouse_department_id = fields.Many2one('hr.department', string="Department" , compute='_get_department_id', store=True)
#     type_warehouse_department_ids = fields.Many2many('hr.department', string="Department" , compute='_get_department_id', store=True)
#     @api.depends('picking_type_id')
#     def _get_department_id(self):
#         for rec in self:
#             print(rec)
#             rec.type_warehouse_department_id = rec.picking_type_id.warehouse_id.department_id
#             rec.type_warehouse_department_ids = rec.picking_type_id.warehouse_id.allowed_department_ids
