import logging
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _
import threading

import base64

_logger = logging.getLogger(__name__)


class res_division_file(models.Model):
    _name= "res.division.file"
    _rec_name="filename"

    def _rows(self, line):
        data = {
            'rec_id' : line[0:1].strip(),
            'div' : line[1:4].strip(),
            'div_name' : line[4:34].strip(),
            'pmgrp' : line[34:37].strip(),
            'pmgrp_name' : line[37:67].strip()
        }
        return data

    def check_line(self, line_code):
        res = self.env['res.line'].search([('code','=', line_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res

    def check_division(self, division_code):
        res = self.env['res.division'].search([('code','=', division_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res

    def create_division(self, rows):
        vals = {
            'name': rows['div_name'].rstrip(),
            'code': rows['div'].replace(" ", ""),
            'description': rows['div_name'].rstrip(),
            'active': True
        }
        line_mes, line = self.check_line(rows['pmgrp'])
        if line_mes:
            vals.update({'line_id': line.id})

        _logger.info("CREATE DIVISION")
        _logger.info(vals)
        res = self.env['res.division'].create(vals)

    def update_division(self, rows, division_id):
        res = self.env['res.division'].search([('id','=', division_id)])
        vals = {
            'name': rows['div_name'],
            'code': rows['div'],
            'description': rows['div_name']
        }
        line_mes, line = self.check_line(rows['pmgrp'])
        if line_mes:
            vals.update({'line_id': line.id})

        _logger.info("UPDATE DIVISION")
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
            self.env['res.division.file'].generate_file(active_id)
            # new_cr.commit()

    def generate_file(self, id):
        _logger.info("res.division.file")
        try:
            # Example : D5C31990.001
            res_division_file_id = self.env['res.division.file'].browse(id)
            filename = res_division_file_id.filename
            filename = filename.replace(".","")
            store_code = filename[7:11]
            _logger.info(store_code)

            file_content = base64.b64decode(res_division_file_id.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")

            for line in file_lines:
                _logger.info(str(len(line)))
                rows = self._rows(line)
                _logger.info(rows)

                if rows['rec_id'] == "A":
                    check, val = self.check_division(rows['div'])
                    if check:
                        self.update_division(rows, val.id)
                    else:
                        self.create_division(rows)

                if rows['rec_id'] == "D":
                    _logger.info("ARCHIVE DIVISION")
                    division = self.env['res.division'].search([('code','=', rows['div'])])
                    division.archive()

            
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
