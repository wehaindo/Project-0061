from odoo import models, fields, api, _ 
from datetime import datetime
import os
import base64

import logging
_logger = logging.getLogger(__name__)



class PosInterfaceDownload(models.Model):
    _name = 'pos.interface.download'

    def generate_download_file(self):
        _logger.info('generate_download_file')
        vals = {
            'name': datetime.now()
        }
        res = self.env['pos.interface.download'].create(vals)
        res.process_download_file()
        res.import_download_file()

    def import_download_file(self):
        self.ensure_one()
        _logger.info('import_download_file')
        for division_id in self.division_ids:
            if division_id.state != 'done':
                division_id.state = 'in_progress'                
                division_id.process_download()
                division_id.state = 'done' 
        
        for department_id in self.department_ids:
            if department_id.state != 'done':
                department_id.state = 'in_progress'                
                department_id.process_download()
                department_id.state = 'done' 

        for category_id in self.category_ids:
            if category_id.state != 'done':
                category_id.state = 'in_progress'                
                category_id.process_download()
                category_id.state = 'done' 

        for subcategory_id in self.subcategory_ids:
            if subcategory_id.state != 'done':
                subcategory_id.state = 'in_progress'                
                subcategory_id.process_download()
                subcategory_id.state = 'done'

        for file_id in self.file_ids:
            if file_id.state != 'done':
                file_id.state = 'in_progress'                
                file_id.process_download()
                # file_id.state = 'done'

        for barcode_id in self.barcode_ids:
            if barcode_id.state != 'done':
                barcode_id.state = 'in_progress'                
                barcode_id.process_download()
                # barcode_id.state = 'done'

        for change_id in self.change_ids:
            if change_id.state != 'done':
                change_id.state = 'in_progress'                
                change_id.process_download()
                # change_id.state = 'done'

        
        for partial_id in self.partial_ids:
            if partial_id.state != 'done':
                partial_id.state = 'in_progress'                
                partial_id.process_download()
                # partial_id.state = 'done'


        for combination_id in self.combination_ids:
            if combination_id.state != 'done':
                combination_id.state = 'in_progress'                
                combination_id.process_download()
                # combination_id.state = 'done'

    def _process_download_file(self, file_path, files):
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
                    'download_id': self.id
                }
                res = self.env['res.division.file'].create(vals)
                os.remove(file_full_path)
            elif file[0] == 'T':  #Department
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id
                }
                res = self.env['res.department.file'].create(vals)  
                os.remove(file_full_path)
            elif file[0] == 'A':  #Category
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id
                }
                res = self.env['product.category.file'].create(vals)
                os.remove(file_full_path)
            elif file[0] == 'C':  #Sub Category
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id
                }
                res = self.env['product.subcategory.file'].create(vals)     
                os.remove(file_full_path) 
            elif file[0] == 'I':  #Product
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id
                }
                res = self.env['product.items.file'].create(vals)  
                os.remove(file_full_path)          
            elif file[0] == 'B':  #Product Barcode
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id
                }
                res = self.env['product.barcode.file'].create(vals)  
                os.remove(file_full_path)
            elif file[0] == 'P':  #Price Change
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id
                }
                res = self.env['price.change.file'].create(vals) 
                os.remove(file_full_path) 
            elif file[0] == 'M':  #Mix and Match Partial
                with open(file_full_path, "rb") as download_file:
                    encoded_string = base64.b64encode(download_file.read())        
                vals = {
                    'file': encoded_string,
                    'filename': file,
                    'download_id': self.id
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
                    'download_id': self.id
                }
                _logger.info("create n file")
                res = self.env['mix.and.match.comb.file'].create(vals)    
                os.remove(file_full_path)                                  
            else:
                _logger.info('File not valid')

            _logger.info(file_path + "/" + file)

    def process_download_file(self):
        self.ensure_one()
        _logger.info('process_download_file')
        # file_path = "/mnt/odoo/filestore_comm/download/pos/7001"
        file_path = "/comm/idn/download/extPos/odoo/7001"
        files = [f for f in os.listdir(file_path) if os.path.isfile(file_path + '/' + f)]
        _logger.info(files)
        d_files = []
        for file in files:
            if file[0] == 'D':
                d_files.append(file)
        
        self._process_download_file(file_path, d_files)
        
        t_files = []
        for file in files:
            if file[0] == 'T':
                t_files.append(file)

        self._process_download_file(file_path, t_files)

        a_files = []
        for file in files:
            if file[0] == 'A':
                a_files.append(file)
        
        self._process_download_file(file_path, a_files)

        c_files = []
        for file in files:
            if file[0] == 'C':
                c_files.append(file)
        self._process_download_file(file_path, c_files)

        i_files = []
        for file in files:
            if file[0] == 'I':
                i_files.append(file)

        self._process_download_file(file_path, i_files)

        b_files = []
        for file in files:
            if file[0] == 'B':
                b_files.append(file)

        self._process_download_file(file_path, b_files)

        p_files = []
        for file in files:
            if file[0] == 'P':
                p_files.append(file)

        self._process_download_file(file_path, p_files)

        m_files = []
        for file in files:
            if file[0] == 'M':
                m_files.append(file)

        self._process_download_file(file_path, m_files)                

        n_files = []
        for file in files:
            if file[0] == 'N':
                n_files.append(file)

        self._process_download_file(file_path, n_files)
        return {'type': 'ir.actions.client', 'tag': 'reload'} 
    
    def calculate_file_count(self):
        count = 0
        for row in self:
            count = count + len(self.division_ids)
            count = count + len(self.department_ids)
            count = count + len(self.category_ids)
            count = count + len(self.subcategory_ids)
            count = count + len(self.file_ids)
            count = count + len(self.barcode_ids)
            count = count + len(self.change_ids)
            count = count + len(self.partial_ids)
            count = count + len(self.combination_ids)
            self.file_count = count
        
    name = fields.Datetime("Date and Time", default=datetime.now())
    file_count = fields.Integer("File Count", compute="calculate_file_count")
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


