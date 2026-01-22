import logging
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _

import base64

_logger = logging.getLogger(__name__)


class group_price_change_file(models.Model):
    _name= "group.price.change.file"
    _rec_name="filename"

    def _rows(self, line):
        data = {
            'rec_no' : line[0:1],
            'prc_no' : line[2:11],
            'prc_type' : line[12:17],
            'prc_start_date' : line[18:25],
            'prc_end_date' : line[26:33],
            'prc_start_time' : line[34:37],
            'prc_end_time' : line[38:42],
            'subcategory' : line[43:51],
            'prc_disc_rate' : line[52:57],
            'exclude_ssn_id' : line[58:63],
            'end_of_record': line[64:65]
        }
        return data
        
    def check_sub_categ(self, subcateg_code):
        res = self.env['product.sub.category'].search([('code','=', subcateg_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res
    
    def create_product_pricelist_item(self, rows, pricelist_id):
        _logger.info("create_product_pricelist_item")
        # Start Date Time
        start_date = rows['prc_start_date'].replace(" ","")
        start_time = rows['prc_start_time'].replace(" ","")
        start_time = f"{start_time[:2]}:{start_time[2:]}:00"
        str_start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2) + " " + start_time
        # End Date Time
        end_date = rows['prc_end_date'].replace(" ","")
        end_time = rows['prc_end_time'].replace(" ","")
        end_time = f"{end_time[:2]}:{end_time[2:]}:00"
        str_end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2) + " " + end_time
        
        mes,subcateg = self.check_sub_categ(rows['subcategory'].replace(" ", ""))
        vals = {
            'prc_no': rows['prc_no'].replace(" ", ""),
            'date_start': str_start_date,
            'date_end': str_end_date,
            'base_pricelist_id': pricelist_id
        }
        if mes == True:
            vals.update({'sub_categ_id': subcateg.id})

        _logger.info("CREATE BRANCH")
        _logger.info(vals)
        res = self.env['product.pricelist.item'].create(vals)

    def update_product_pricelist_item(self, rows, pricelist_item_id):
        _logger.info("update_product_pricelist_item")
        # Start Date Time
        start_date = rows['prc_start_date'].replace(" ","")
        start_time = rows['prc_start_time'].replace(" ","")
        start_time = f"{start_time[:2]}:{start_time[2:]}:00"
        str_start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2) + " " + start_time
        # End Date Time
        end_date = rows['prc_end_date'].replace(" ","")
        end_time = rows['prc_end_time'].replace(" ","")
        end_time = f"{end_time[:2]}:{end_time[2:]}:00"
        str_end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2) + " " + end_time
        
        res = self.env['product.pricelist.item'].search([('id','=', pricelist_item_id)])
        mes,subcateg = self.check_sub_categ(rows['subcategory'].replace(" ", ""))
        vals = {
            'prc_no': rows['prc_no'].replace(" ", ""),
            'date_start': str_start_date,
            'date_end': str_end_date
        }
        if mes == True:
            vals.update({'sub_categ_id': subcateg.id})

        _logger.info("UPDATE BRANCH")
        _logger.info(vals)
        res.write(vals)
    
    def check_store(self, store_code):
        res = self.env['res.branch'].search([('code','=', store_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res
    
    def check_product_pricelist(self, store_id, price_type):
        res = self.env['product.pricelist'].search([('branch_id','=', store_id), ('price_type','=', price_type)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res

    def check_product_pricelist_item(self, pricelist_id, price_change_code):
        res = self.env['product.pricelist.item'].search([('base_pricelist_id','=', pricelist_id), ('prc_no','=', price_change_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res

    def generate_file(self):
        # Example File : G8708000.001
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
                # Check Store
                store_mes, store = self.check_store(store_code)
                if store_mes:
                    # Check Product Pricelist by branch_id & prc_type
                    pricelist_mes, pricelist = self.check_product_pricelist(store.id, rows['prc_type'].replace(" ", ""))
                    if pricelist_mes:
                        # Check Product Pricelist Items by pricelist_id & prc_no
                        check, pricelist_item = self.check_product_pricelist_item(pricelist.id, rows['prc_no'].replace(" ", ""))
                        if check:
                            # UPDATE
                            self.update_product_pricelist_item(rows, pricelist_item.id)
                        else:
                            # CREATE
                            self.create_product_pricelist_item(rows, pricelist.id)
            
            if rows['rec_id'] == "D":
                product_pricelist_item = self.env['product.pricelist.item'].search([('base_pricelist_id','=', pricelist.id), ('prc_no','=', rows['prc_no'].replace(" ", ""))])
                product_pricelist_item.write({'active': False})


    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)