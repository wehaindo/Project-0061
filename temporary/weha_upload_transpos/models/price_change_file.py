import logging
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _, registry
from datetime import datetime
import threading

import base64

_logger = logging.getLogger(__name__)


class price_change_file(models.Model):
    _name= "price.change.file"
    _rec_name="filename"

    def _rows(self, line):
        data = {
            'rec_id' : line[0:1].strip(),
            'item_no' : line[1:14].strip(),
            'prc_no' : line[14:24].strip(),
            'prc_type' : line[24:30].strip(),
            'prc_start_date' : line[30:38].strip(),
            'prc_end_date' : line[38:46].strip(),
            'prc_start_time' : line[46:50].strip(),
            'prc_end_time' : line[50:54].strip(),
            'prc_disc_rate' : line[54:60].strip(),
            'prc_disc_amt' : line[60:72].strip(),
            'prc_sell' : line[72:89].strip()
        }
        return data

    def check_product(self, sku):
        res = self.env['product.product'].search([('default_code','=', sku)], limit=1)
        if res:
            _logger.info("Product Found")
            mes = True
            return mes, res
        else:
            _logger.info("Product not Found")
            mes = False
            return mes, res

    def check_store_pricelist(self, store_id, price_type):
        _logger.info("check_store_pricelist")
        domain = [
            ('branch_id','=', store_id.id), 
            ('price_type','=', price_type)
        ]
        try:
            res = self.env['product.pricelist'].search(domain, limit=1)
            if res:        
                _logger.info("Pricelist and Price Type Found")
                mes = True
                return mes, res
            else:
                _logger.info("Pricelist and Price Type not Found")
                mes = False
                return mes, res
        except Exception as e:
            _logger.info(e)
            return False, e

    def check_product_pricelist_item(self, pricelist_id, product_id, price_change_code=False):
        
        if not price_change_code:
            res = self.env['product.pricelist.item'].search([('pricelist_id','=', pricelist_id.id),('product_tmpl_id','=',product_id.product_tmpl_id.id),('product_id','=',product_id.id)], limit=1)
        else:
            res = self.env['product.pricelist.item'].search([('pricelist_id','=', pricelist_id.id),('product_tmpl_id','=',product_id.product_tmpl_id.id),('product_id','=',product_id.id), ('prc_no','=', price_change_code)], limit=1)
        
        if res:
            _logger.info("Pricelist and Product Change Found")
            mes = True
            return mes, res
        else:
            _logger.info("Pricelist and Product Change not Found")
            mes = False
            return mes, res
        
    def create_product_pricelist_item(self, pricelist_id, product_id, rows):
        _logger.info("create_product_pricelist_item")
        # Start Date Time
        start_date = rows['prc_start_date']
        start_time = rows['prc_start_time']
        start_time = f"{start_time[:2]}:{start_time[2:]}:00"
        str_start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2) + " " + start_time
        # End Date Time
        end_date = rows['prc_end_date']
        end_time = rows['prc_end_time']
        end_time = f"{end_time[:2]}:{end_time[2:]}:00"
        str_end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2) + " " + end_time
        vals = {
            'prc_no': rows['prc_no'],
            'fixed_price': rows['prc_sell'],
            'date_start': str_start_date,
            'date_end': str_end_date,
            'pricelist_id': pricelist_id.id,
            'product_tmpl_id':  product_id.product_tmpl_id.id, #Product Template
            'product_id':  product_id.id #Product ID
        }

        _logger.info("CREATE PRICELIST ITEMS")
        _logger.info(vals)
        try:
            res = self.env['product.pricelist.item'].create(vals)
            self.env.cr.commit()
            _logger.info("Create Pricelist Item Successfully")
        except Exception as e:
            _logger.error("Error Create Pricelist Item")
            _logger.error(e)

    def update_product_pricelist_item(self, pricelist_item_id, rows):
        _logger.info("update_product_pricelist_item")
        # Start Date Time
        start_date = rows['prc_start_date']
        start_time = rows['prc_start_time']
        start_time = f"{start_time[:2]}:{start_time[2:]}:00"
        str_start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2) + " " + start_time
        # End Date Time
        end_date = rows['prc_end_date']
        end_time = rows['prc_end_time']
        end_time = f"{end_time[:2]}:{end_time[2:]}:00"
        str_end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2) + " " + end_time
        
        res = self.env['product.pricelist.item'].search([('id','=', pricelist_item_id.id)])
        vals = {
            # 'prc_no': rows['prc_no'],
            'fixed_price': rows['prc_sell'],
            'date_start': str_start_date,
            'date_end': str_end_date,
        }

        _logger.info("UPDATE PRICELIST ITEMS")
        _logger.info(vals)
        res.write(vals)
        self.env.cr.commit()
    
    def _process_download(self):
        _logger.info("run _process_download")
        active_id = self.id
        # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
        with api.Environment.manage(), self.pool.cursor() as new_cr:            
            self = self.with_env(self.env(cr=new_cr))            
            self.state = 'in_progress'
            self.env.cr.commit()
            self.env['price.change.file'].generate_file(active_id)
            
    def generate_file(self, id):
        # Example : P5C31990.001
        _logger.info("start generate file")
        price_change_file_id = self.env['price.change.file'].browse(id)            
        filename = price_change_file_id.filename
        filename = filename.replace(".","")
        store_code = filename[7:11]
        _logger.info(store_code)

        try:
            res_branch_id = self.env['res.branch'].search([("code","=", store_code)], limit=1)        
            _logger.info(res_branch_id)

            file_content = base64.b64decode(price_change_file_id.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")


            for line in file_lines:
                _logger.info(str(len(line)))
                rows = self._rows(line)
                _logger.info(rows)

                if rows['rec_id'] == "A":
                    _logger.info("A")
                    # Check Product Item No for get branch_id
                    product_mes, product = self.check_product(rows['item_no'])
                    if product_mes:
                        _logger.info("product_found")
                        # Check Product Pricelist by branch_id & prc_type
                        pricelist_mes, pricelist = self.check_store_pricelist(res_branch_id, rows['prc_type'])
                        if pricelist_mes:
                            # Check Product Pricelist Items by pricelist_id & prc_no
                            check, pricelist_item = self.check_product_pricelist_item(pricelist, product, rows['prc_no'])
                            if check:
                                # UPDATE
                                self.update_product_pricelist_item(pricelist_item, rows)
                            else:
                                # CREATE                            
                                self.create_product_pricelist_item(pricelist, product, rows)

                if rows['rec_id'] == "D":
                    _logger.info("A")
                    product_pricelist_item = self.env['product.pricelist.item'].search([('base_pricelist_id','=', pricelist.id), ('prc_no','=', rows['prc_no'])])
                    product_pricelist_item.write({'active': False})
                    self.env.cr.commit()

            price_change_file_id.state = 'done'
            # price_change_file_id.date_end = datetime.now()                                
            self.env.cr.commit()
            _logger.info("stop generate file")

        except Exception as e:
            _logger.error(e)

    def cron_process_download(self):     
        #Running Thread
        if self.is_use_thread:
            _logger.info("running thread")
            threaded_download = threading.Thread(target=self._process_download, args=())
            threaded_download.start()   
            #threaded_download.join()        
        else:
            self._process_download()            

    def process_download(self):     
        #Running Thread
        if self.is_use_thread:
            _logger.info("running thread")
            threaded_download = threading.Thread(target=self._process_download, args=())
            threaded_download.start()           
            #threaded_download.join()
            return {'type': 'ir.actions.client', 'tag': 'reload'}                     
        else:
            self._process_download()

    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)
    is_use_thread = fields.Boolean('Use Threading', default=True)
    download_id = fields.Many2one('pos.interface.download','Download #', ondelete='set null')
    state = fields.Selection([('draft','New'),('in_progress','In Progress'),('done','Finished'),('cancel','Cancel')], 'Status', default='draft')