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
from datetime import datetime, date

import logging
_logger = logging.getLogger(__name__)



class ProductPriceChange(models.Model):
    _name = 'product.price.change'
    
    def action_view_product(self):
        return {
            'name': _('Products'),
            'res_model': 'product.price.change.line',
            'view_mode': 'tree',
            'views': [
                (self.env.ref('weha_smart_pos_aeon_price_change.product_price_change_line_view_tree').id, 'tree'),                
                ],
            'type': 'ir.actions.act_window',
            'domain': [('price_change_id', 'in', self.ids)],
        }

    def action_generate(self):
        self.line_ids.unlink()
        if self.is_product_only:
            for product_template in self.product_template_ids:
                vals = {
                    'price_change_id': self.id,
                    'product_template_id': product_template.id,
                    'fixed_price': product_template.list_price
                }
                self.env['product.price.change.line'].create(vals)

    def action_process(self):        
        for line in self.line_ids:
            vals = {
                'pricelist_id': self.product_price_list_id.id,
                'product_tmpl_id': line.product_template_id.id,
                'product_id': line.product_product_id or line.product_template_id.id,
                'min_quantity': line.min_quantity,
                'fixed_price': line.fixed_price,
                'date_start': line.date_start,
                'date_end': line.date_end
            }
            self.env['product.pricelist.item'].create(vals)

    def action_request_approval(self):
        pass

    def action_approve(self):
        pass

    def action_reject(self):
        pass 
    
    def _compute_line_count(self):
        for row in self:
            row.line_count = len(row.line_ids)

    @api.onchange('branch_id')
    def onchange_branch_id(self):
        domain = [
            ('branch_id','=', self.branch_id.id)
        ]
        product_pricelist_id = self.env['product.pricelist'].search(domain, limit=1)
        _logger.info(product_pricelist_id)
        if product_pricelist_id:
            self.product_price_list_id = product_pricelist_id.id
        else:
            self.product_price_list_id = False
            raise ValidationError(_('Store product pricelist not found, Please define product pricelist on this store!'))

    name = fields.Char('Name', size=250)
    date = fields.Date('Date', default=date.today())
    branch_id = fields.Many2one('res.branch', 'Store')
    product_price_list_id = fields.Many2one('product.pricelist', 'Store Pricelist')
    is_product_only = fields.Boolean('Product Only', default=False)
    res_line_ids = fields.Many2many('res.line','price_change_res_line_rel','product_price_change_id','res_line_id','Lines')
    res_division_ids = fields.Many2many('res.division','price_change_res_division_rel','product_price_change_id','res_division_id','Divisions')    
    res_group_ids = fields.Many2many('res.group','price_change_res_group_rel','product_price_change_id','res_group_id','Groups')    
    res_department_ids = fields.Many2many('res.department','price_change_res_department_rel','product_price_change_id','res_department_id','Departments')    
    product_category_ids = fields.Many2many('product.category','price_change_product_category_rel','product_price_change_id','product_category_id','Categories')
    product_template_ids = fields.Many2many('product.template','price_change_product_template_rel','product_price_change_id','product_template_id','Products')
    line_count = fields.Integer(compute='_compute_line_count')
    line_ids = fields.One2many('product.price.change.line','price_change_id','Lines')
    state = fields.Selection([('draft','New'),('request','Request Approval'),('approved','Approved'),('rejected','Rejected'),('done','Close')],'Status', default='draft')
    
class ProductPriceChangeLine(models.Model):
    _name = 'product.price.change.line'
    
    price_change_id = fields.Many2one('product.price.change', 'Price Change#', ondelete='cascade')
    product_template_id = fields.Many2one('product.template', 'Product')
    product_product_id = fields.Many2one('product.template', 'Variants')
    min_quantity = fields.Float('Quantity', default=0)
    fixed_price = fields.Float('Price')
    member_fixed_price = fields.Float('Member Price')
    date_start = fields.Datetime('Start Date')
    date_end = fields.Datetime('End Date')



