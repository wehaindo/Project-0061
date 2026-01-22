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
import threading
import time

import logging
_logger = logging.getLogger(__name__)


class ProductProductBarcode(models.Model):
    _inherit = 'product.product.barcode'

    def generate_decentralize_by_branch(self, branch=False, type=False):
        _logger.info('generate_decentralize_by_branch')
        for row in self:
            #Product Barcode Format
            # Digit 1    (1)    : C (Add), W (Update), U (Delete)
            # Digit 2-5  (4)    : Store Code
            # Digit 6-15 (10)   : Server ID
            # Digit 16-24 (9)   : SKU
            # Digit 25-42 (18)  : Barcode
            
            # branch= '7001'
            branch_id = self.env['res.branch'].search([('code','=',branch)], limit=1)            
            server_id = str(row.id).rjust(10,'0')        
            sku = row.product_id.default_code
            barcode = row.barcode.ljust(18,'0')
            
            try: 
                data = type + branch + server_id + sku + barcode
                vals = {
                    'branch_id': branch_id.id, 
                    'data_type': 'barcode',
                    'reference': '',
                    'data':data,
                }
                _logger.info(vals)
                self.env['pos.decentralize'].create(vals)
            except Exception as e:
                _logger.error(e)
                

    def generate_decentralize(self, branch, date_start=False, date_end=False):
        _logger.info('generate_decentralize_by_branch')
        if not date_start or not date_end:
            domain = [
                ('branch_id','=',branch)
            ]
        else:
            domain = [
                ('branch_id','=',branch),
                ('write_date','>=', date_start),
                ('write_date','<=', date_end)
            ]
        _logger.info(domain)
        product_product_barcode_ids = self.env['product.product.barcode'].search(domain)
        row_count = len(product_product_barcode_ids)
        
        row_num = 0
        row_process = 0
        for row in product_product_barcode_ids:
            #Product Barcode Format
            # Digit 1    (1)    : C (Add), W (Update), U (Delete)
            # Digit 2-5  (4)    : Store Code
            # Digit 6-15 (10)   : Server ID
            # Digit 16-24 (9)   : SKU
            # Digit 25-42 (18)  : Barcode
            
            # branch= '7001'
            branch_id = self.env['res.branch'].browse(branch)
            server_id = str(row.id).rjust(10,'0')        
            sku = row.product_id.default_code
            barcode = row.barcode.ljust(18,'0')
            if row.create_date == row.write_date:
                type = 'C'
            else:
                type = 'U'
            try:
                data = type + branch_id.code + server_id + sku + barcode
                vals = {
                    'branch_id': branch_id.id, 
                    'data_type': 'barcode',
                    'res_id': row.id,
                    'reference': '',
                    'data':data,
                }
                _logger.info(vals)
                self.env['pos.decentralize'].create(vals)
                if row_num == 200:
                    row_num = 0
                    self.env.cr.commit()
                    _logger.info("Commit")
                else:
                    row_num += 1
                    row_process += 1
                    if row_process == row_count:
                        self.env.cr.commit()
                        _logger.info("Last Commit")
            except Exception as e:
                _logger.error(e)
                            
            _logger.info('Row Num : ' + str(row_num) + ';Row Process : ' + str(row_process))
                
    def _process_generate_decentralize(self, branch, date_start=False, date_end=False):
        _logger.info("_process_generate_decentralize")
        active_id = self.id
        with api.Environment.manage(), self.pool.cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            self.env['product.product.barcode'].generate_decentralize(branch, date_start, date_end)
            
    def background_process_process(self, branch, date_start=False, date_end=False):
        threaded_process = threading.Thread(target=self._process_generate_decentralize, args=(branch, date_start, date_end))
        threaded_process.start()
                        
    @api.model            
    def sync_product(self):  
        super(ProductProductBarcode,self).sync_product()
        # self.generate_decentralize_by_branch(self.branch_id.code, type='C')

    def remove_product_barcode(self):
        super(ProductProductBarcode,self).remove_product_barcode()
        # self.generate_decentralize_by_branch(self.branch_id.code, 'U')
