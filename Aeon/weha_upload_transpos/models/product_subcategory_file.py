import logging
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _
from datetime import datetime
import threading
import base64

_logger = logging.getLogger(__name__)


class product_subcategory_file(models.Model):
    _name= "product.subcategory.file"
    _rec_name="filename"
    _order = "date_start desc"

    def _rows(self, line):
        data = {
            'rec_id' : line[0:1].strip(),
            'categ' : line[1:7].strip(),
            'subcateg' : line[7:16].strip(),
            'subcateg_name' : line[16:46].strip(),
            'acs_flag' : line[46:47].strip(),
            'disc_flag' : line[47:48].strip(),
            'mbr_disc' : line[48:51].strip(),
            'mommy_disc' : line[51:54].strip()
        }
        return data

    def check_categ(self, categ_code):
        res = self.env['product.category'].search([('code','=', categ_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res

    def check_subcateg(self, subcateg_code):
        res = self.env['product.sub.category'].search([('code','=', subcateg_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res
    
    def create_subcateg(self, rows):
        disc_flag = False
        member_day_discount = 0
        if rows['disc_flag'] == '1':
            disc_flag = True
            member_day_discount = int(rows['mbr_disc'])
            
        vals = {
            'name': rows['subcateg_name'],
            'code': rows['subcateg'],
            'description': rows['subcateg_name'],
            'is_member_day_discount': disc_flag,
            'member_day_discount_percentage': member_day_discount,
            'active': True
        }
        categ_mes,check_categ = self.check_categ(rows['categ'])
        if categ_mes:
            vals.update({'product_category_id': check_categ.id})
            # vals.update({'dept_type': })

        _logger.info("CREATE SUB-CATEGORY")
        _logger.info(vals)
        res = self.env['product.sub.category'].create(vals)

    def update_subcateg(self, rows, subcateg):
        disc_flag = False
        member_day_discount = 0
        if rows['disc_flag'] == '1':
            disc_flag = True
            member_day_discount = int(rows['mbr_disc'])
            
        # res = self.env['product.sub.category'].search([('id','=', subcateg_id)])
        vals = {
            'name': rows['subcateg_name'],
            'code': rows['subcateg'],
            'description': rows['subcateg_name'],
            'is_member_day_discount': disc_flag,
            'member_day_discount_percentage': member_day_discount,
            'active': True
        }
        categ_mes,check_categ = self.check_categ(rows['categ'])
        if categ_mes:
            vals.update({'product_category_id': check_categ.id})
            # vals.update({'dept_type': })

        _logger.info("UPDATE SUB-CATEGORY")
        _logger.info(vals)
        subcateg.write(vals)

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
            self.env['product.subcategory.file'].generate_file(active_id)
            # new_cr.commit()

    def generate_file(self, id):
        # Example : C5C31990.001
        try:
            product_subcategory_file_id = self.env['product.subcategory.file'].browse(id)
            filename = product_subcategory_file_id.filename        
            filename = filename.replace(".","")
            store_code = filename[7:11]
            _logger.info(store_code)

            file_content = base64.b64decode(product_subcategory_file_id.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")

            for line in file_lines:
                _logger.info(str(len(line)))
                rows = self._rows(line)
                _logger.info("rows")
                _logger.info(rows)

                if rows['rec_id'] == "A":
                    check, subcateg = self.check_subcateg(rows['subcateg'])
                    if check:
                        self.update_subcateg(rows, subcateg)
                    else:
                        self.create_subcateg(rows)
                
                if rows['rec_id'] == "D":
                    _logger.info("ARCHIVE SUB-CATEGORY")
                    #sub_categ = self.env['product.sub.category'].search([('code','=', rows['subcateg'])])
                    #sub_categ.write({'active': False})
            
            product_subcategory_file_id.date_end = datetime.now()
            product_subcategory_file_id.state = 'done'
            self.env.cr.commit()

        except Exception as e:
            _logger.error(e)
            product_subcategory_file_id.date_end = datetime.now()
            product_subcategory_file_id.state = 'error'
            self.env.cr.commit()

            
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
        else:
            self._process_download()

    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)
    date_start = fields.Datetime('Start Date', default=datetime.now(), readonly=1)
    date_end = fields.Datetime('End Date', readonly=1)
    is_use_thread = fields.Boolean('Use Threading', default=True)
    download_id = fields.Many2one('pos.interface.download','Download #', ondelete='set null')
    state = fields.Selection([('draft','New'),('in_progress','In Progress'),('done','Finished'),('cancel','Cancel')], 'Status', default='draft')
    
