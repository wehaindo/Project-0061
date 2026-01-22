import logging
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _
import threading
import base64

_logger = logging.getLogger(__name__)


class res_department_file(models.Model):
    _name= "res.department.file"
    _rec_name="filename"

    def _rows(self, line):
        data = {
            'rec_id' : line[0:1].strip(),
            'div' : line[1:4].strip(),
            'dept' : line[4:7].strip(),
            'dept_name' : line[7:37].strip()
        }
        return data

    def check_dept(self, dept_code):
        res = self.env['res.department'].search([('code','=', dept_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res
    
    def check_group(self, group_code):
        res = self.env['res.group'].search([('code','=', group_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res

    def create_dept(self, rows):
        vals = {
            'name': rows['dept_name'].rstrip(),
            'code': rows['dept'].replace(" ", ""),
            'description': rows['dept_name'].rstrip(),
            'active': True,
        }
        group_mes, group = self.check_group(rows['div'])
        if group_mes:
            vals.update({'group_id': group.id})

        _logger.info("CREATE DEPARTMENT")
        _logger.info(vals)
        res = self.env['res.department'].create(vals)

    def update_dept(self, rows, dept_id):
        res = self.env['res.department'].search([('id','=', dept_id)])
        vals = {
            'name': rows['dept_name'],
            'code': rows['dept'],
            'description': rows['dept_name'],
            'active': True,
        }
        group_mes, group = self.check_group(rows['div'])
        if group_mes:
            vals.update({'group_id': group.id})
            
        _logger.info("UPDATE DEPARTMENT")
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
            self.env['res.department.file'].generate_file(active_id)
            # new_cr.commit()

    def generate_file(self, id):
        # Example : T5C31990.001
        try:
            res_department_file_id = self.env['res.department.file'].browse(id)
            filename = res_department_file_id.filename
            filename = filename.replace(".","")
            store_code = filename[7:11]
            _logger.info(store_code)

            file_content = base64.b64decode(res_department_file_id.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")

            for line in file_lines:
                _logger.info(str(len(line)))
                rows = self._rows(line)
                _logger.info(rows)

                if rows['rec_id'] == "A":
                    check, val = self.check_dept(rows['dept'])
                    if check:
                        self.update_dept(rows, val.id)
                    else:
                        self.create_dept(rows)
                
                if rows['rec_id'] == "D":
                    _logger.info("ARCHIVE DEPARTMENT")
                    branch = self.env['res.department'].search([('code','=', rows['dept'])])
                    branch.archive()
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
            #threaded_download.join()
            return {'type': 'ir.actions.client', 'tag': 'reload'}                     
        else:
            self._process_download()

    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)
    is_use_thread = fields.Boolean('Use Threading', default=True)
    download_id = fields.Many2one('pos.interface.download','Download #', ondelete='set null')
    state = fields.Selection([('draft','New'),('in_progress','In Progress'),('done','Finished'),('cancel','Cancel')], 'Status', default='draft')
