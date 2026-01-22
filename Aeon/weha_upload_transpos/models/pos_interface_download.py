from odoo import models, fields, api, _ 
from datetime import datetime
import os
import base64
import threading

import logging
_logger = logging.getLogger(__name__)


class PosInterfaceDownload(models.Model):
    _name = 'pos.interface.download'
    _order = "name desc"
    
    def action_import_download_file(self):
        _logger.info("running thread")
        threaded_download = threading.Thread(target=self._cron_import_download_file, args=())
        threaded_download.start()
        
    def _cron_import_download_file(self):        
        _logger.info("run_process_download")             
        active_id = self.id
        with api.Environment.manage(), self.pool.cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            self.env['pos.interface.download'].cron_import_download_file(active_id)

    def cron_import_download_file(self, id):
        _logger.info("cron_import_download_file")        
        try:
            pos_interface_download_id = self.env['pos.interface.download'].browse(id)
            _logger.info('import_download_file')
            for division_id in pos_interface_download_id.division_ids:
                if division_id.state != 'done':
                    division_id.cron_process_download()                
            
            for department_id in pos_interface_download_id.department_ids:
                if department_id.state != 'done':                
                    department_id.cron_process_download()                 

            for category_id in pos_interface_download_id.category_ids:
                if category_id.state != 'done':
                    category_id.cron_process_download()                

            for subcategory_id in pos_interface_download_id.subcategory_ids:
                if subcategory_id.state != 'done':                
                    subcategory_id.cron_process_download()                

            for file_id in pos_interface_download_id.file_ids:    
                if file_id.state != 'done':
                    file_id.cron_process_download()                

            for barcode_id in pos_interface_download_id.barcode_ids:
                if barcode_id.state != 'done':                
                    barcode_id.cron_process_download()                

            for change_id in pos_interface_download_id.change_ids:
                if change_id.state != 'done':
                    change_id.cron_process_download()                
        
            for partial_id in pos_interface_download_id.partial_ids:
                if partial_id.state != 'done':
                    partial_id.cron_process_download()

            for combination_id in pos_interface_download_id.combination_ids:
                if combination_id.state != 'done':                
                    combination_id.cron_process_download()
            return {'type': 'ir.actions.client', 'tag': 'reload'}                     
        except Exception as e:
            _logger.info(e)
            return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model 
    def cron_generate_download_file(self):             
        _logger.info('generate_download_file')    
        file_exist = self.check_file_for_download()
        if file_exist:
            _logger.info("File Exist")
            vals = {
                'name': datetime.now()
            }
            res = self.env['pos.interface.download'].create(vals)
            res.process_download_file(use_thread=False)            
            threaded_download = threading.Thread(target=res._cron_import_download_file, args=())
            threaded_download.start()

    @api.model
    def generate_download_file(self):
        _logger.info('generate_download_file')
        file_exist = self.check_file_for_download()
        if file_exist:
            _logger.info("File Exist")
            vals = {
                'name': datetime.now()
            }
            res = self.env['pos.interface.download'].create(vals)
            res.process_download_file()
            res.import_download_file()        

    def check_file_for_download(self):
        file_exist = False
        file_scope= ['D','T','A','C','I','B','P','M','N']        
        #file_paths = ["/comm/idn/download/extPos/odoo/7001","/comm/idn/download/extPos/odoo/7002"]
        file_paths = [
            "/comm/idn/download/extPos/odoo/7001",
            "/comm/idn/download/extPos/odoo/7002",
            "/comm/idn/download/extPos/odoo/7003",
            "/comm/idn/download/extPos/odoo/7004"
        ]
        for file_path in file_paths:
            files = [f for f in os.listdir(file_path) if os.path.isfile(file_path + '/' + f)]
            for file in files:
                if file[0] in file_scope:
                    file_exist = True
        return file_exist    

    def import_download_file(self):
        try:
            self.ensure_one()
            _logger.info('import_download_file')
            for division_id in self.division_ids:
                if division_id.state != 'done':
                    division_id.cron_process_download()                
            
            for department_id in self.department_ids:
                if department_id.state != 'done':                
                    department_id.cron_process_download()                 

            for category_id in self.category_ids:
                if category_id.state != 'done':
                    category_id.cron_process_download()                

            for subcategory_id in self.subcategory_ids:
                if subcategory_id.state != 'done':                
                    subcategory_id.cron_process_download()                

            _logger.info(self.file_ids)
            for file_id in self.file_ids:    
                if file_id.state != 'done':
                    file_id.cron_process_download()                

            for barcode_id in self.barcode_ids:
                if barcode_id.state != 'done':                
                    barcode_id.cron_process_download()                

            for change_id in self.change_ids:
                if change_id.state != 'done':
                    change_id.cron_process_download()                
        
            for partial_id in self.partial_ids:
                if partial_id.state != 'done':
                    partial_id.cron_process_download()

            for combination_id in self.combination_ids:
                if combination_id.state != 'done':                
                    combination_id.cron_process_download()
        except Exception as e:
            _logger.info(e)
       
    def _process_download_file(self, file_path, files, use_thread):
        self.ensure_one()
        _logger.info('_process_download_file')
        for file in files:
            file_full_path = file_path + '/' + file
            if file[0] == 'D':  #Division
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id,
                    'is_use_thread': use_thread
                }
                res = self.env['res.division.file'].create(vals)
                os.remove(file_full_path)
            elif file[0] == 'T':  #Department
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id,
                    'is_use_thread': use_thread
                }
                res = self.env['res.department.file'].create(vals)  
                os.remove(file_full_path)
            elif file[0] == 'A':  #Category
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id,
                    'is_use_thread': use_thread
                }
                res = self.env['product.category.file'].create(vals)             
                os.remove(file_full_path)
            elif file[0] == 'C':  #Sub Category
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id,
                    'is_use_thread': use_thread
                }
                res = self.env['product.subcategory.file'].create(vals)                    
                os.remove(file_full_path) 
            elif file[0] == 'I':  #Product
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id,
                    'is_use_thread': use_thread
                }
                res = self.env['product.items.file'].create(vals)           
                os.remove(file_full_path)          
            elif file[0] == 'B':  #Product Barcode
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id,
                    'is_use_thread': use_thread
                }
                res = self.env['product.barcode.file'].create(vals)                
                os.remove(file_full_path)
            elif file[0] == 'P':  #Price Change
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id,
                    'is_use_thread': use_thread
                }
                res = self.env['price.change.file'].create(vals)                
                os.remove(file_full_path) 
            elif file[0] == 'M':  #Mix and Match Partial
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id,
                    'is_use_thread': use_thread
                }
                _logger.info("create m file")
                res = self.env['mix.and.match.partial.file'].create(vals)           
                os.remove(file_full_path)  
            elif file[0] == 'N':  #Mix and Match Combination                        
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id,
                    'is_use_thread': use_thread
                }
                _logger.info("create n file")
                res = self.env['mix.and.match.comb.file'].create(vals)                 
                os.remove(file_full_path)                                  
            else:
                _logger.info('File not valid')
            
            _logger.info(file_path + "/" + file)

    def process_download_file(self, use_thread=True):
        self.ensure_one()
        _logger.info('process_download_file')
        # file_path = "/mnt/odoo/filestore_comm/download/pos/7001"
        file_paths = [
            "/comm/idn/download/extPos/odoo/7001",
            "/comm/idn/download/extPos/odoo/7002",
            "/comm/idn/download/extPos/odoo/7003",
            "/comm/idn/download/extPos/odoo/7004",
        ]

        for file_path in file_paths:
            files = [f for f in os.listdir(file_path) if os.path.isfile(file_path + '/' + f)]
            _logger.info(files)
        
            d_files = []
            for file in files:
                if file[0] == 'D':
                    d_files.append(file)
        
            self._process_download_file(file_path, d_files, use_thread)
            
            t_files = []
            for file in files:
                if file[0] == 'T':
                    t_files.append(file)

            self._process_download_file(file_path, t_files, use_thread)

            a_files = []
            for file in files:
                if file[0] == 'A':
                    a_files.append(file)
            
            self._process_download_file(file_path, a_files, use_thread)

            c_files = []
            for file in files:
                if file[0] == 'C':
                    c_files.append(file)
            self._process_download_file(file_path, c_files, use_thread)

            i_files = []
            for file in files:
                if file[0] == 'I':
                    i_files.append(file)

            self._process_download_file(file_path, i_files, use_thread)

            b_files = []
            for file in files:
                if file[0] == 'B':
                    b_files.append(file)

            self._process_download_file(file_path, b_files, use_thread)

            p_files = []
            for file in files:
                if file[0] == 'P':
                    p_files.append(file)

            self._process_download_file(file_path, p_files, use_thread)

            m_files = []
            for file in files:
                if file[0] == 'M':
                    m_files.append(file)

            self._process_download_file(file_path, m_files, use_thread)                

            n_files = []
            for file in files:
                if file[0] == 'N':
                    n_files.append(file)

            self._process_download_file(file_path, n_files, use_thread)
            self.env.cr.commit()
        
    def calculate_file_count(self):
        count = 0
        for row in self:
            count = count + len(row.division_ids)
            count = count + len(row.department_ids)
            count = count + len(row.category_ids)
            count = count + len(row.subcategory_ids)
            count = count + len(row.file_ids)
            count = count + len(row.barcode_ids)
            count = count + len(row.change_ids)
            count = count + len(row.partial_ids)
            count = count + len(row.combination_ids)
            row.file_count = count
            count = 0
        
    def calculate_division_count(self):
        for row in self:
            row.division_file_count = len(row.division_ids)

    def calculate_department_count(self):
        for row in self:
            row.department_file_count = len(row.department_ids)

    def calculate_category_count(self):
        for row in self:
            row.category_file_count = len(row.category_ids)

    def calculate_subcategory_count(self):
        for row in self:
            row.subcategory_file_count = len(row.subcategory_ids)

    def calculate_product_count(self):
        for row in self:
            row.product_item_file_count = len(row.file_ids)

    def calculate_barcode_count(self):
        for row in self:
            row.barcode_file_count = len(row.barcode_ids)

    def calculate_price_count(self):
        for row in self:
            row.price_change_file_count = len(row.change_ids)

    def calculate_partial_count(self):
        for row in self:
            row.partial_file_count = len(row.partial_ids)

    def calculate_combination_count(self):
        for row in self:
            row.combination_file_count = len(row.combination_ids)


    name = fields.Datetime("Date and Time", default=datetime.now())
    file_count = fields.Integer("File Count", compute="calculate_file_count", store=False)
    division_file_count = fields.Integer("Division", compute="calculate_division_count", store=False)
    department_file_count = fields.Integer("Department", compute="calculate_department_count", store=False)
    category_file_count = fields.Integer("Category", compute="calculate_category_count", store=False)
    subcategory_file_count = fields.Integer("Subcategory", compute="calculate_subcategory_count", store=False)
    product_item_file_count = fields.Integer("Product", compute="calculate_product_count", store=False)
    barcode_file_count = fields.Integer("Barcode", compute="calculate_barcode_count", store=False)
    price_change_file_count = fields.Integer("Price", compute="calculate_price_count", store=False)
    partial_file_count = fields.Integer("Partial", compute="calculate_partial_count", store=False)
    combination_file_count = fields.Integer("Combination", compute="calculate_combination_count", store=False)

    file_list = fields.Char('File List', size=255)
    division_ids = fields.One2many('res.division.file','download_id', 'Divisions')
    department_ids = fields.One2many('res.department.file','download_id', 'Departments')
    category_ids = fields.One2many('product.category.file','download_id', 'Categories')
    subcategory_ids = fields.One2many('product.subcategory.file','download_id', 'Sub Categories')
    file_ids = fields.One2many('product.items.file','download_id', 'Products')
    barcode_ids = fields.One2many('product.barcode.file','download_id', 'Barcodes')
    change_ids = fields.One2many('price.change.file','download_id','Price Changes')
    partial_ids = fields.One2many('mix.and.match.partial.file', 'download_id','Mix and Match Partials')
    combination_ids = fields.One2many('mix.and.match.comb.file', 'download_id','Mix and Match Combination')


