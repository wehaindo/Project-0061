from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError
import threading
import time

import logging
_logger = logging.getLogger(__name__)


class PosPromotion(models.Model):
    _inherit='pos.promotion'
        
    def generate_decentralize_by_branch_for_combination(self, type, products):        
        #Product Barcode Format
        # Digit 1    (1)    : C (Add), W (Update), U (Delete)
        # Digit 2-5  (4)    : Store Code
        # Digit 6-15 (10)   : Server ID     
        # Digit 16-25 (10)  : Promotion Code
        # Digit 26-32 (7)  : Promotion Description
        # Digit 33-40 (8)  : From Date
        # Digit 41-48 (8)  : To Date                 
        # Digit 49-56 (8)  : PLU Count / SKU Count
        # Digit 57-66 (10)  : Promo Qty / Total Qty 7.2
        # Digit 67-72 (6)  : Promo Qty1           
        # Digit 73-78 (6)  : Promo Qty2          
        # Digit 79-84 (6)  : Promo Qty3           
        # Digit 85-90 (6)  : Promo Qty4           
        # Digit 91-96 (6)  : Promo Qty5           
        # Digit 97-102 (6)  : Promo Qty6 
        # Digit 103-111 (9)  : Sku 1
        # Digit 112-120 (9)  : Sku 2
        # Digit 121-129 (9)  : Sku 3
        # Digit 130-138 (9)  : Sku 4
        # Digit 139-147 (9)  : Sku 5
        # Digit 148-156 (9)  : Sku 6
        # Digit 157-173 (17)  : Promo Price 1
        # Digit 174-190 (17)  : Promo Price 2
        # Digit 191-207 (17)  : Promo Price 3
        # Digit 208-224 (17)  : Promo Price 4
        # Digit 225-241 (17)  : Promo Price 5
        # Digit 242-258 (17)  : Promo Price 1
        # Digit 259-275 (17)  : Total Promo Price                                                                   
        # branch= '7001'            
        try:
            # product_id = row.product_id                
            # promotion_id = row.id
            # _logger.info(promotion_id)
            _logger.info('generate_decentralize_by_branch_for_combination')
            row = self
            _logger.info(row)
            branch_id = row.branch_ids[0]
            _logger.info(branch_id)
            # branch_id = self.env['res.branch'].search([('code','=',branch)], limit=1)            
            server_id = str(row.id).rjust(10,'0')        
            _logger.info(server_id)                        
            promotion_code = row.promotion_code
            _logger.info(promotion_code)
            promotion_description =  row.promotion_description.ljust(7,' ')[0:7]
            _logger.info(promotion_description)
            from_date = row.from_date.strftime('%Y%m%d')
            _logger.info(from_date)
            to_date = row.to_date.strftime('%Y%m%d')
            _logger.info(to_date)
            promo_qty1 = "000000"
            promo_qty2 = "000000"
            promo_qty3 = "000000"
            promo_qty4 = "000000"
            promo_qty5 = "000000"
            promo_qty6 = "000000"
            sku1 = "         "
            sku2 = "         "
            sku3 = "         "
            sku4 = "         "
            sku5 = "         " 
            sku6 = "         "
            promo_price1 = "00000000000000.00"
            promo_price2 = "00000000000000.00"
            promo_price3 = "00000000000000.00"
            promo_price4 = "00000000000000.00"
            promo_price5 = "00000000000000.00"
            promo_price6 = "00000000000000.00"       
            promo_total_price = "00000000000000.00"                             
            product_count = 1
            for product in products:
            # for combination_product_fixed_price_id in row.combination_product_fixed_price_ids:                                                 
                if product_count == 1:
                    promo_qty1 = str(product['quantity_amt']).rjust(6,'0')
                    _logger.info(promo_qty1)
                    sku1 = product['product_id'].default_code
                    _logger.info(sku1)
                    promo_price1 = product['fixed_price']
                    _logger.info(promo_price1)
                if product_count == 2:
                    promo_qty2 = str(product['quantity_amt']).rjust(6,'0')
                    _logger.info(promo_qty2)
                    sku2 = product['product_id'].default_code
                    _logger.info(sku2)
                    promo_price2 = product['fixed_price']
                    _logger.info(promo_price2)
                if product_count == 3:
                    promo_qty3 = str(product['quantity_amt']).rjust(6,'0')
                    _logger.info(promo_qty3)
                    sku3 = product['product_id'].default_code
                    _logger.info(sku3)
                    promo_price3 = product['fixed_price']
                    _logger.info(promo_price3)
                if product_count == 4:
                    promo_qty4 = str(product['quantity_amt']).rjust(6,'0')
                    _logger.info(promo_qty4)
                    sku4 = product['product_id'].default_code
                    _logger.info(sku4)
                    promo_price4 = product['fixed_price']
                    _logger.info(promo_price4)
                if product_count == 5:
                    promo_qty5 = str(product['quantity_amt']).rjust(6,'0')
                    _logger.info(promo_qty5)
                    sku5 = product['product_id'].default_code
                    _logger.info(sku5)
                    promo_price5 = product['fixed_price']
                    _logger.info(promo_price5)
                if product_count == 6:
                    promo_qty6 = str(product['quantity_amt']).rjust(6,'0')
                    _logger.info(promo_qty6)
                    sku6 = product['product_id'].default_code
                    _logger.info(sku6)
                    promo_price6 = product['fixed_price']
                    _logger.info(promo_price6)
                product_count += 1                
            data = type + branch_id.code + server_id  + promotion_code + promotion_description + from_date + to_date + promo_qty1 + promo_qty2 + promo_qty3 + promo_qty4 + promo_qty5 + promo_qty6 + sku1 + sku2 + sku3 + sku4 + sku5 + sku6 + promo_price1 + promo_price2 + promo_price3 + promo_price4 + promo_price5 + promo_price6  +  promo_total_price               
            vals = {
                'branch_id': branch_id.id, 
                'data_type': 'combination',
                'reference': '',
                'data':data,                
            }
            _logger.info(vals)
            self.env['pos.decentralize'].create(vals)
        except Exception as e:
            _logger.error(e)
            
    def generate_decentralize_combination(self, branch, date_start=False, date_end=False):        
        #Product Barcode Format
        # Digit 1    (1)    : C (Add), W (Update), U (Delete)
        # Digit 2-5  (4)    : Store Code
        # Digit 6-15 (10)   : Server ID     
        # Digit 16-25 (10)  : Promotion Code
        # Digit 26-32 (7)  : Promotion Description
        # Digit 33-40 (8)  : From Date
        # Digit 41-48 (8)  : To Date                 
        # Digit 49-56 (8)  : PLU Count / SKU Count
        # Digit 57-66 (10)  : Promo Qty / Total Qty 7.2
        # Digit 67-72 (6)  : Promo Qty1           
        # Digit 73-78 (6)  : Promo Qty2          
        # Digit 79-84 (6)  : Promo Qty3           
        # Digit 85-90 (6)  : Promo Qty4           
        # Digit 91-96 (6)  : Promo Qty5           
        # Digit 97-102 (6)  : Promo Qty6 
        # Digit 103-111 (9)  : Sku 1
        # Digit 112-120 (9)  : Sku 2
        # Digit 121-129 (9)  : Sku 3
        # Digit 130-138 (9)  : Sku 4
        # Digit 139-147 (9)  : Sku 5
        # Digit 148-156 (9)  : Sku 6
        # Digit 157-173 (17)  : Promo Price 1
        # Digit 174-190 (17)  : Promo Price 2
        # Digit 191-207 (17)  : Promo Price 3
        # Digit 208-224 (17)  : Promo Price 4
        # Digit 225-241 (17)  : Promo Price 5
        # Digit 242-258 (17)  : Promo Price 1
        # Digit 259-275 (17)  : Total Promo Price                                                                   
        # branch= '7001'            
        try:
            # product_id = row.product_id                
            # promotion_id = row.id
            # _logger.info(promotion_id)
            _logger.info('generate_decentralize_by_branch')
            res_branch_id = self.env['res.branch'].browse(branch)                                    

            domain = [
                ('branch_ids','in',[branch]),
                ('active','=', True),
                ('promotion_type','=','combination_product_fixed_price')
            ]
            _logger.info(domain)    
            pos_promotion_ids = self.env['pos.promotion'].search(domain).ids
            
            if not date_start or not date_end:
                domain = [
                    ('promotion_id','in',pos_promotion_ids)
                ]
            else:
                domain = [
                    ('promotion_id','in',pos_promotion_ids),
                    ('write_date','>=', date_start),
                    ('write_date','<=', date_end)
            ]
            _logger.info(domain)                
            price_combination_products_ids = self.env['price.combination.products'].search(domain).ids            
            if len(price_combination_products_ids) == 1:
                strSQL = "SELECT distinct(promotion_id) FROM price_combination_products WHERE id = " + str(price_combination_products_ids[0])
            else:
                strSQL = "SELECT distinct(promotion_id) FROM price_combination_products WHERE id in " + str(tuple(price_combination_products_ids))
            self.env.cr.execute(strSQL)
            promotion_ids = self.env.cr.fetchall()
            _logger.info(promotion_ids)
            for promotion_id in promotion_ids:
                promotion = self.env['pos.promotion'].browse(promotion_id)  
                branch_id = res_branch_id.id
                _logger.info(branch_id)                  
                server_id = str(promotion.id).rjust(10,'0')        
                _logger.info(server_id)                        
                promotion_code = promotion.promotion_code
                _logger.info(promotion_code)
                promotion_description = "".ljust(7," ")[0:7] if not promotion.promotion_description else promotion.promotion_description.ljust(7," ")[0:7]
                _logger.info(promotion_description)
                from_date = promotion.from_date.strftime('%Y%m%d')
                _logger.info(from_date)
                to_date = promotion.to_date.strftime('%Y%m%d')
                _logger.info(to_date)
                promo_qty1 = "000000"
                promo_qty2 = "000000"
                promo_qty3 = "000000"
                promo_qty4 = "000000"
                promo_qty5 = "000000"
                promo_qty6 = "000000"
                sku1 = "         "
                sku2 = "         "
                sku3 = "         "
                sku4 = "         "
                sku5 = "         " 
                sku6 = "         "
                promo_price1 = "00000000000000.00"
                promo_price2 = "00000000000000.00"
                promo_price3 = "00000000000000.00"
                promo_price4 = "00000000000000.00"
                promo_price5 = "00000000000000.00"
                promo_price6 = "00000000000000.00" 
                promo_total_price = "00000000000000.00"     
                total_price = 0                
                product_count = 1
                for product in promotion.combination_product_fixed_price_ids:                                                                     
                    if product_count == 1:
                        promo_qty1 = str(product.quantity_amt).rjust(6,'0')
                        _logger.info(promo_qty1)
                        sku1 = product.product_id.default_code
                        _logger.info(sku1)
                        arr_fixed_price =  str(product.fixed_price).split('.')
                        promo_price1 = arr_fixed_price[0].rjust(14,'0') + '.' + arr_fixed_price[1].ljust(2,'0')
                        total_price = total_price + product.fixed_price
                        _logger.info(promo_price1)
                    if product_count == 2:                        
                        promo_qty2 = str(product.quantity_amt).rjust(6,'0')
                        _logger.info(promo_qty2)
                        sku2 = product.product_id.default_code
                        _logger.info(sku2)
                        arr_fixed_price =  str(product.fixed_price).split('.')
                        promo_price2 = arr_fixed_price[0].rjust(14,'0') + '.' + arr_fixed_price[1].ljust(2,'0')
                        total_price = total_price + product.fixed_price
                        _logger.info(promo_price2)
                    if product_count == 3:
                        promo_qty3 = str(product.quantity_amt).rjust(6,'0')
                        _logger.info(promo_qty3)
                        sku3 = product.product_id.default_code
                        _logger.info(sku3)
                        arr_fixed_price =  str(product.fixed_price).split('.')
                        promo_price3 = arr_fixed_price[0].rjust(14,'0') + '.' + arr_fixed_price[1].ljust(2,'0')
                        total_price = total_price + product.fixed_price
                        _logger.info(promo_price3)
                    if product_count == 4:
                        promo_qty4 = str(product.quantity_amt).rjust(6,'0')
                        _logger.info(promo_qty4)
                        sku4 = product.product_id.default_code
                        _logger.info(sku4)
                        arr_fixed_price =  str(product.fixed_price).split('.')
                        promo_price4 = arr_fixed_price[0].rjust(14,'0') + '.' + arr_fixed_price[1].ljust(2,'0')
                        total_price = total_price + product.fixed_price
                        _logger.info(promo_price4)
                    if product_count == 5:
                        promo_qty5 = str(product.quantity_amt).rjust(6,'0')
                        _logger.info(promo_qty5)
                        sku5 = product.product_id.default_code
                        _logger.info(sku5)
                        arr_fixed_price =  str(product.fixed_price).split('.')
                        promo_price5 = arr_fixed_price[0].rjust(14,'0') + '.' + arr_fixed_price[1].ljust(2,'0')
                        total_price = total_price + product.fixed_price
                        _logger.info(promo_price5)
                    if product_count == 6:
                        promo_qty6 = str(product.quantity_amt).rjust(6,'0')
                        _logger.info(promo_qty6)
                        sku6 = product.product_id.default_code
                        _logger.info(sku6)
                        arr_fixed_price =  str(product.fixed_price).split('.')
                        promo_price6 = arr_fixed_price[0].rjust(14,'0') + '.' + arr_fixed_price[1].ljust(2,'0')
                        total_price = total_price + product.fixed_price
                        _logger.info(promo_price6)
                    product_count += 1    
                    
                arr_total_price =  str(total_price).split('.')
                promo_total_price = arr_total_price[0].rjust(14,'0') + '.' + arr_total_price[1].ljust(2,'0')
                if product.create_date == product.write_date:
                    type = 'C'
                else:
                    type = 'U'         
                                    
                data = type + res_branch_id.code + server_id  + promotion_code + promotion_description + from_date + to_date + promo_qty1 + promo_qty2 + promo_qty3 + promo_qty4 + promo_qty5 + promo_qty6 + sku1 + sku2 + sku3 + sku4 + sku5 + sku6 + promo_price1 + promo_price2 + promo_price3 + promo_price4 + promo_price5 + promo_price6  + promo_total_price                      
                vals = {
                    'branch_id': res_branch_id.id, 
                    'data_type': 'combination',
                    'res_id': promotion.id,
                    'reference': '',
                    'data':data,                
                }
                _logger.info(vals)
                self.env['pos.decentralize'].create(vals)
        except Exception as e:
            _logger.error(e)
    
    def generate_decentralize_by_branch_for_partial(self, type, promotion_line):
        _logger.info('generate_decentralize_by_branch')
        for row in self:
            _logger.info(row)
            #Product Barcode Format
            # Digit 1    (1)    : C (Add), W (Update), U (Delete)
            # Digit 2-5  (4)    : Store Code
            # Digit 6-15 (10)   : Server ID
            # Digit 16-24 (9)   : SKU
            # Digit 25-34 (10)  : Promotion Code
            # Digit 35-47 (12)  : Promotion Description
            # Digit 48-55 (8)  : From Date
            # Digit 56-63 (8)  : To Date
            # Digit 64-71 (8)  : Quantity
            # Digit 72-73 (2)  : Quantity Amt
            # Digit 74-88 (15)  : Fixed Price                                    
            try:                
                branch_id = row.branch_ids[0]
                _logger.info(branch_id)
                server_id = str(row.id).rjust(10,'0')        
                _logger.info(server_id)
                promotion_code = row.promotion_code.ljust(10,' ') # 10 Digit
                _logger.info(promotion_code)
                promotion_description =  row.promotion_description.ljust(7,' ')[0:7] # 7 Digit
                _logger.info(promotion_description)
                from_date = row.from_date.strftime('%Y%m%d')
                _logger.info(from_date)
                to_date = row.to_date.strftime('%Y%m%d')
                _logger.info(to_date) 
                product_id = promotion_line['product_id']                                    
                sku = product_id.default_code
                _logger.info(sku)
                quantity = str(promotion_line['quantity'] or 0).rjust(8,'0')
                _logger.info(quantity)
                quantity_amt = str(promotion_line['quantity_amt'] or 0).rjust(8,'0')
                _logger.info(quantity_amt)
                fixed_price = ('%.2f' %  promotion_line['fixed_price']).rjust(15,'0')
                _logger.info(fixed_price)
                data = type + branch_id.code + server_id + sku + promotion_code + promotion_description + from_date + to_date + quantity + quantity_amt + fixed_price
                vals = {
                    'branch_id': branch_id.id, 
                    'data_type': 'partial',
                    'reference': '',
                    'data':data,                
                }
                _logger.info(vals)
                self.env['pos.decentralize'].create(vals)
            except Exception as e:
                _logger.error(e)
                
    def generate_decentralize_partial(self, branch, date_start=False, date_end=False):
        _logger.info('generate_decentralize_by_branch')
        domain = [
            ('branch_ids','in',[branch]),
            ('active','=', True),
            ('promotion_type','=','buy_x_partial_quantity_get_special_price')
        ]
        _logger.info(domain)    
        pos_promotion_ids = self.env['pos.promotion'].search(domain).ids
        if not date_start or not date_end:
            domain = [
                ('pos_promotion_id','in',pos_promotion_ids)
            ]
        else:
            domain = [
                ('pos_promotion_id','in',pos_promotion_ids),
                ('write_date','>=', date_start),
                ('write_date','<=', date_end)
            ]
        _logger.info(domain)       
        partial_quantity_fixed_price_ids = self.env['partial.quantity.fixed.price'].search(domain)
        for row in partial_quantity_fixed_price_ids:
            _logger.info(row)
            #Product Barcode Format
            # Digit 1    (1)    : C (Add), W (Update), U (Delete)
            # Digit 2-5  (4)    : Store Code
            # Digit 6-15 (10)   : Server ID
            # Digit 16-24 (9)   : SKU
            # Digit 25-34 (10)  : Promotion Code
            # Digit 35-47 (12)  : Promotion Description
            # Digit 48-55 (8)  : From Date
            # Digit 56-63 (8)  : To Date
            # Digit 64-71 (8)  : Quantity
            # Digit 72-73 (2)  : Quantity Amt
            # Digit 74-88 (15)  : Fixed Price                                    
            try:            
                res_branch_id = self.env['res.branch'].browse(branch)                                    
                branch_id = res_branch_id.id
                _logger.info(branch_id)
                server_id = str(row.id).rjust(10,'0')        
                _logger.info(server_id)
                promotion_code = row.pos_promotion_id.promotion_code.ljust(10,' ') # 10 Digit
                _logger.info(promotion_code)
                promotion_description =  row.pos_promotion_id.promotion_description.ljust(7,' ')[0:7] # 7 Digit
                _logger.info(promotion_description)
                from_date = row.pos_promotion_id.from_date.strftime('%Y%m%d')
                _logger.info(from_date)
                to_date = row.pos_promotion_id.to_date.strftime('%Y%m%d')
                _logger.info(to_date)   
                for product_id in row.product_ids:              
                    sku = product_id.default_code
                    _logger.info(sku)
                    quantity = str(row.quantity or 0).rjust(8,'0')
                    _logger.info(quantity)
                    quantity_amt = str(row.quantity_amt or 0).rjust(8,'0')
                    _logger.info(quantity_amt)
                    arr_fixed_price =  str(row.fixed_price).split('.')
                    fixed_price = arr_fixed_price[0].rjust(12,'0') + '.' + arr_fixed_price[1].ljust(2,'0')
                    #fixed_price = ('%.2f' %  row.fixed_price).rjust(15,'0')
                    _logger.info(fixed_price)
                    if row.create_date == row.write_date:
                        type = 'C'
                    else:
                        type = 'U'
                        
                    data = type + res_branch_id.code + server_id + sku + promotion_code + promotion_description + from_date + to_date + quantity + quantity_amt + fixed_price
                    vals = {
                        'branch_id': branch_id, 
                        'data_type': 'partial',
                        'reference': '',
                        'data':data,                
                    }
                    _logger.info(vals)
                    self.env['pos.decentralize'].create(vals)
            except Exception as e:
                _logger.error(e)

    def _process_generate_decentralize_combination(self, branch, date_start=False, date_end=False):
        _logger.info("_process_generate_decentralize_combination")
        active_id = self.id
        with api.Environment.manage(), self.pool.cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            self.env['pos.promotion'].generate_decentralize_combination(branch, date_start, date_end)
            
    def background_process_process_combination(self, branch, date_start=False, date_end=False):
        threaded_process = threading.Thread(target=self._process_generate_decentralize_combination, args=(branch, date_start, date_end))
        threaded_process.start()
        
    def _process_generate_decentralize_partial(self, branch, date_start=False, date_end=False):
        _logger.info("_process_generate_decentralize_partial")
        active_id = self.id
        with api.Environment.manage(), self.pool.cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            self.env['pos.promotion'].generate_decentralize_partial(branch, date_start, date_end)
            
    def background_process_process_partial(self, branch, date_start=False, date_end=False):
        threaded_process = threading.Thread(target=self._process_generate_decentralize_partial, args=(branch, date_start, date_end))
        threaded_process.start()        