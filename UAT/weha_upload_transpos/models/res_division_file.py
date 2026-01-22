import logging
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _

import base64

_logger = logging.getLogger(__name__)


class res_division_file(models.Model):
    _name= "res.division.file"
    _rec_name="filename"

    def _rows(self, line):
        data = {
            'rec_id' : line[0:1],
            'div' : line[1:4],
            'div_name' : line[4:34],
            'pmgrp' : line[34:37],
            'pmgrp_name' : line[37:67]
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
        line_mes, line = self.check_line(rows['pmgrp'].replace(" ", ""))
        if line_mes:
            vals.update({'line_id': line.id})

        _logger.info("CREATE DIVISION")
        _logger.info(vals)
        res = self.env['res.division'].create(vals)

    def update_division(self, rows, division_id):
        res = self.env['res.division'].search([('id','=', division_id)])
        vals = {
            'name': rows['div_name'].rstrip(),
            'code': rows['div'].replace(" ", ""),
            'description': rows['div_name'].rstrip()
        }
        line_mes, line = self.check_line(rows['pmgrp'].replace(" ", ""))
        if line_mes:
            vals.update({'line_id': line.id})

        _logger.info("UPDATE DIVISION")
        _logger.info(vals)
        res.write(vals)

    def generate_file(self):
        # Example : D5C31990.001
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
                check, val = self.check_division(rows['div'].replace(" ", ""))
                if check:
                    self.update_division(rows, val.id)
                else:
                    self.create_division(rows)

            if rows['rec_id'] == "D":
                _logger.info("ARCHIVE DIVISION")
                division = self.env['res.division'].search([('code','=', rows['div'].replace(" ", ""))])
                division.archive()



    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)