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
import threading
import time

import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def update_store_product(self, vals):
        super(ProductTemplate, self).update_store_product(vals)
        # self.generate_decentralize_by_branch(vals['res_branch_id'],'C')
    
    def remove_product(self, branch):
        super(ProductTemplate, self).remove_product(branch)
        # self.generate_decentralize_by_branch(branch,'U')

    def generate_decentralize_by_branch(self, branch, type):
        _logger.info('generate_decentralize_by_branch')
        for row in self:
            #Product Template Format
            # Digit 1    (1)    : C (Add), W (Update), U (Delete)
            # Digit 2-5  (4)    : Store Code
            # Digit 6-15 (10)   : Server ID
            # Digit 16-24 (9)   : SKU 007958038
            # Digit 25-30 (6)   : Sub Category
            # Digit 31-39 (9)   : 3 Taxes 1 Tax 3 Digit but from profit only 2 digit so remove leading zero for tax code
            # Digit 40-54 (15)  : Price
            # Digit 55-57 (3)   : UOM 
            # Digit 58-87 (30)  : Product Name

            # branch= '7001'
            _logger.info(branch)
            branch_id = self.env['res.branch'].browse(branch)            
            _logger.info(branch_id)
            server_id = str(row.id).rjust(10,'0')
            _logger.info(server_id)
            sku = row.default_code
            _logger.info(sku)
            sub_category = row.sub_categ_id.code
            _logger.info(sub_category)
            taxes = ''
            for tax in row.taxes_id:
                if tax.code:
                    taxes = taxes + tax.code.rjust(3,'0')
            taxes = taxes.ljust(9,'0')       
            _logger.info(taxes)            
            price_id = self.env['product.template.price'].search([('res_branch_id','=',branch_id.id),('product_template_id','=', row.id)], limit=1)
            _logger.info(price_id.list_price)            
            price = ('%.2f' %  price_id.list_price).rjust(15,'0')
            _logger.info(price)
            uom = row.uom_id.code
            _logger.info(uom)
            product_name = row.name[0:30].ljust(30,' ')
            _logger.info(product_name)
            
            data = type + branch_id.code + server_id + sku + sub_category + taxes + price + uom + product_name
            _logger.info(data)
            vals = {
                'branch_id': branch_id.id, 
                'data_type': 'product',
                'reference': '',
                'data':data,
            }
            self.env['pos.decentralize'].create(vals)
                 
    def generate_decentralize(self, branch, date_start=False, date_end=False):        
        if not date_start or not date_end:
            domain = [
                ('branch_ids','in',[branch])
            ]
        else:                    
            domain = [
                ('branch_ids','in',[branch]),
                ('write_date','>=', date_start), # date_start utc
                ('write_date','<=', date_end) # date_end utc
            ]
        _logger.info(domain)
        product_template_ids = self.env['product.template'].search(domain).ids
        
        domain = [
            ('product_tmpl_id', 'in' , product_template_ids)
        ]
        product_ids = self.env['product.product'].search(domain)    
        _logger.info('generate_decentralize')
        for row in product_ids:
            #Product Template Format
            # Digit 1    (1)    : C (Add), W (Update), U (Delete)
            # Digit 2-5  (4)    : Store Code
            # Digit 6-15 (10)   : Server ID
            # Digit 16-24 (9)   : SKU 007958038
            # Digit 25-30 (6)   : Sub Category
            # Digit 31-39 (9)   : 3 Taxes 1 Tax 3 Digit but from profit only 2 digit so remove leading zero for tax code
            # Digit 40-54 (15)  : Price
            # Digit 55-57 (3)   : UOM 
            # Digit 58-87 (30)  : Product Name

            # branch= '7001'
            _logger.info(branch)
            branch_id = self.env['res.branch'].browse(branch)            
            _logger.info(branch_id)
            server_id = str(row.id).rjust(10,'0')
            _logger.info(server_id)
            sku = row.default_code
            _logger.info(sku)
            sub_category = row.sub_categ_id.code
            _logger.info(sub_category)
            taxes = ''
            for tax in row.taxes_id:
                taxes = taxes + str(tax.code).rjust(3,'0')
            taxes = taxes.ljust(9,'0')       
            _logger.info(taxes)            
            price_id = self.env['product.template.price'].search([('res_branch_id','=',branch_id.id),('product_template_id','=', row.product_tmpl_id.id)], limit=1)
            _logger.info(price_id.list_price)            
            price = ('%.2f' %  price_id.list_price).rjust(15,'0')
            _logger.info(price)
            uom = str(row.uom_id.id).rjust(3,'0')
            _logger.info(uom)
            product_name = row.name[0:30].ljust(30,' ')
            _logger.info(product_name)
            type = ''
            if row.create_date == row.write_date:
                type = 'C'
            else:
                type = 'U'
            try:
                data = type + branch_id.code + server_id + sku + sub_category + taxes + price + uom + product_name
                _logger.info(data)
                vals = {
                    'branch_id': branch_id.id, 
                    'data_type': 'product',
                    'res_id': row.id,
                    'reference': '',
                    'data':data,
                }
                self.env['pos.decentralize'].create(vals)
                self.env.cr.commit()
            except Exception as e:
                _logger.error(e)

    def _process_generate_decentralize(self, branch, date_start=False, date_end=False):
        _logger.info("_process_generate_decentralize")
        active_id = self.id
        with api.Environment.manage(), self.pool.cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            self.env['product.template'].generate_decentralize(branch, date_start, date_end)
            
    def background_process_process(self, branch, date_start=False, date_end=False):
        threaded_process = threading.Thread(target=self._process_generate_decentralize, args=(branch, date_start, date_end))
        threaded_process.start()
        
        