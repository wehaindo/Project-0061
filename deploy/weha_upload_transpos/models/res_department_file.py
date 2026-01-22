import logging
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _

import base64

_logger = logging.getLogger(__name__)


class res_department_file(models.Model):
    _name= "res.department.file"
    _rec_name="filename"

    def _rows(self, line):
        data = {
            'rec_id' : line[0:1],
            'div' : line[1:4],
            'dept' : line[4:7],
            'dept_name' : line[7:37]
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
        group_mes, group = self.check_group(rows['div'].replace(" ", ""))
        if group_mes:
            vals.update({'group_id': group.id})

        _logger.info("CREATE DEPARTMENT")
        _logger.info(vals)
        res = self.env['res.department'].create(vals)

    def update_dept(self, rows, dept_id):
        res = self.env['res.department'].search([('id','=', dept_id)])
        vals = {
            'name': rows['dept_name'].rstrip(),
            'code': rows['dept'].replace(" ", ""),
            'description': rows['dept_name'].rstrip(),
            'active': True,
        }
        group_mes, group = self.check_group(rows['div'].replace(" ", ""))
        if group_mes:
            vals.update({'group_id': group.id})
            
        _logger.info("UPDATE DEPARTMENT")
        _logger.info(vals)
        res.write(vals)

    def generate_file(self):
        # Example : T5C31990.001
        filename = self.filename
        filename = filename.replace(".","")
        store_code = filename[7:11]
        _logger.info(store_code)

        file_content = base64.b64decode(self.file)
        file_content = file_content.decode("utf-8")
        file_lines = file_content.split("\r\n")

        for line in file_lines:
            _logger.info(str(len(line)))
            rows = self._rows(line)
            _logger.info(rows)

            if rows['rec_id'] == "A":
                check, val = self.check_dept(rows['dept'].replace(" ", ""))
                if check:
                    self.update_dept(rows, val.id)
                else:
                    self.create_dept(rows)
            
            if rows['rec_id'] == "D":
                _logger.info("ARCHIVE DEPARTMENT")
                branch = self.env['res.department'].search([('code','=', rows['dept'].replace(" ", ""))])
                branch.archive()
                

    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)