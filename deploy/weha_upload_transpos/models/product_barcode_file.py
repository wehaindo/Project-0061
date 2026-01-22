import logging
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _

import base64

_logger = logging.getLogger(__name__)


class product_barcode_file(models.Model):
    _name= "product.barcode.file"
    _rec_name="filename"

    def _rows(self, line):
        data = {
            'rec_id' : line[0:1],
            'sku_number' : line[1:14],
            'barcode_no' : line[14:32]
        }
        return data

    def check_barcode(self, barcode_code):
        res = self.env['product.tamplate'].search([('default_code','=', barcode_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res
    
    def create_barcode(self, rows):
        vals = {
            # 'default_code': rows['sku_number'],
            'barcode': rows['barcode_no'].replace(" ", ""),
        }
        _logger.info("CREATE BARCODE")
        _logger.info(vals)
        res = self.env['product.template'].create(vals)

    def update_barcode(self, rows, barcode_id):
        res = self.env['product.template'].search([('id','=', barcode_id)])
        if res:
            vals = {
                # 'default_code': rows['sku_number'],
                'barcode': rows['barcode_no'].replace(" ", ""),
            }
            _logger.info("UPDATE BARCODE")
            _logger.info(vals)
            res.write(vals)

    def generate_file(self):
        # Example : B5C31990.001
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
                check, val = self.check_barcode(rows['sku_number'].replace(" ", ""))
                if check:
                    self.update_barcode(rows, val.id)
                else:
                    self.create_barcode(rows)



    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)