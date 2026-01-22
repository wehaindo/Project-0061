from concurrent.futures import ThreadPoolExecutor
from functools import partial
import logging
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _, registry
import threading
import time
import numpy as np
import json
import base64
import requests
from requests.auth import HTTPBasicAuth

_logger = logging.getLogger(__name__)


create_bulk_docs = []
update_bulk_docs = []

COUCHDB_URL = "https://couchdb.server1601.weha-id.com"


def match_doc(doc, compare_value):
#   _logger.info(doc)
#   _logger.info(compare_value)
  if doc is None:
      return False
  elif compare_value is None:
      return False
  elif doc['_id'] == compare_value:
    return True
  else:
    return False

def process_docs(couchdb_datas, parent):
    _logger.info('process_docs')
    couchdb_data_ids = []
    for couchdb_data in couchdb_datas:                        
        couchdb_data_ids.append(couchdb_data['_id'])  
    #Get Data on Couchdb using doc key
    # _logger.info(couchdb_data_ids)
    couchdb_datas_on_server = parent.get_couchdb_data_by_key(couchdb_data_ids)    
    #Filter and Update DOc for Update to CouchDB Server
    couhcdb_datas_match = []   
    for couchdb_data in couchdb_datas:                        
        partial_func = partial(match_doc, compare_value=couchdb_data['_id'])
        match_data = list(filter(partial_func, couchdb_datas_on_server))
        if not match_data:                
            couhcdb_datas_match.append(couchdb_data)
        else:
            # _logger.info('match_data')
            # _logger.info(couchdb_data)           
            # _logger.info(match_data[0])   
            match_couchdb_data = match_data[0]
            match_couchdb_data.update(couchdb_data)                                                     
            # couchdb_data.update(match_data[0])                                               
            couhcdb_datas_match.append(match_couchdb_data)
    #Update to CouchDB Server
    _logger.info(len(couhcdb_datas_match))
    return couhcdb_datas_match

def update_docs(batch):
    _logger.info('update_docs')
    # COUCHDB_URL = "https://couchdb.server1601.weha-id.com"
    DATABASE = "s_7001_products"
    
    url = f"{COUCHDB_URL}/{DATABASE}/_bulk_docs"
    headers = {"Content-Type": "application/json"}
    data = {"docs": batch}
    response = requests.post(url, auth=('admin', 'pelang1'), headers=headers, data=json.dumps(data))
    # _logger.info(response.status_code)
    return response.json()
    
class product_items_file(models.Model):
    _name= "product.items.file"
    _rec_name="filename"
    _order = "date_start desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('product_items_line_ids')
    def get_product_items_line_count(self):
        for row in self:
            row.items_line_count = len(row.product_items_line_ids)

    def get_couchdb_data_by_key(self, keys):
        _logger.info('get_couchdb_data_by_key')
        auth = HTTPBasicAuth('admin','pelang1')
        headers = {
            'Content-Type': 'application/json'                  
        }         
        
        # CouchDB connection details
        # COUCHDB_URL = "https://couchdb.server1601.weha-id.com"
        DATABASE = "s_7001_products"
        URL = f"{COUCHDB_URL}/{DATABASE}/_all_docs"

        # List of document IDs to retrieve
        ids = keys

        # Make a POST request with the 'keys' parameter
        response = requests.post(
            f"{URL}?include_docs=true",
            headers=headers,
            data=json.dumps({"keys": ids}),
            auth=('admin', 'pelang1'),          
        )

        # Parse and print the response
        couchdb_datas = []        
        if response.status_code == 200:                       
            rows = response.json()["rows"]
            count = 0
            for row in rows:
                count = count + 1
                if 'doc' in row:                                
                    couchdb_datas.append(row['doc'])
                # if count == 5500:
                #     break
        else:
            # print("Error:", response.status_code, response.text)
            _logger.error('Error')
            _logger.error(response.status_code)
            # _logger.error(response.text)
                    
        return couchdb_datas 
    
    def update_couch_data_to_server(self, results):   
        _logger.info('update_couch_data_to_server')     
        # _logger.info(len(results))
        # Divide documents into batches
        # batch_size = 500
        # batches = [couchdb_datas[i:i+batch_size] for i in range(0, len(couchdb_datas), batch_size)]

        # Use ThreadPoolExecutor to process batches in parallel    
        with ThreadPoolExecutor(max_workers=5) as executor:            
            results = executor.map(update_docs, results)        
            
    def get_filter_and_update_data(self, couchdb_data, couchdb_datas_on_server):  
        couchdb_datas_match = []      
        for couchdb_data in couchdb_datas:
            partial_func = partial(match_doc, compare_value=couchdb_data['_id'])
            match_data = list(filter(partial_func, couchdb_datas_on_server))
            if not match_data:                
                couchdb_datas_match.append(couchdb_data)                            
            elif len(match_data) == 1:
                # _logger.info('match_data')           
                # _logger.info(match_data[0])            
                couchdb_data.update(match_data[0])                                               
                couchdb_datas_match.append(couchdb_data)    
        self.update_docs(couchdb_datas_match)
        
    def action_view_product_items_line(self):
        return {
            'name': _('Lines'),
            'res_model': 'product.items.line',
            'view_mode': 'tree,form',
            'views': [
                (self.env.ref('weha_upload_transpos.view_product_items_line_tree').id, 'tree'),
                (self.env.ref('weha_upload_transpos.view_product_items_line_form').id, 'form'),
                ],
            'type': 'ir.actions.act_window',
            'domain': [('product_items_file_id', 'in', self.ids)],
        }

    def process_split_file(self):
        lines_per_file = 300
        smallfile = None
        with open('really_big_file.txt') as bigfile:
            for lineno, line in enumerate(bigfile):
                if lineno % lines_per_file == 0:
                    if smallfile:
                        smallfile.close()
                    small_filename = 'small_file_{}.txt'.format(lineno + lines_per_file)
                    smallfile = open(small_filename, "w")
                smallfile.write(line)
            if smallfile:
                smallfile.close()

    def _rows(self, line):                
        data = {
            'rec_id' : line[0:1].strip(),                   # OK
            'item_no' : line[1:14].strip(),                 # OK
            'item_short_name' : line[14:29].strip(),        # OK
            'item_long_name' : line[29:59].strip(),
            'item_short_name_chinese' : line[59:79].strip(),
            'item_long_name_chinese' : line[79:119].strip(),
            'item_barcode' : line[119:137].strip(),         # OK
            'item_sell' : line[137:154].strip(),            # OK
            'item_member_sell' : line[154:171].strip(),     # OK
            'item_uom' : line[171:176].strip(),             # OK
            'item_div' : line[176:179].strip(),             # OK
            'item_dept' : line[179:182].strip(),            # OK
            'item_categ' : line[182:188].strip(),           # OK
            'item_subcateg' : line[188:197].strip(),        # OK
            'item_weight' : line[197:198].strip(),
            'item_plu_flag' : line[198:199].strip(),
            'item_date' : line[199:207].strip(),
            'item_vat_flag' : line[207:208].strip(), 
            'item_vat_percent' : line[208:211].strip(), 
            'season_id' : line[211:217].strip(),
            'sales_tax' : line[217:220].strip(), 
            'kadsim_flag' : line[220:221].strip(),          # tidak digunakan
            'valid_to_use_date' : line[221:224].strip(),    # tidak digunakan
            'card_flag' : line[224:225].strip(),  # 0 = NON Discount, 1 = Mommy Item, 2 = aeon card % item, 3 = Mommy + aeon % item
            'item_uom2' : line[225:233].strip(), 
            'print_prod_flag' : line[233:234].strip(),
            'tax_code' : line[234:241].strip()              # OK
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
    
    def check_line(self, div_id):
        division_id = self.env['res.division'].browse(div_id)
        return division_id.line_id.id
    
    def check_div(self):
        sqlgroup="""SELECT id, code FROM res_division GROUP BY id, code"""
        self.env.cr.execute(sqlgroup)
        groups = self.env.cr.dictfetchall()
        #self.env.cr.commit()
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
        #res = self.env['product.template'].search([('default_code','=', product_code)], limit=1)
        domain  = [
            ('default_code','=', product_code),
            ('active','=', True)
        ]
        res = self.env['product.template'].search([('default_code','=', product_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, {}
        
    def check_product_store(self, product_id, store_id):
        domain = [
            ('branch_id','=', store_id),
            ('price_type','=', 'Store')
        ]
        store_pricelist_id = self.env['product.pricelist'].search(domain, limit=1)
        if store_pricelist_id:
            domain = [
                ('product_tmpl_id','=', product_id),
                ('pricelist_id','=', store_pricelist_id.id)
            ]
            product_pricelist_item_id = self.env['product.pricelist.item'].search(domain, limit=1)            
            if product_pricelist_item_id:
                mes = True
                return mes
            else:
                mes = False
                return mes 

        # product = self.env['product.template'].search([('id','=', product_id), ('branch_ids','in', store_id)], limit=1)
        # if product:
        #     mes = True
        #     return mes
        # else:
        #     mes = False
        #     return mes
            
    def update_product(self, rows, product_id, store_id, list_uom, list_tax, list_div, list_dept, list_categ, list_subcateg):
        # _logger.info(rows)
        product = self.env['product.template'].search([('id','=', product_id)], limit=1)
        vals = {
            'name': rows['item_long_name'],
            'list_price': 0,
            'available_in_pos': True,
            'active': True,
            'detailed_type': 'product',
            # 'barcode': rows['item_barcode'],
        }

        vals.update({'branch_ids': [
            (4, store_id)
        ]})        

        res_tax = list(filter(lambda list_tax: list_tax['code'] == str(rows['tax_code']), list_tax))
        if res_tax:
            for tax in res_tax:
                vals.update({'taxes_id': [
                    (6, 0, [tax['id']])
                ]})

        res_uom = list(filter(lambda list_uom: list_uom['code'] == str(rows['item_uom']), list_uom))
        for uom in res_uom:
            vals.update({'uom_id' : uom['id']})
        
        # _logger.info('list_div')
        # _logger.info(list_div)
        # _logger.info('item_div')
        # _logger.info(rows['item_div'])
        # res_div = list(filter(lambda list_div: list_div['code'] == str(rows['item_div']), list_div))
        # _logger.info(res_div)
        # for div in res_div:
        #     _logger.info('found division')
        #     vals.update({'division_id' : div['id']})
        for div in list_div:
            # _logger.info(div)
            if div['code'] == int(rows['item_div']):
                _logger.info('match')
                vals.update({'division_id' : div['id']})      
                vals.update({'line_id': self.check_line(div['id'])})

        # _logger.info(vals)

        res_dept = list(filter(lambda list_dept: list_dept['code'] == str(rows['item_dept']), list_dept))
        for dept in res_dept:
            vals.update({'dept_id': dept['id']})

        res_categ = list(filter(lambda list_categ: list_categ['code'] == str(rows['item_categ']), list_categ))
        for categ in res_categ:
            vals.update({'categ_id': categ['id']})

        res_subcateg = list(filter(lambda list_subcateg: list_subcateg['code'] == str(rows['item_subcateg']), list_subcateg))
        for subcateg in res_subcateg:
            vals.update({'sub_categ_id': subcateg['id']})

        # _logger.info("UPDATE PRODUCT")
        # _logger.info(vals)
        try:
            context = dict(self._context or {})
            context['cron_process_download'] = True           
            product.with_context(context).write(vals)       
            #Update Price Store   
            product_store_vals = {
                'res_branch_id': store_id,
                'product_template_id': product.id,
                'list_price': float(rows['item_sell'])
            }
            #weha_smart_pos_aeon_pos_data
            product.update_store_product(product_store_vals)    
            self.env.cr.commit()                  
            #Sync Product To CouchDB
            product.action_sync_product_by_branch(store_id)
            self.env.cr.commit()
            #Update Product Barcode
            if product.has_multiple_barcode:                
                product.barcode_ids.action_sync_product()
                
        except Exception as e:
            _logger.error(e)

    def update_product_with_line(self, line, rows, product_id, store_id, list_uom, list_tax, list_div, list_dept, list_categ, list_subcateg):
        _logger.info("update_product_with_line")
        # _logger.info(rows)        
        # try:            
        # product = self.env['product.template'].search([('id','=', product_id)], limit=1)
        if product_id:
            # _logger.info(f'Start Browse Product {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
            product = self.env['product.template'].browse(product_id)
            # _logger.info(f'End Browse Product {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
            vals = {
                'name': rows['item_long_name'],
                'list_price': 0,
                'available_in_pos': True,
                'active': True,
                'detailed_type': 'product',
                # 'barcode': rows['item_barcode'],
            }
            vals.update({'branch_ids': [
                (4, store_id)
            ]})        
            # _logger.info(f'Start Check Master {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
            res_tax = list(filter(lambda list_tax: list_tax['code'] == str(rows['tax_code']), list_tax))
            if res_tax:
                for tax in res_tax:
                    vals.update({'taxes_id': [
                        (6, 0, [tax['id']])
                    ]})

            res_uom = list(filter(lambda list_uom: list_uom['code'] == str(rows['item_uom']), list_uom))
            for uom in res_uom:
                vals.update({'uom_id' : uom['id']})
            
            for div in list_div:
                # _logger.info(div)
                if div['code'] == int(rows['item_div']):
                    _logger.info('match')
                    vals.update({'division_id' : div['id']})      
                    vals.update({'line_id': self.check_line(div['id'])})

            # _logger.info(vals)

            res_dept = list(filter(lambda list_dept: list_dept['code'] == str(rows['item_dept']), list_dept))
            for dept in res_dept:
                vals.update({'dept_id': dept['id']})

            res_categ = list(filter(lambda list_categ: list_categ['code'] == str(rows['item_categ']), list_categ))
            for categ in res_categ:
                vals.update({'categ_id': categ['id']})

            res_subcateg = list(filter(lambda list_subcateg: list_subcateg['code'] == str(rows['item_subcateg']), list_subcateg))
            for subcateg in res_subcateg:
                vals.update({'sub_categ_id': subcateg['id']})

            # _logger.info(f'End Check Master {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')                
            
            # _logger.info(f'Start Update Product {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
            context = dict(self._context or {})
            context['cron_process_download'] = True           
            product.with_context(context).write(vals)       
            # _logger.info(f'End Update Product1 {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
            
            #Update Price Store   
            # _logger.info(f'Start Update Price Store {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
            product_store_vals = {
                'res_branch_id': store_id,
                'product_template_id': product.id,
                'list_price': float(rows['item_sell'])
            }                                                
            product.update_store_product(product_store_vals)    
            # _logger.info(f'End Update Price Store {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
            # self.env.cr.commit()    
            
            #Sync Product To CouchDB
            # _logger.info(f'Start Sync Product {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')                
            # product.action_sync_product_by_branch(store_id)
            product.generate_product_json_by_branch(store_id)
            # line.couchdb_data = product.
            # _logger.info(f'End Sync Product {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
            # self.env.cr.commit()

            #Update Product Barcode
            # _logger.info(f'Start Update Product Barcode {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
            product_barcode_vals = {
                'branch_id' : store_id,
                'product_id': product.id,
                'barcode': rows['item_barcode']
            }
            product.update_product_barcode(product_barcode_vals)           
            # _logger.info(f'End Update Product Barcode {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
            self.env.cr.commit()
            
            # _logger.info('product.product_template_data_ids')
            # _logger.info(product.product_template_data_ids)
            product_template_couchdb_id = product.product_template_data_ids.filtered(lambda r:r.branch_id.id == store_id)
            _logger.info("product_template_couchdb_id")
            _logger.info(product_template_couchdb_id)
            line.couchdb_data =  product_template_couchdb_id.product_json
                        
            # _logger.info(f'Start Update Line Status {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')    
            line.state = 'done'
            line.err_msg = "Successfully"
            self.env.cr.commit()
            # _logger.info(f'End Update Line Status {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')    
        else:
            line.state = 'error'
            line.err_msg = "Product not Found"
            self.env.cr.commit()
        # except Exception as e:
        #     line.state = 'error'
        #     line.err_msg = str(e)
        #     # self.env.cr.commit()
        #     _logger.error(e)

    def create_product(self, rows, store_id, list_uom, list_tax, list_div, list_dept, list_categ, list_subcateg):        
        _logger.info("create_product")
        vals = {
            'name': rows['item_long_name'],
            'default_code': rows['item_no'],
            'list_price': 0,
            # 'barcode': rows['item_barcode'],
            'branch_ids': [store_id],
            'pos_categ_id': 1,
            'available_in_pos': True,
            'active': True,
            'detailed_type': 'product' 
        }

        _logger.info(vals)

        res_tax = list(filter(lambda list_tax: list_tax['code'] == str(rows['tax_code']), list_tax))
        _logger.info(res_tax)
        if res_tax:
            for tax in res_tax:
                vals.update({'taxes_id': [
                            (6, 0, [tax['id']])
                        ]})

        res_uom = list(filter(lambda list_uom: list_uom['code'] == str(rows['item_uom']), list_uom))
        for uom in res_uom:
            vals.update({'uom_id' : uom['id']})

        res_div = list(filter(lambda list_div: list_div['code'] == str(rows['item_div']), list_div))
        for div in res_div:
            vals.update({'division_id' : div['id']})

        res_dept = list(filter(lambda list_dept: list_dept['code'] == str(rows['item_dept']), list_dept))
        for dept in res_dept:
            vals.update({'dept_id': dept['id']})

        res_categ = list(filter(lambda list_categ: list_categ['code'] == str(rows['item_categ']), list_categ))
        for categ in res_categ:
            vals.update({'categ_id': categ['id']})

        res_subcateg = list(filter(lambda list_subcateg: list_subcateg['code'] == str(rows['item_subcateg']), list_subcateg))
        for subcateg in res_subcateg:
            vals.update({'sub_categ_id': subcateg['id']})   
        # _logger.info("CREATE PRODUCT")        
        try:
            context = dict(self._context or {})
            context['cron_process_download'] = True
            product_template_id = self.env['product.template'].with_context(context).create(vals)    
            _logger.info(product_template_id)
            #Update Product Store                
            product_store_vals = {
                    'res_branch_id': store_id,
                    'product_template_id': product_template_id.id,
                    'list_price': float(rows['item_sell'])
            }
            product_template_id.update_store_product(product_store_vals)
            self.env.cr.commit()
            product_template_id.action_sync_product_by_branch(store_id)            
            self.env.cr.commit()
        except Exception as e:
            _logger.error(e)

    def create_product_with_line(self, line, rows, store_id, list_uom, list_tax, list_div, list_dept, list_categ, list_subcateg):        
        _logger.info("create_product")
        try:        
            vals = {
                'name': rows['item_long_name'],
                'default_code': rows['item_no'],
                'list_price': 0,                
                'branch_ids': [store_id],
                'pos_categ_id': 1,
                'available_in_pos': True,
                'active': True,
                'detailed_type': 'product' 
            }
            _logger.info(vals)

            res_tax = list(filter(lambda list_tax: list_tax['code'] == str(rows['tax_code']), list_tax))
            _logger.info(res_tax)
            if res_tax:
                for tax in res_tax:
                    vals.update({'taxes_id': [
                        (6, 0, [tax['id']])
                    ]})

            res_uom = list(filter(lambda list_uom: list_uom['code'] == str(rows['item_uom']), list_uom))
            for uom in res_uom:
                vals.update({'uom_id' : uom['id']})

            res_div = list(filter(lambda list_div: list_div['code'] == str(rows['item_div']), list_div))
            for div in res_div:
                vals.update({'division_id' : div['id']})

            res_dept = list(filter(lambda list_dept: list_dept['code'] == str(rows['item_dept']), list_dept))
            for dept in res_dept:
                vals.update({'dept_id': dept['id']})

            res_categ = list(filter(lambda list_categ: list_categ['code'] == str(rows['item_categ']), list_categ))
            for categ in res_categ:
                vals.update({'categ_id': categ['id']})

            res_subcateg = list(filter(lambda list_subcateg: list_subcateg['code'] == str(rows['item_subcateg']), list_subcateg))
            for subcateg in res_subcateg:
                vals.update({'sub_categ_id': subcateg['id']})   
            # _logger.info("CREATE PRODUCT")        
        
            context = dict(self._context or {})
            context['cron_process_download'] = True
            product_template_id = self.env['product.template'].with_context(context).create(vals)    
            _logger.info(product_template_id)
            
            #Update Product Price Store                
            product_store_vals = {
                'res_branch_id': store_id,
                'product_template_id': product_template_id.id,
                'list_price': float(rows['item_sell'])
            }
            product_template_id.update_store_product(product_store_vals)            
            #self.env.cr.commit()

            #Sync Product To CouchDB
            #product_template_id.action_sync_product_by_branch(store_id)   
            product_template_id.generate_product_json_by_branch(store_id)         
            #self.env.cr.commit()

            #Update Product Barcode
            product_barcode_vals = {
                'branch_id' : store_id,
                'product_id': product_template_id.id,
                'barcode': rows['item_barcode']
            }
            product_template_id.update_product_barcode(product_barcode_vals)           
            self.env.cr.commit()

            product_template_couchdb_id = product_template_id.product_template_data_ids.filtered(lambda r:r.branch_id == store_id)
            _logger.info("product_template_couchdb_id1")
            _logger.info(product_template_couchdb_id)
            line.couchdb_data =  product_template_couchdb_id.product_json
            
            line.state = 'done'
            line.err_msg = "Successfully"
            self.env.cr.commit()
        except Exception as e:
            line.state = 'error'
            line.err_msg = str(e)
            self.env.cr.commit()
            _logger.error(e)

    def delete_product(self, rows, store_id):
        # _logger.info("ARCHIVE PRODUCT")
        product = self.env['product.template'].search([('default_code','=', rows['item_no'])], limit=1)        
        if product:
            product.remove_product(store_id)
            self.env.cr.commit()        
        else:
            _logger.info("Delete Product - Product Not Found")

    def create_or_update_product_barcode(self, line, rows, store_id):
        pass

    def _process_download(self):
        _logger.info("run_process_download")
        active_id = self.id
        with api.Environment.manage(), self.pool.cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            self.state = 'in_progress'
            self.env.cr.commit()
            self.env['product.items.file']._import_data(active_id)
            self.env['product.items.file'].generate_data(active_id)
            self.env['product.items.file'].synchronize_data(active_id)
            
    def import_data(self):
        for row in self:
            row.message_post(body='Start Import')
            self._import_data(row.id)
            row.message_post(body='Finish Import')

    def _import_data(self, id):
        _logger.info("Start Import Data")
        product_items_file_id = self.env['product.items.file'].browse(id)
        product_items_file_id.message_post(body='Start Import')
        file_content = base64.b64decode(product_items_file_id.file)
        file_content = file_content.decode("utf-8")
        file_lines = file_content.split("\r\n")
        for line in file_lines:
            if line[0] == 'A':
                crud = 'add'
            else:
                crud = 'del'

            vals = {
                'product_items_file_id': product_items_file_id.id,
                'crud': crud,
                'name': line,
            }
            self.env['product.items.line'].create(vals)
        product_items_file_id.message_post(body='Finish Import')
        self.env.cr.commit()
        _logger.info("Finish Import Data")

    def process_generate_data(self):
        for row in self:
            self.env['product.items.file'].generate_data(row.id)

    def generate_data(self, id):
        _logger.info("Start Generate Data")
        create_bulk_docs = []
        update_bulk_docs = []
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

        product_items_file_id = self.env['product.items.file'].browse(id)
        filename = product_items_file_id.filename
        filename = filename.replace(".","")
        store_code = filename[7:11]
        store_id = self.env['res.branch'].search([('code','=', store_code)], limit=1)
        # _logger.info(store_code)

        try:          
            row_count = len(product_items_file_id.product_items_line_ids)
            row_num = 0
            row_process = 0
            store_id = store_id.id
            for line in product_items_file_id.product_items_line_ids:
                # count = count + 1
                rows = self._rows(line.name)
                if rows['rec_id'] == "A":                                 
                    check, product = self.check_product(rows['item_no'])
                    if check:
                        # _logger.info(f'Start Update {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
                        self.update_product_with_line(line, rows, product.id, store_id, uom, tax, div, dept, categ, subcateg)
                        # _logger.info(f'End Update {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
                    else:                 
                        # _logger.info(f'Start Create {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')       
                        self.create_product_with_line(line, rows, store_id, uom, tax, div, dept, categ, subcateg)
                        # _logger.info(f'End Create {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')                        
                                            
                if rows['rec_id'] == "D":
                    self.delete_product(rows, store_id)                
                self.env.cr.commit()
                # row_num =+ 1
                # row_process =+ 1
                # if row_num == 200:
                #     row_num = 0     
                #     self.env.cr.commit()                                   
                # if row_process == row_count:
                #     self.env.cr.commit()                                                               
            product_items_file_id.date_end = datetime.now()
            product_items_file_id.state = 'done'
            self.env.cr.commit()
            
        except Exception as e: 
            _logger.error(e)
            product_items_file_id.date_end = datetime.now()
            product_items_file_id.state = 'error'
            self.env.cr.commit()

        _logger.info("Stop Generate Data")

    def process_sync_data(self):
        for row in self:
            self.env['product.items.file'].synchronize_data(row.id)
        
    def synchronize_data(self, id):
        _logger.info('sync_data')                
        product_items_file_id = self.env['product.items.file'].browse(id)
        try:          
            row_count = len(product_items_file_id.product_items_line_ids)                        
            couchdb_data_ids = []
            couchdb_datas = []
            for line in product_items_file_id.product_items_line_ids:
                # _logger.info(line.id)
                if line.couchdb_data and line.state == 'done':                    
                    couchdbd_data = json.loads(line.couchdb_data)
                    # couchdb_data_ids.append(couchdbd_data['_id'])            
                    couchdb_datas.append(couchdbd_data)
            # couchdb_datas_on_server = self.get_couchdb_data_by_key(couchdb_data_ids)
            # _logger.info('couchdb_datas_on_server')                
            
            # Divide documents into batches
            batch_size = 500
            # batches = [couchdb_datas[i:i+batch_size] for i in range(0, len(couchdb_datas), batch_size)]
            batches = []
            parents = []
            for i in range(0, len(couchdb_datas), batch_size):
                batch = couchdb_datas[i:i + batch_size]
                batches.append(batch)
                parents.append(self)
            # _logger.info(len(product_items_file_id.product_items_line_ids))
            # _logger.info(len(batches))
            # Use ThreadPoolExecutor to process batches in parallel
            with ThreadPoolExecutor(max_workers=5) as executor:            
                results = executor.map(process_docs, batches, parents)  
            
            # _logger.info('results')
            # _logger.info(results)
            # for result in results:
            #     _logger.info(len(result))                
            # partial_func = partial(batches, compare_value=couchdb_data['_id'])

            # _logger.info(len(couchdb_datas_on_server))     
            # couchdb_datas_on_server = []       
            # couhcdb_datas_match = []            
            # for couchdb_data in couchdb_datas:
            #     _logger.info('couchdb_data')
            #     _logger.info(couchdb_data)               
                
                # match_data = list(filter(lambda d: d['_id'] == couchdb_data['_id'], couchdb_datas_on_server))               
                # partial_func = partial(match_doc, compare_value=couchdb_data['_id'])
                # match_data = list(filter(partial_func, couchdb_datas_on_server))
                # if not match_data:                
                #     continue
                # _logger.info(match_data)
                # _logger.info(match_data[0])
                # if len(match_data) == 1:
                #     _logger.info('match_data')           
                #     _logger.info(match_data[0])            
                #     couchdb_data.update(match_data[0])                                               
                #     couhcdb_datas_match.append(couchdb_data)
            list_results = list(results)
            # _logger.info('list_results')
            # _logger.info(len(list_results))
            self.update_couch_data_to_server(list_results)      
            # _logger.info(couhcdb_datas_match)            
            # _logger.info(len(couhcdb_datas_match))                        
            _logger.info("Update Successfully")
        except Exception as e: 
            _logger.error(e)
            
    def generate_file(self, id):
        # Example File : I5C31990.001
        count = 0
        #file_lines_length = len(file_lines)
        _logger.info("start generate file")
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

        product_items_file_id = self.env['product.items.file'].browse(id)
        try:           
            # Example : D5C31990.001            
            filename = product_items_file_id.filename
            filename = filename.replace(".","")
            store_code = filename[7:11]
            store_id = self.env['res.branch'].search([('code','=', store_code)], limit=1)
            _logger.info(store_code)

            file_content = base64.b64decode(product_items_file_id.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")

            for line in file_lines:
                count = count + 1
                rows = self._rows(line)
                # _logger.info("count")
                # _logger.info(count)
                # _logger.info(rows)
                if rows['rec_id'] == "A":                
                    if store_id:                                        
                        check, product = self.check_product(rows['item_no'])
                        if check:
                            self.update_product(rows, product.id, store_id.id, uom, tax, div, dept, categ, subcateg)
                        else:                        
                            self.create_product(rows, store_id.id, uom, tax, div, dept, categ, subcateg)                    

                if rows['rec_id'] == "D":
                    # _logger.info("ARCHIVE PRODUCT")
                    product = self.env['product.template'].search([('default_code','=', rows['item_no'])], limit=1)
                    #product.remove_product(store_id.id)
                    #product.remove_product()
                    #product.write({'active': False})
                    #self.env.cr.commit()

            product_items_file_id.date_end = datetime.now()
            product_items_file_id.state = 'done'
            self.env.cr.commit()
            
        except Exception as e: 
            _logger.error(e)
            product_items_file_id.date_end = datetime.now()
            product_items_file_id.state = 'error'
            self.env.cr.commit()

        _logger.info("stop generate file")

    def prepare_download(self, id):
        product_items_file_id = self.env['product.items.file'].browse(id)
        product_items_file_id.state = 'in_progress'
        filename = product_items_file_id.filename
        filename = filename.replace(".","")
        store_code = filename[7:11]
        _logger.info("store_code")
        _logger.info(store_code)
        try:
            file_content = base64.b64decode(product_items_file_id.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")
        except Exception as e:
            _logger.error(e)

        thread_data_list = []        
        thread_number = 6
        for line in file_lines:
            pass
    
    def cron_process_download(self):
        if self.is_use_thread:
            _logger.info("running thread")
            threaded_download = threading.Thread(target=self._process_download, args=())
            threaded_download.start()
        else:
            _logger.info("without thread")
            self._process_download()
                          
    def process_download(self): 
        try:
            #Get Store Code
            filename = self.filename
            filename = filename.replace(".","")
            store_code = filename[7:11]
            #Split Array
            file_content = base64.b64decode(self.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")           
            if self.is_use_thread:
                split_row = int(len(file_lines) / self.split_number)
                if self.split_number == 1:
                    result_lines = [file_lines]    
                else:
                    product_lines = np.array(file_lines)
                    result_lines = np.array_split(product_lines, self.split_number)             
                                
                for result_line in result_lines:
                    #Running Thread
                    # _logger.info("running thread")
                    threaded_download = threading.Thread(target=self._process_download, args=(store_code, result_line))
                    threaded_download.start()  
                    # threaded_download.join()  
                    return {'type': 'ir.actions.client', 'tag': 'reload'} 
            else:
                self._process_download(store_code, file_lines)
        except Exception as e:
            _logger.error(e)
            
    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)
    date_start = fields.Datetime('Start Date', default=datetime.now(), readonly=1)
    date_end = fields.Datetime('End Date', readonly=1)
    is_use_thread = fields.Boolean('Use Threading', default=True)
    split_number = fields.Integer('Split file', default=1)
    download_id = fields.Many2one('pos.interface.download','Download #', ondelete='set null')
    line_ids = fields.One2many('product.items.file.line', 'product_items_file_id', 'Lines')
    product_items_line_ids = fields.One2many('product.items.line','product_items_file_id', 'Item Lines')
    items_line_count = fields.Integer('Line Count', compute="get_product_items_line_count")
    state = fields.Selection([('draft','New'),('in_progress','In Progress'),('done','Finished'),('cancel','Cancel')], 'Status', default='draft')

class ProductItemsFileLine(models.Model):
    _name = 'product.items.file.line'

    product_items_file_id = fields.Many2one('product.items.file', 'Product Items File')
    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)
    state = fields.Selection([('draft','New'),('in_progress','In Progress'),('done','Finished')], 'Status', default='draft', readonly=True)

class ProductItemsLine(models.Model):
    _name = 'product.items.line'

    def action_reprocess(self): 
        pass
            
    product_items_file_id = fields.Many2one('product.items.file', 'Product Items File')
    name = fields.Text("Data")
    crud = fields.Selection([
        ('add','Add/Update'),
        ('update','Update'),
        ('del','Delete')
        ],'Type')    
    couchdb_data = fields.Text("Couchdb Data")
    is_sync = fields.Boolean('Is Synced', default=False)    
    state = fields.Selection([
        ('open','Open'),
        ('progress','Process'),
        ('syncing','Syncing'),
        ('done','Success'),
        ('error','Error')
        ],'Status', default='open', readonly=True, tracking=True)
    err_msg = fields.Char("Message", size=255)

