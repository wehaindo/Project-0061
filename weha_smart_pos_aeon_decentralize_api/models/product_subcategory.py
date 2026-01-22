from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError
import threading
import time

import logging
_logger = logging.getLogger(__name__)


class ProductSubCategory(models.Model):
    _inherit = 'product.sub.category'

    def generate_decentralize_by_branch(self, branch=False, type=False):
        _logger.info('generate_decentralize_by_branch')
        for row in self:
            #Product Subcategory Format
            # 1. Digit 1    (1)    : C (Add), W (Update), U (Delete)
            # 2. Digit 2-5  (4)    : Store Code
            # 3. Digit 6-15 (10)   : Server ID
            # 4. Digit 16-21 (6)   : Code
            # 5. Digit 22 (1)      : Member Day Discount
            # 6. Digit 23-37 (5)   : Member Day Discount Percentage
            # 7. Digit 38-67 (30)  : Name
                    
            # branch= '7001'
            branch_id = self.env['res.branch'].search([('code','=',branch)], limit=1)            
            server_id = str(row.id).rjust(10,'0')        
            code = row.code           
            member_day_discount =  '1' if row.is_member_day_discount == True else '0'            
            member_day_discount_percentage  = ('%.2f' %  row.member_day_discount_percentage).rjust(5,'0')            
            name = row.name[0:30].ljust(30,' ')
            
            data = type + branch + server_id + code + member_day_discount + member_day_discount_percentage + name
            vals = {
                'branch_id': branch_id.id, 
                'data_type': 'subcategory',
                'reference': '',
                'data':data,
            }
            _logger.info(vals)
            self.env['pos.decentralize'].create(vals)
                        
    def generate_decentralize(self, branch, date_start=False, date_end=False):
        _logger.info('generate_decentralize')  
        
        if not date_start or not date_end:
            domain = []
        else:
            domain = [
                ('write_date','>=', date_start),
                ('write_date','<=', date_end)
            ]
        _logger.info(domain)
        product_ids = self.env['product.sub.category'].search(domain)
        row_count = len(product_ids)
        
        _logger.info(product_ids)
        _logger.info('generate_decentralize')
        row_num = 0
        row_process = 0
        for row in product_ids:            
            #Product Subcategory Format
            # 1. Digit 1    (1)    : C (Add), W (Update), U (Delete)
            # 2. Digit 2-5  (4)    : Store Code
            # 3. Digit 6-15 (10)   : Server ID
            # 4. Digit 16-21 (6)   : Code
            # 5. Digit 22-30 (9)   : Member Day Discount
            # 6. Digit 31-39 (9)   : Member Day Discount Percentage
            # 7. Digit 40-57 (18)  : Name
                    
            # branch= '7001'
            branch_id = self.env['res.branch'].browse(branch)   
            server_id = str(row.id).rjust(10,'0')
            code = row.code           
            member_day_discount =  '1' if row.is_member_day_discount == True else '0'            
            member_day_discount_percentage  = ('%.2f' %  row.member_day_discount_percentage).rjust(5,'0')            
            name = row.name[0:30].ljust(30,' ')
            if row.create_date == row.write_date:
                type = 'C'
            else:
                type = 'U'
                
            data = type + branch_id.code + server_id + code + member_day_discount + member_day_discount_percentage + name
            
            vals = {
                'branch_id': branch_id.id, 
                'data_type': 'subcategory',
                'res_id': row.id,
                'reference': '',
                'data': data,
            }
            _logger.info(vals)
            self.env['pos.decentralize'].create(vals)
            if row_num == 200:
                row_num = 0
                self.env.cr.commit()
            else:
                row_num =+ 1
                row_process =+ 1
                if row_process == row_count:
                     self.env.cr.commit()
                
    def _process_generate_decentralize(self, branch, date_start=False, date_end=False):
        _logger.info("_process_generate_decentralize")
        active_id = self.id
        with api.Environment.manage(), self.pool.cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            self.env['product.sub.category'].generate_decentralize(branch, date_start, date_end)
            
    def background_process_process(self, branch, date_start=False, date_end=False):
        threaded_process = threading.Thread(target=self._process_generate_decentralize, args=(branch, date_start, date_end))
        threaded_process.start()
    
    
    @api.model
    def create(self, vals):
        res = super(ProductSubCategory,self).create(vals)        
        # res.generate_decentralize_by_branch()

    def write(self, vals):
        super(ProductSubCategory,self).write(vals)
        # self.generate_decentralize_by_branch()