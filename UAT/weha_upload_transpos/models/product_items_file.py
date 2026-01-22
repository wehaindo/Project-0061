import logging
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _, registry
import threading
import time

import base64

_logger = logging.getLogger(__name__)


class product_items_file(models.Model):
    _name= "product.items.file"
    _rec_name="filename"


    def _rows(self, line):
        data = {
            'rec_id' : line[0:1],                   # OK
            'item_no' : line[1:14],                 # OK
            'item_short_name' : line[14:29],        # OK
            'item_long_name' : line[29:59],
            'item_short_name_chinese' : line[59:79],
            'item_long_name_chinese' : line[79:119],
            'item_barcode' : line[119:137],         # OK
            'item_sell' : line[137:154],            # OK
            'item_member_sell' : line[154:171],     # OK
            'item_uom' : line[171:176],             # OK
            'item_div' : line[176:179],             # OK
            'item_dept' : line[179:182],            # OK
            'item_categ' : line[182:188],           # OK
            'item_subcateg' : line[188:197],        # OK
            'item_weight' : line[197:198],
            'item_plu_flag' : line[198:199],
            'item_date' : line[199:207],
            'item_vat_flag' : line[207:208], 
            'item_vat_percent' : line[208:211], 
            'season_id' : line[211:217],
            'sales_tax' : line[217:220], 
            'kadsim_flag' : line[220:221],          # tidak digunakan
            'valid_to_use_date' : line[221:224],    # tidak digunakan
            'card_flag' : line[224:225],  # 0 = NON Discount, 1 = Mommy Item, 2 = aeon card % item, 3 = Mommy + aeon % item
            'item_uom2' : line[225:233], 
            'print_prod_flag' : line[233:234],
            'tax_code' : line[234:241]              # OK
        }
        return data
    
    def check_account_tax(self):
        sqlgroup="""SELECT id, code FROM account_tax GROUP BY id, code"""
        self.env.cr.execute(sqlgroup)
        groups = self.env.cr.dictfetchall()
        self.env.cr.commit()
        return groups
    
    def check_uom(self):
        sqlgroup="""SELECT id, code FROM uom_uom GROUP BY id, code"""
        self.env.cr.execute(sqlgroup)
        groups = self.env.cr.dictfetchall()
        self.env.cr.commit()
        return groups
    
    def check_div(self):
        sqlgroup="""SELECT id, code FROM res_division GROUP BY id, code"""
        self.env.cr.execute(sqlgroup)
        groups = self.env.cr.dictfetchall()
        self.env.cr.commit()
        return groups
    
    def check_dept(self):
        sqlgroup="""SELECT id, code FROM res_department GROUP BY id, code"""
        self.env.cr.execute(sqlgroup)
        groups = self.env.cr.dictfetchall()
        self.env.cr.commit()
        return groups

    def check_categ(self):
        sqlgroup="""SELECT id, code FROM product_category GROUP BY id, code"""
        self.env.cr.execute(sqlgroup)
        groups = self.env.cr.dictfetchall()
        self.env.cr.commit()
        return groups

    def check_subcateg(self):
        sqlgroup="""SELECT id, code FROM product_sub_category GROUP BY id, code"""
        self.env.cr.execute(sqlgroup)
        groups = self.env.cr.dictfetchall()
        self.env.cr.commit()
        return groups
  
    def check_product(self, product_code):
        res = self.env['product.template'].search([('default_code','=', product_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res
        
    def check_product_store(self, product_id, store_id):
        product = self.env['product.template'].search([('id','=', product_id), ('branch_ids','in', store_id)], limit=1)
        if product:
            mes = True
            return mes
        else:
            mes = False
            return mes
            
    def update_product(self, rows, product_id, store_id, list_uom, list_tax, list_div, list_dept, list_categ, list_subcateg):
        product = self.env['product.template'].search([('id','=', product_id)], limit=1)
        vals = {
            'name': rows['item_long_name'].rstrip(),
            'default_code': rows['item_no'].replace(" ", ""),
            'list_price': rows['item_sell'],
            'available_in_pos': True,
            'active': True
        }

        product_store = self.check_product_store(product_id, store_id)
        if product_store != True:
            vals.update({'branch_ids': [(4, store_id)]})

        res_tax = list(filter(lambda list_tax: list_tax['code'] == str(rows['tax_code'].replace(" ", "")), list_tax))
        for tax in res_tax:
            vals.update({'taxes_id': tax['id']})

        res_uom = list(filter(lambda list_uom: list_uom['code'] == str(rows['item_uom'].replace(" ", "")), list_uom))
        for uom in res_uom:
            vals.update({'uom_id' : uom['id']})

        res_div = list(filter(lambda list_div: list_div['code'] == str(rows['item_div'].replace(" ", "")), list_div))
        for div in res_div:
            vals.update({'division_id' : div['id']})

        res_dept = list(filter(lambda list_dept: list_dept['code'] == str(rows['item_dept'].replace(" ", "")), list_dept))
        for dept in res_dept:
            vals.update({'dept_id': dept['id']})

        res_categ = list(filter(lambda list_categ: list_categ['code'] == str(rows['item_categ'].replace(" ", "")), list_categ))
        for categ in res_categ:
            vals.update({'categ_id': categ['id']})

        res_subcateg = list(filter(lambda list_subcateg: list_subcateg['code'] == str(rows['item_subcateg'].replace(" ", "")), list_subcateg))
        for subcateg in res_subcateg:
            vals.update({'sub_categ_id': subcateg['id']})

        _logger.info("UPDATE PRODUCT")
        _logger.info(vals)
        product.write(vals)

        # UPDATE HARGA product.template.price
        # args = [('product_template_id','=', product.id), ('res_branch_id','=', store_id)]
        # _logger.info(str(args))
        # product_tmpl_price = self.env['product.template.price'].search(args)

        # product_tmpl_price.sudo().write({'member_price': rows['item_member_sell'], 'list_price': rows['item_sell']})
        # product.action_update_store_product()
        self.env.cr.commit()

    def create_product(self, rows, store_id, list_uom, list_tax, list_div, list_dept, list_categ, list_subcateg):
        vals = {
            'name': rows['item_long_name'].rstrip(),
            'default_code': rows['item_no'].replace(" ", ""),
            'list_price': rows['item_sell'],
            'barcode': rows['item_barcode'].replace(" ", ""),
            'branch_ids': [store_id],
            'pos_categ_id': 1,
            'available_in_pos': True,
            'active': True
        }

        res_tax = list(filter(lambda list_tax: list_tax['code'] == str(rows['tax_code'].replace(" ", "")), list_tax))
        for tax in res_tax:
            vals.update({'taxes_id': tax['id']})

        res_uom = list(filter(lambda list_uom: list_uom['code'] == str(rows['item_uom'].replace(" ", "")), list_uom))
        for uom in res_uom:
            vals.update({'uom_id' : uom['id']})

        res_div = list(filter(lambda list_div: list_div['code'] == str(rows['item_div'].replace(" ", "")), list_div))
        for div in res_div:
            vals.update({'division_id' : div['id']})

        res_dept = list(filter(lambda list_dept: list_dept['code'] == str(rows['item_dept'].replace(" ", "")), list_dept))
        for dept in res_dept:
            vals.update({'dept_id': dept['id']})

        res_categ = list(filter(lambda list_categ: list_categ['code'] == str(rows['item_categ'].replace(" ", "")), list_categ))
        for categ in res_categ:
            vals.update({'categ_id': categ['id']})

        res_subcateg = list(filter(lambda list_subcateg: list_subcateg['code'] == str(rows['item_subcateg'].replace(" ", "")), list_subcateg))
        for subcateg in res_subcateg:
            vals.update({'sub_categ_id': subcateg['id']})
   

        # _logger.info("CREATE PRODUCT")
        # _logger.info(vals)
        res = self.env['product.template'].create(vals)

        # UPDATE HARGA product.template.price
        # res.action_update_store_product()
        # args = [('product_template_id','=', res.id), ('res_branch_id','=', store_id)]
        # _logger.info(str(args))
        # product_tmpl_price = self.env['product.template.price'].search(args)
        # product_tmpl_price.sudo().write({'member_price': rows['item_member_sell']})
        self.env.cr.commit()

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
            new_cr.commit()
            self.env['product.items.file'].generate_file(active_id)
            # new_cr.commit()
       
    def generate_file(self, id):
        # Example File : I5C31990.001
        count = 0
        _logger.info("start generate file")
        product_items_file_id = self.env['product.items.file'].browse(id)
        product_items_file_id.state = 'in_progress'
        filename = product_items_file_id.filename
        filename = filename.replace(".","")
        store_code = filename[7:11]
        try:
            file_content = base64.b64decode(product_items_file_id.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")
        except Exception as e:
            _logger.error(e)

        try:
            # SAVE distinery ID, CODE in VARIABEL
            uom = self.check_uom()
            tax = self.check_account_tax()
            div = self.check_div()
            dept = self.check_dept()
            categ = self.check_categ()
            subcateg = self.check_subcateg()
        except Exception as e:
            _logger.error(e)

        for line in file_lines:
            count = count + 1
            rows = self._rows(line)
            _logger.info(count)
            # _logger.info(rows)
            if rows['rec_id'] == "A":
                check, product = self.check_product(rows['item_no'].replace(" ", ""))
                store_id = self.env['res.branch'].search([('code','=', store_code)], limit=1)
                if store_id:
                    if check:
                        self.update_product(rows, product.id, store_id.id, uom, tax, div, dept, categ, subcateg)
                    else:
                        self.create_product(rows, store_id.id, uom, tax, div, dept, categ, subcateg)

            if rows['rec_id'] == "D":
                # _logger.info("ARCHIVE PRODUCT")
                product = self.env['product.template'].search([('default_code','=', rows['item_no'].replace(" ", ""))], limit=1)
                product.write({'active': False})

            if count == 500:
                time.sleep(10)
            #     count = 0
            #     _logger.info("commit 500")
            count = count + 1

        product_items_file_id.state = 'done'
        product_items_file_id.date_end = datetime.now()
        self.cr.commit()

        _logger.info("stop generate file")

    def process_download(self): 
        threaded_download = threading.Thread(target=self._process_download, args=())
        threaded_download.start()
        return {'type': 'ir.actions.client', 'tag': 'reload'}
    
    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)
    date_start = fields.Datetime('Start Date', default=datetime.now(), readonly=1)
    date_end = fields.Datetime('End Date', readonly=1)
    state = fields.Selection([('draf','New'),('in_progress','In Progress'),('done','Finished'),('cancel','Cancel')])
