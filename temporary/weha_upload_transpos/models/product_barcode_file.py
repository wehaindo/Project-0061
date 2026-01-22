import logging
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _
from datetime import datetime
import threading

import base64

_logger = logging.getLogger(__name__)


class product_barcode_file(models.Model):
    _name= "product.barcode.file"
    _rec_name="filename"

    def _rows(self, line):
        data = {
            'rec_id' : line[0:1].strip(),
            'sku_number' : line[1:14].strip(),
            'barcode_no' : line[14:32].strip()
        }
        return data

    def check_barcode(self, sku):
        domain = [
            ('default_code','=', sku)
        ]
        res = self.env['product.tamplate'].search(domain, limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res
        
    def _process_download(self):
        _logger.info("run_process_download")
        # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
        active_id = self.id
        _logger.info('active_id')
        _logger.info(active_id)
        with api.Environment.manage(), self.pool.cursor() as new_cr:
            # new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            # active_id = self.env.context.get('active_id')
            self.state = 'in_progress'
            self.env.cr.commit()
            self.env['product.barcode.file'].generate_file(active_id)
            # new_cr.commit()
    
    # def create_barcode(self, rows):
    #     vals = {
    #         # 'default_code': rows['sku_number'],
    #         'barcode': rows['barcode_no'].replace(" ", ""),
    #     }
    #     _logger.info("CREATE BARCODE")
    #     _logger.info(vals)
    #     res = self.env['product.template'].create(vals)

    # def update_barcode(self, rows, product_template):
    #     res = self.env['product.template'].search([('id','=', barcode_id)])
    #     if res:
    #         vals = {
    #             # 'default_code': rows['sku_number'],
    #             'barcode': rows['barcode_no'].replace(" ", ""),
    #         }
    #         _logger.info("UPDATE BARCODE")
    #         _logger.info(vals)
    #         res.write(vals)

    def generate_file(self, id):
        # Example : B5C31990.001
        try:
            product_barcode_file_id = self.env['product.barcode.file'].browse(id)
            filename = product_barcode_file_id.filename
            filename = filename.replace(".","")
            store_code = filename[7:11]
            _logger.info(store_code)

            file_content = base64.b64decode(product_barcode_file_id.file)
            file_content = file_content.decode("utf-8")
            # file_lines = file_content.split("\r\n")
            file_lines = file_content.split("\n")

            branch_id = self.env['res.branch'].search([('code','=', store_code)], limit=1)
            if branch_id:
                _logger.info(file_lines)
                for line in file_lines:
                    _logger.info(str(len(line)))
                    rows = self._rows(line)
                    _logger.info(rows)
                    
                    if rows['rec_id'] == "A":
                        sku = rows['sku_number']
                        barcode = rows['barcode_no']
                        domain = [
                            ('default_code', '=', sku)
                        ]
                        product_template_id = self.env['product.template'].search(domain, limit=1)
                        _logger.info('product_template_id')
                        _logger.info(product_template_id)
                        if product_template_id:
                            domain = [
                                ('product_id','=', product_template_id.id),
                                ('barcode','=', barcode),
                                ('branch_id','=', branch_id.id)
                            ]
                            _logger.info("domain")
                            _logger.info(domain)
                            product_barcode_id = self.env['product.product.barcode'].search(domain, limit=1)
                            _logger.info('product_barcode_id')
                            _logger.info(product_barcode_id)
                            if product_barcode_id:
                                _logger.info('found product_barcode_id')
                            else:
                                _logger.info('create product_barcode_id')
                                vals = {
                                    "product_id": product_template_id.id,
                                    "barcode": barcode,
                                    "branch_id": branch_id.id
                                }
                                try:
                                    res = self.env['product.product.barcode'].create(vals)       
                                    _logger.info(res)
                                    self.env.cr.commit()                     
                                except Exception as e:
                                    _logger.error(e)                                

                    if rows['rec_id'] == "D":
                        pass

                self.state = 'done'              
                self.env.cr.commit()
            else:
                self.state = 'cancel'              
                self.env.cr.commit()
                _logger.error('Branch not Found')
        except Exception as e:
            self.state = 'cancel'              
            self.env.cr.commit()
            _logger.error('Branch not Found')
            _logger.error(e)
            
    def cron_process_download(self):     
        #Running Thread
        if self.is_use_thread:
            _logger.info("running thread")
            threaded_download = threading.Thread(target=self._process_download, args=())
            threaded_download.start()   
            # threaded_download.join()        
        else:
            self._process_download()            

    def process_download(self):     
        #Running Thread
        if self.is_use_thread:
            _logger.info("running thread")
            threaded_download = threading.Thread(target=self._process_download, args=())
            threaded_download.start()           
            # threaded_download.join()           
            return {'type': 'ir.actions.client', 'tag': 'reload'}                     
        else:
            self._process_download()

    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)    
    is_use_thread = fields.Boolean('Use Threading', default=True)
    download_id = fields.Many2one('pos.interface.download','Download #', ondelete='set null')
    state = fields.Selection([('draft','New'),('in_progress','In Progress'),('done','Finished'),('cancel','Cancel')], 'Status', default='draft')