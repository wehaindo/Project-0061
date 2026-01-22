import logging
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _

import base64

_logger = logging.getLogger(__name__)


class product_subcategory_file(models.Model):
    _name= "product.subcategory.file"
    _rec_name="filename"

    def _rows(self, line):
        data = {
            'rec_id' : line[0:1],
            'categ' : line[1:7],
            'subcateg' : line[7:16],
            'subcateg_name' : line[16:46],
            'acs_flag' : line[46:47],
            'disc_flag' : line[50:48],
            'mbr_disc' : line[48:51],
            'mommy_disc' : line[51:54]
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
        vals = {
            'name': rows['subcateg_name'].rstrip(),
            'code': rows['subcateg'].replace(" ", ""),
            'description': rows['subcateg_name'].rstrip(),
            'active': True
        }
        categ_mes,check_categ = self.check_categ(rows['categ'].replace(" ", ""))
        if categ_mes:
            vals.update({'product_category_id': check_categ.id})
            # vals.update({'dept_type': })

        _logger.info("CREATE SUB-CATEGORY")
        _logger.info(vals)
        res = self.env['product.sub.category'].create(vals)

    def update_subcateg(self, rows, subcateg_id):
        res = self.env['product.sub.category'].search([('id','=', subcateg_id)])
        vals = {
            'name': rows['subcateg_name'].rstrip(),
            'code': rows['subcateg'].replace(" ", ""),
            'description': rows['subcateg_name'].rstrip(),
            'active': True
        }
        categ_mes,check_categ = self.check_categ(rows['categ'].replace(" ", ""))
        if categ_mes:
            vals.update({'product_category_id': check_categ.id})
            # vals.update({'dept_type': })

        _logger.info("UPDATE SUB-CATEGORY")
        _logger.info(vals)
        res.write(vals)

    def generate_file(self):
        # Example : C5C31990.001
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
                check, subcateg = self.check_subcateg(rows['categ'].replace(" ", ""))
                if check:
                    self.update_subcateg(rows, subcateg.id)
                else:
                    self.create_subcateg(rows)
            
            if rows['rec_id'] == "D":
                _logger.info("ARCHIVE SUB-CATEGORY")
                sub_categ = self.env['product.sub.category'].search([('code','=', rows['categ'].replace(" ", ""))])
                sub_categ.write({'active': False})


    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)