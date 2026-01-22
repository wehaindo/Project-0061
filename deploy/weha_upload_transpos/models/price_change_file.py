import logging
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _, registry
import threading

import base64

_logger = logging.getLogger(__name__)


class price_change_file(models.Model):
    _name= "price.change.file"
    _rec_name="filename"

    def _rows(self, line):
        data = {
            'rec_id' : line[0:1],
            'item_no' : line[1:14],
            'prc_no' : line[14:24],
            'prc_type' : line[24:30],
            'prc_start_date' : line[30:38],
            'prc_end_date' : line[38:46],
            'prc_start_time' : line[46:50],
            'prc_end_time' : line[50:54],
            'prc_disc_rate' : line[54:60],
            'prc_disc_amt' : line[60:72],
            'prc_sell' : line[72:89]
        }
        return data

    def check_product_pricelist_item(self, pricelist_id, price_change_code):
        res = self.env['product.pricelist.item'].search([('base_pricelist_id','=', pricelist_id), ('prc_no','=', price_change_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res

    def check_product(self, sku):
        res = self.env['product.template'].search([('default_code','=', sku)], limit=1)
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
    
    def create_product_pricelist_item(self, rows, pricelist_id):
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
        vals = {
            'prc_no': rows['prc_no'].replace(" ",""),
            'fixed_price': rows['prc_sell'],
            'date_start': str_start_date,
            'date_end': str_end_date,
            'base_pricelist_id': pricelist_id
        }

        _logger.info("CREATE PRICELIST ITEMS")
        _logger.info(vals)
        res = self.env['product.pricelist.item'].create(vals)

    def update_product_pricelist_item(self, rows, pricelist_item_id):
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
        vals = {
            'prc_no': rows['prc_no'],
            'fixed_price': rows['prc_sell'],
            'date_start': str_start_date,
            'date_end': str_end_date,
        }

        _logger.info("UPDATE PRICELIST ITEMS")
        _logger.info(vals)
        res.write(vals)
    
    def _process_download(self):
        _logger.info("run _process_download")
        # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
        with api.Environment.manage(), self.pool.cursor() as new_cr:
            # new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            # active_id = self.env.context.get('active_id')
            # self.state = 'in_progress'
            # new_cr.commit()
            self.env['price.change.file'].generate_file(5)
            # new_cr.commit()

    def generate_file(self, id):
        # Example : P5C31990.001
        _logger.info("start generate file")
        price_change_file_id = self.env['price.change.file'].browse(id)
        price_change_file_id.state = 'in_progress'
        filename = price_change_file_id.filename
        filename = filename.replace(".","")
        store_code = filename[7:11]
        _logger.info(store_code)

        try:
            file_content = base64.b64decode(price_change_file_id.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")
        except Exception as e:
            _logger.info(e)

        for line in file_lines:
            _logger.info(str(len(line)))
            rows = self._rows(line)
            _logger.info(rows)

            if rows['rec_id'] == "A":
                # Check Product Item No for get branch_id
                product_mes, product = self.check_product(rows['item_no'].replace(" ", ""))
                if product_mes:
                    # Check Product Pricelist by branch_id & prc_type
                    pricelist_mes, pricelist = self.check_product_pricelist(product.branch_id, rows['prc_type'].replace(" ", ""))
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
        
        price_change_file_id.state = 'done'
        _logger.info("stop generate file")


    def process_download(self):
        threaded_download = threading.Thread(target=self._process_download, args=())
        threaded_download.start()
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)
    state = fields.Selection([('draf','New'),('in_progress','In Progress'),('done','Finished'),('cancel','Cancel')], default='draf')