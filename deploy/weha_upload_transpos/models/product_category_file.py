import logging
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _

import base64

_logger = logging.getLogger(__name__)


class product_category_file(models.Model):
    _name= "product.category.file"
    _rec_name="filename"

    def _rows(self, line):
        data = {
            'rec_id' : line[0:1],
            'dept' : line[1:4],
            'categ' : line[4:10],
            'categ_name' : line[10:50],
            'dept_type' : line[50:51]
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
            'name': rows['categ_name'].rstrip(),
            'code': rows['categ'].replace(" ", ""),
            'active': True
        }
        
        dept_mes, check_dept = self.check_dept(rows['dept'].replace(" ", ""))
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
        dept_mes,check_dept = self.check_dept(rows['dept'].replace(" ", ""))
        if dept_mes:
            vals.update({'dept_id': check_dept.id})
            # vals.update({'dept_type': })

        _logger.info("UPDATE CATEGORY")
        _logger.info(vals)
        res.write(vals)

    def generate_file(self):
        # Example : A5C31990.001
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
                check, val = self.check_categ(rows['categ'].replace(" ", ""))
                if check:
                    self.update_categ(rows, val.id)
                else:
                    self.create_categ(rows)

            if rows['rec_id'] == "D":
                _logger.info("ARCHIVE CATEGORY")
                categ = self.env['product.category'].search([('code','=', rows['categ'].replace(" ", ""))])
                categ.write({'active': False})



    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)