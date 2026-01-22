import logging
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _
import threading
import base64

_logger = logging.getLogger(__name__)


class product_category_file(models.Model):
    _name= "product.category.file"
    _rec_name="filename"

    def _rows(self, line):
        data = {
            'rec_id' : line[0:1].strip(),
            'dept' : line[1:4].strip(),
            'categ' : line[4:10].strip(),
            'categ_name' : line[10:50].strip(),
            'dept_type' : line[50:51].strip()
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

    def check_dept(self, dept_code):
        res = self.env['res.department'].search([('code','=', dept_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res
    
    def create_categ(self, rows):
        vals = {
            'name': rows['categ_name'],
            'code': rows['categ'].replace(" ", ""),
            'active': True
        }
        
        dept_mes, check_dept = self.check_dept(rows['dept'])
        if dept_mes:
            vals.update({'dept_id': check_dept.id})
            # vals.update({'dept_type': })

        _logger.info("CREATE CATEGORY")
        _logger.info(vals)
        res = self.env['product.category'].create(vals)

    def update_categ(self, rows, categ_id):
        res = self.env['product.category'].search([('id','=', categ_id)])
        vals = {
            'name': rows['categ_name'].rstrip(),
            'code': rows['categ'].replace(" ", ""),
        }
        dept_mes,check_dept = self.check_dept(rows['dept'])
        if dept_mes:
            vals.update({'dept_id': check_dept.id})
            # vals.update({'dept_type': })

        _logger.info("UPDATE CATEGORY")
        _logger.info(vals)
        res.write(vals)

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
            self.env['product.category.file'].generate_file(active_id)
            # new_cr.commit()

    def generate_file(self, id):
        # Example : A5C31990.001
        try:
            product_category_file_id = self.env['product.category.file'].browse(id)
            filename = product_category_file_id.filename        
            filename = filename.replace(".","")
            store_code = filename[7:11]
            _logger.info(store_code)

            file_content = base64.b64decode(product_category_file_id.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")

            for line in file_lines:
                _logger.info(str(len(line)))
                rows = self._rows(line)
                _logger.info(rows)

                if rows['rec_id'] == "A":
                    check, val = self.check_categ(rows['categ'])
                    if check:
                        self.update_categ(rows, val.id)
                    else:
                        self.create_categ(rows)

                if rows['rec_id'] == "D":
                    _logger.info("ARCHIVE CATEGORY")
                    categ = self.env['product.category'].search([('code','=', rows['categ'])])
                    categ.write({'active': False})
        except Exception as e:
            _logger.error(e)
        
    def cron_process_download(self):     
        #Running Thread
        if self.is_use_thread:
            _logger.info("running thread")
            threaded_download = threading.Thread(target=self._process_download, args=())
            threaded_download.start()   
            threaded_download.join()        
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