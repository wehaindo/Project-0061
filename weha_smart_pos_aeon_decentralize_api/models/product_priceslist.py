from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError
import threading
import time

import logging
_logger = logging.getLogger(__name__)


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'


    def generate_decentralize_by_branch(self, branch=False, type=False):
        _logger.info('generate_decentralize_by_branch')
        for row in self:          
            #Product Barcode Format
            # Digit 1    (1)    : C (Add), W (Update), U (Delete)
            # Digit 2-5  (4)    : Store Code
            # Digit 6-15 (10)   : Server ID
            # Digit 16-24 (9)   : SKU                          
            # Digit 25-29 (5)   : Price Type PDC or PDCM
            # Digit 24-34 (10)  : Prc No
            # Digit 35-42 (8)   : Start Date
            # Digit 43-50 (8)   : End Date
            # Digit 50-65 (15)  : Price
            
            # branch= '7001'
            try:
                # branch_id = self.env['res.branch'].search([('code','=',branch)], limit=1)            
                branch_id = row.pricelist_id.branch_id                
                _logger.info(branch_id)
                server_id = str(row.id).rjust(10,'0')        
                _logger.info(server_id)
                sku = row.product_id.default_code
                _logger.info(sku)
                price_type = row.pricelist_id.price_type.ljust(5,' ')
                _logger.info(type)
                prcno = row.prc_no.ljust(10,' ')
                _logger.info(prcno)
                date_start = row.date_start.strftime('%Y%m%d' + '000000')
                _logger.info(date_start)
                date_end  = row.date_end.strftime('%Y%m%d' + '235959') 
                _logger.info(date_end)
                fixed_price = ('%.2f' %  row.fixed_price).rjust(15,'0')
                _logger.info(fixed_price)

                data = type + branch_id.code + server_id + sku + price_type + prcno + date_start + date_end + fixed_price
                vals = {
                    'branch_id': branch_id.id, 
                    'data_type': 'pricelist',
                    'reference': '',
                    'data':data,
                }
                _logger.info(vals)
                self.env['pos.decentralize'].create(vals)
            except Exception as e:
                _logger.info(e)
                
    def generate_decentralize(self, branch, date_start=False, date_end=False):
        _logger.info('generate_decentralize_by_branch')
        domain = [
            ('branch_id','=',branch),
            ('price_type','in', ['PDC','PDCM'])
        ]
        pricelist_ids = self.env['product.pricelist'].search(domain)
        
        for pricelist_id in pricelist_ids:
            if not date_start or not date_end:
                domain = [
                    ('pricelist_id','=',pricelist_id.id),
                    
                ]
            else:
                domain = [
                    ('pricelist_id','=',pricelist_id.id),
                    ('write_date','>=', date_start),
                    ('write_date','<=', date_end)
                ]
            _logger.info(domain)
            product_pricelist_item_ids = self.env['product.pricelist.item'].search(domain)         
            _logger.info(product_pricelist_item_ids)   
            _logger.info('generate_decentralize')        
            for row in product_pricelist_item_ids:          
                #Product Barcode Format
                # Digit 1    (1)    : C (Add), W (Update), U (Delete)
                # Digit 2-5  (4)    : Store Code
                # Digit 6-15 (10)   : Server ID
                # Digit 16-24 (9)   : SKU                          
                # Digit 25-29 (5)   : Price Type PDC or PDCM
                # Digit 24-34 (10)  : Prc No
                # Digit 35-42 (8)   : Start Date
                # Digit 43-50 (8)   : End Date
                # Digit 50-65 (15)  : Price
                
                # branch= '7001'
                try:
                    type = 'C'
                    # branch_id = self.env['res.branch'].search([('code','=',branch)], limit=1)            
                    branch_id = row.pricelist_id.branch_id                
                    _logger.info(branch_id)
                    server_id = str(row.id).rjust(10,'0')        
                    _logger.info(server_id)
                    sku =  row.product_id.default_code if row.product_id else row.product_tmpl_id.default_code
                    _logger.info(sku)
                    price_type = row.pricelist_id.price_type.ljust(5,' ')[0:5]
                    _logger.info(type)
                    prcno = row.prc_no.ljust(10,' ')[0:10] if row.prc_no else ''.ljust(10,' ')[0:10]
                    _logger.info(prcno)
                    start_date = row.date_start.strftime('%Y%m%d' + '000000')
                    _logger.info(date_start)
                    end_date  = row.date_end.strftime('%Y%m%d' + '235959') 
                    _logger.info(date_end)
                    fixed_price = ('%.2f' %  row.fixed_price).rjust(15,'0')
                    _logger.info(fixed_price)
                    
                    if row.create_date == row.write_date:
                        type = 'C'
                    else:
                        type = 'U'
                                    
                    data = type + branch_id.code + server_id + sku + price_type + prcno + start_date + end_date + fixed_price
                    vals = {
                        'branch_id': branch_id.id, 
                        'data_type': 'pricelist',
                        'res_id': row.id,
                        'reference': '',
                        'data':data,
                    }
                    _logger.info(vals)
                    self.env['pos.decentralize'].create(vals)
                    self.env.cr.commit()
                except Exception as e:
                    _logger.info(e)
    
    def _process_generate_decentralize(self, branch, date_start=False, date_end=False):
        _logger.info("_process_generate_decentralize")
        active_id = self.id
        with api.Environment.manage(), self.pool.cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            self.env['product.pricelist.item'].generate_decentralize(branch, date_start, date_end)
            
    def background_process_process(self, branch, date_start=False, date_end=False):
        threaded_process = threading.Thread(target=self._process_generate_decentralize, args=(branch, date_start, date_end))
        threaded_process.start()    

    @api.model
    def create(self, vals):
        res = super(ProductPricelistItem, self).create(vals)
        # res.generate_decentralize_by_branch(type='C')
        return res
    

    def write(self, vals):
        super(ProductPricelistItem,self).write(vals)
        # self.generate_decentralize_by_branch(type='U')

    # def unlink(self, )