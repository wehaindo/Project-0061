import logging
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _
from datetime import datetime
import threading

import base64

_logger = logging.getLogger(__name__)


class product_barcode_file(models.Model):
    _name= "product.barcode.file"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name="filename"
    _order = "date_start desc"
    
    @api.depends('product_barcode_line_ids')
    def get_product_barcode_line_count(self):
        for row in self:
            row.barcode_line_count = len(row.product_barcode_line_ids)

    def action_view_product_barcode_line(self):
        return {
            'name': _('Lines'),
            'res_model': 'product.barcode.line',
            'view_mode': 'tree,form',
            'views': [
                (self.env.ref('weha_upload_transpos.view_product_barcode_line_tree').id, 'tree'),
                (self.env.ref('weha_upload_transpos.view_product_barcode_line_form').id, 'form'),
                ],
            'type': 'ir.actions.act_window',
            'domain': [('product_barcode_file_id', 'in', self.ids)],
        }

    def _rows(self, line):
        data = {
            'rec_id' : line[0:1].strip(),
            'sku_number' : line[1:14].strip(),
            'barcode_no' : line[14:32].strip()
        }
        return data

    def check_barcode(self, sku):
        domain = [
            ('default_code','=', sku)
        ]
        res = self.env['product.tamplate'].search(domain, limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res
        
    def delete_product(self, rows, store_id):
        # _logger.info("ARCHIVE PRODUCT")
        product = self.env['product.template'].search([('default_code','=', rows['item_no'])], limit=1)        
        if product:
            product.remove_product(store_id)
            self.env.cr.commit()        
        else:
            _logger.info("Delete Product - Product Not Found")
            
    def delete_product_barcode(self, rows):
        pass 

    def _process_download(self):
        _logger.info("run_process_download")
        # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
        active_id = self.id
        _logger.info('active_id')
        _logger.info(active_id)
        with api.Environment.manage(), self.pool.cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            self.state = 'in_progress'
            self.env.cr.commit()
            self.env['product.barcode.file']._import_data(active_id)
            self.env['product.barcode.file'].generate_data(active_id)

    def generate_file(self, id):
        # Example : B5C31990.001
        product_barcode_file_id = self.env['product.barcode.file'].browse(id)
        try:
            filename = product_barcode_file_id.filename
            filename = filename.replace(".","")
            store_code = filename[7:11]
            _logger.info(store_code)

            file_content = base64.b64decode(product_barcode_file_id.file)
            file_content = file_content.decode("utf-8")
            # file_lines = file_content.split("\r\n")
            file_lines = file_content.split("\n")

            domain = [('code','=', store_code)]
            _logger.info(domain)
            branch_id = self.env['res.branch'].search(domain, limit=1)
            _logger.info(branch_id)

            if branch_id:
                _logger.info(file_lines)
                for line in file_lines:
                    _logger.info(str(len(line)))
                    rows = self._rows(line)
                    _logger.info(rows)
                    
                    if rows['rec_id'] == "A":
                        sku = rows['sku_number']
                        barcode = rows['barcode_no']
                        domain = [
                            ('default_code', '=', sku)
                        ]
                        product_template_id = self.env['product.template'].search(domain, limit=1)
                        _logger.info('product_template_id')
                        _logger.info(product_template_id)
                        if product_template_id:
                            domain = [
                                ('product_id','=', product_template_id.id),
                                ('barcode','=', barcode),
                                ('branch_id','=', branch_id.id)
                            ]
                            _logger.info("domain")
                            _logger.info(domain)
                            product_barcode_id = self.env['product.product.barcode'].search(domain, limit=1)
                            _logger.info('product_barcode_id')
                            _logger.info(product_barcode_id)
                            if product_barcode_id:
                                _logger.info('found product_barcode_id')
                            else:
                                _logger.info('create product_barcode_id')
                                vals = {
                                    "product_id": product_template_id.id,
                                    "barcode": barcode,
                                    "branch_id": branch_id.id
                                }
                                try:
                                    res = self.env['product.product.barcode'].create(vals)       
                                    _logger.info(res)
                                    self.env.cr.commit()                     
                                except Exception as e:
                                    _logger.error(e)                                

                    if rows['rec_id'] == "D":
                        pass

                product_barcode_file_id.date_end = datetime.now()
                product_barcode_file_id.state = 'done'
                self.env.cr.commit()
            else:
                product_barcode_file_id.date_end = datetime.now()
                product_barcode_file_id.state = 'cancel'
                self.env.cr.commit()
        except Exception as e:
            _logger.err(e)
            product_barcode_file_id.date_end = datetime.now()
            product_barcode_file_id.state = 'error'
            self.env.cr.commit()

    def import_data(self):
        for row in self:
            row.message_post(body='Start Import')
            self._import_data(row.id)
            row.message_post(body='Finish Import')

    def _import_data(self, id):
        try:
            _logger.info("Start Import Data")
            product_barcode_file_id = self.env['product.barcode.file'].browse(id)
            product_barcode_file_id.message_post(body='Start Import')
            file_content = base64.b64decode(product_barcode_file_id.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")
            _logger.info('file_lines')
            _logger.info(file_lines)
            for line in file_lines:
                if line[0] == 'A':
                    crud = 'add'
                else:
                    crud = 'del'

                vals = {
                    'product_barcode_file_id': product_barcode_file_id.id,
                    'crud': crud,
                    'name': line,
                }
                _logger.info(vals)            
                self.env['product.barcode.line'].create(vals)                
            product_barcode_file_id.message_post(body='Finish Import')
            _logger.info("Finish Import Data")
        except Exception as e:
            _logger.info("Error Import Data")
            _logger.error(e)
        
    def generate_data(self, id):
        try:
            product_barcode_file_id = self.env['product.barcode.file'].browse(id)
            filename = product_barcode_file_id.filename
            filename = filename.replace(".","")
            store_code = filename[7:11]
            domain = [('code','=', store_code)]
            branch_id = self.env['res.branch'].search(domain, limit=1)
            if branch_id:
                _logger.info('Branch Found')
                _logger.info(product_barcode_file_id.product_barcode_line_ids)
                for line in product_barcode_file_id.product_barcode_line_ids:
                    # _logger.info(str(len(line)))
                    _logger.info(line)
                    rows = self._rows(line.name)
                    _logger.info(rows)                    
                    if rows['rec_id'] == "A":
                        sku = rows['sku_number']
                        barcode = rows['barcode_no']
                        domain = [
                            ('default_code', '=', sku),
                            ('branch_ids','in', [branch_id.id])
                        ]
                        _logger.info(domain)
                        product_template_id = self.env['product.template'].search(domain, limit=1)
                        if product_template_id:
                            domain = [
                                ('product_id','=', product_template_id.id),
                                ('barcode','=', barcode),
                                ('branch_id','=', branch_id.id)
                            ]
                            product_barcode_id = self.env['product.product.barcode'].search(domain, limit=1)
                            if product_barcode_id:
                                _logger.info('found product_barcode_id')
                                self.env.cr.commit()          
                                line.state = 'done'
                                line.err_msg = 'Barcode Already Exist'
                                self.env.cr.commit()
                            else:
                                _logger.info('create product_barcode_id')
                                vals = {
                                    "product_id": product_template_id.id,
                                    "barcode": barcode,
                                    "branch_id": branch_id.id
                                }
                                try:
                                    res = self.env['product.product.barcode'].create(vals)       
                                    _logger.info(res)
                                    self.env.cr.commit()          
                                    line.state = 'done'
                                    line.err_msg = 'Successfully'
                                    self.env.cr.commit()
                                except Exception as e:
                                    line.state = 'error'
                                    line.err_msg = str(e)
                                    self.env.cr.commit()
                                    _logger.error(e)                                
                        else:
                            line.state = 'error'
                            line.err_msg = 'Product not found or not exist on store'
                            self.env.cr.commit()                                   

                    if rows['rec_id'] == "D":
                        _logger.info('Delete')
                        sku = rows['sku_number']
                        barcode = rows['barcode_no']
                        domain = [
                            ('default_code', '=', sku)
                        ]
                        product_template_id = self.env['product.template'].search(domain, limit=1)
                        if product_template_id:
                            _logger.info('found product_tempalte_id')
                            domain = [
                                ('product_id','=', product_template_id.id),
                                ('barcode','=', barcode),
                                ('branch_id','=', branch_id.id)
                            ]
                            _logger.info(domain)
                            product_barcode_id = self.env['product.product.barcode'].search(domain, limit=1)
                            if product_barcode_id:
                                _logger.info("product_barcode_id found")
                                try:
                                    product_barcode_id.remove_product_barcode()
                                    line.state = 'done'
                                    line.err_msg = 'Succesfully'
                                    self.env.cr.commit()
                                except Exception as e:
                                    line.state = 'error'
                                    line.err_msg = str(e)
                                    self.env.cr.commit()
                            else:
                                _logger.info("product_barcode_id not found")
                                line.state = 'error'
                                line.err_msg = 'Produt barcode not found'
                                self.env.cr.commit()
                        else:
                            line.state = 'error'
                            line.err_msg = 'Produt not found'
                            self.env.cr.commit()

                product_barcode_file_id.date_end = datetime.now()
                product_barcode_file_id.state = 'done'
                self.env.cr.commit()
            else:
                product_barcode_file_id.date_end = datetime.now()
                product_barcode_file_id.state = 'cancel'
                self.env.cr.commit()
        except Exception as e:
            _logger.err(e)
            product_barcode_file_id.date_end = datetime.now()
            product_barcode_file_id.state = 'error'
            self.env.cr.commit()

    def cron_process_download(self):     
        #Running Thread
        if self.is_use_thread:
            _logger.info("running thread")
            threaded_download = threading.Thread(target=self._process_download, args=())
            threaded_download.start()   
            # threaded_download.join()        
        else:
            self._process_download()            

    def process_download(self):     
        # Running Thread
        if self.is_use_thread:
            _logger.info("running thread")
            threaded_download = threading.Thread(target=self._process_download, args=())
            threaded_download.start()           
            # threaded_download.join()           
            return {'type': 'ir.actions.client', 'tag': 'reload'}                     
        else:
            self._process_download()

    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)    
    date_start = fields.Datetime('Start Date', default=datetime.now(), readonly=1)
    date_end = fields.Datetime('End Date', readonly=1)
    is_use_thread = fields.Boolean('Use Threading', default=True)
    product_barcode_line_ids = fields.One2many('product.barcode.line','product_barcode_file_id','Lines')
    barcode_line_count = fields.Integer('Line Count', compute="get_product_barcode_line_count")
    download_id = fields.Many2one('pos.interface.download','Download #', ondelete='set null')
    state = fields.Selection([('draft','New'),('in_progress','In Progress'),('done','Finished'),('cancel','Cancel')], 'Status', default='draft')


class ProductBarcodeLine(models.Model):
    _name = 'product.barcode.line'

    def action_reprocess(self): 
        pass
            
    product_barcode_file_id = fields.Many2one('product.barcode.file', 'Product Barcode File')
    name = fields.Text("Data")
    crud = fields.Selection([
        ('add','Add/Update'),
        ('update','Update'),
        ('del','Delete')
        ],'Type')    
    state = fields.Selection([
        ('open','Open'),
        ('progress','Process'),
        ('done','Success'),
        ('error','Error')
        ],'Status', default='open', readonly=True, tracking=True)
    err_msg = fields.Char("Message", size=255)