import logging
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _, registry
from datetime import datetime, timedelta
import threading

import base64

_logger = logging.getLogger(__name__)


class price_change_file(models.Model):
    _name= "price.change.file"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name="filename"
    _order = "date_start desc"

    @api.depends('price_change_line_ids')
    def get_price_change_line_count(self):
         for row in self:            
            row.items_line_count = len(row.price_change_line_ids)

    def action_view_product_items_line(self):
        return {
            'name': _('Lines'),
            'res_model': 'price.change.line',
            'view_mode': 'tree,form',
            'views': [
                (self.env.ref('weha_upload_transpos.view_price_change_line_tree').id, 'tree'),
                (self.env.ref('weha_upload_transpos.view_price_change_line_form').id, 'form'),
                ],
            'type': 'ir.actions.act_window',
            'domain': [('price_change_file_id', 'in', self.ids)],
        }

    def _rows(self, line):
        data = {
            'rec_id' : line[0:1].strip(),
            'item_no' : line[1:14].strip(),
            'prc_no' : line[14:24].strip(),
            'prc_type' : line[24:30].strip(),
            'prc_start_date' : line[30:38].strip(),
            'prc_end_date' : line[38:46].strip(),
            'prc_start_time' : line[46:50].strip(),
            'prc_end_time' : line[50:54].strip(),
            'prc_disc_rate' : line[54:60].strip(),
            'prc_disc_amt' : line[60:72].strip(),
            'prc_sell' : line[72:89].strip()
        }
        return data

    def check_product(self, sku):
        res = self.env['product.product'].search([('default_code','=', sku)], limit=1)
        if res:
            _logger.info("Product Found")
            mes = True
            return mes, res
        else:
            _logger.info("Product not Found")
            mes = False
            return mes, res

    def check_store_pricelist(self, store_id, price_type):
        _logger.info("check_store_pricelist")
        domain = [
            ('branch_id','=', store_id.id), 
            ('price_type','=', price_type)
        ]
        try:
            res = self.env['product.pricelist'].search(domain, limit=1)
            if res:        
                _logger.info("Pricelist and Price Type Found")
                mes = True
                return mes, res
            else:
                _logger.info("Pricelist and Price Type not Found")
                mes = False
                return mes, res
        except Exception as e:
            _logger.info(e)
            return False, e

    def check_product_pricelist_item(self, pricelist_id, product_id, price_change_code=False):
        
        if not price_change_code:
            res = self.env['product.pricelist.item'].search([('pricelist_id','=', pricelist_id.id),('product_tmpl_id','=',product_id.product_tmpl_id.id),('product_id','=',product_id.id)], limit=1)
        else:
            res = self.env['product.pricelist.item'].search([('pricelist_id','=', pricelist_id.id),('product_tmpl_id','=',product_id.product_tmpl_id.id),('product_id','=',product_id.id), ('prc_no','=', price_change_code)], limit=1)
        
        if res:
            _logger.info("Pricelist and Product Change Found")
            mes = True
            return mes, res
        else:
            _logger.info("Pricelist and Product Change not Found")
            mes = False
            return mes, res
        
    def create_product_pricelist_item(self, pricelist_id, product_id, rows):
        _logger.info("create_product_pricelist_item")
        # Start Date Time
        start_date = rows['prc_start_date']
        start_time = rows['prc_start_time']
        start_time = f"{start_time[:2]}:{start_time[2:]}:00"
        str_temp_start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2) + " " + start_time
        temp_start_date = datetime.strptime(str_temp_start_date,'%Y-%m-%d %H:%M:%S') + timedelta(hours=-7)
        str_start_date = temp_start_date.strftime('%Y-%m-%d %H:%M:%S')
      
        # End Date Time
        end_date = rows['prc_end_date']
        end_time = rows['prc_end_time']
        end_time = f"{end_time[:2]}:{end_time[2:]}:00"
        str_end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2) + " " + end_time
        str_temp_end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2) + " " + end_time
        temp_end_date = datetime.strptime(str_temp_end_date,'%Y-%m-%d %H:%M:%S') + timedelta(hours=-7)
        str_end_date = temp_end_date.strftime('%Y-%m-%d %H:%M:%S')

        vals = {
            'prc_no': rows['prc_no'],
            'fixed_price': rows['prc_sell'],
            'date_start': str_start_date,
            'date_end': str_end_date,
            'pricelist_id': pricelist_id.id,
            'product_tmpl_id':  product_id.product_tmpl_id.id, #Product Template
            'product_id':  product_id.id #Product ID
        }

        _logger.info("CREATE PRICELIST ITEMS")
        _logger.info(vals)
        try:
            res = self.env['product.pricelist.item'].create(vals)
            self.env.cr.commit()
            _logger.info("Create Pricelist Item Successfully")
        except Exception as e:
            _logger.error("Error Create Pricelist Item")
            _logger.error(e)

    def update_product_pricelist_item(self, pricelist_item_id, rows):
        _logger.info("update_product_pricelist_item")        
        # Start Date Time
        start_date = rows['prc_start_date']
        start_time = rows['prc_start_time']
        start_time = f"{start_time[:2]}:{start_time[2:]}:00"
        str_temp_start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2) + " " + start_time
        temp_start_date = datetime.strptime(str_temp_start_date,'%Y-%m-%d %H:%M:%S') + timedelta(hours=-7)
        str_start_date = temp_start_date.strftime('%Y-%m-%d %H:%M:%S')
        
        # End Date Time
        end_date = rows['prc_end_date']
        end_time = rows['prc_end_time']
        end_time = f"{end_time[:2]}:{end_time[2:]}:00"
        str_temp_end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2) + " " + end_time
        temp_end_date = datetime.strptime(str_temp_end_date,'%Y-%m-%d %H:%M:%S') + timedelta(hours=-7)
        str_end_date = temp_end_date.strftime('%Y-%m-%d %H:%M:%S')
        
        res = self.env['product.pricelist.item'].search([('id','=', pricelist_item_id.id)])
        vals = {
            # 'prc_no': rows['prc_no'],
            'fixed_price': rows['prc_sell'],
            'date_start': str_start_date,
            'date_end': str_end_date,
        }

        _logger.info("UPDATE PRICELIST ITEMS")
        _logger.info(vals)
        res.write(vals)
        self.env.cr.commit()

    def delete_product_pricelist_item(self, pricelist_item_id, rows):
        pass 

    def create_product_pricelist_item_with_line(self, line, pricelist_id, product_id, rows):
        _logger.info("create_product_pricelist_item")
        try:
            # Start Date Time
            start_date = rows['prc_start_date']
            start_time = rows['prc_start_time']
            start_time = f"{start_time[:2]}:{start_time[2:]}:00"
            str_temp_start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2) + " " + start_time
            temp_start_date = datetime.strptime(str_temp_start_date,'%Y-%m-%d %H:%M:%S') + timedelta(hours=-7)
            str_start_date = temp_start_date.strftime('%Y-%m-%d %H:%M:%S')
        
            # End Date Time
            end_date = rows['prc_end_date']
            end_time = rows['prc_end_time']
            end_time = f"{end_time[:2]}:{end_time[2:]}:00"
            str_end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2) + " " + end_time
            str_temp_end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2) + " " + end_time
            temp_end_date = datetime.strptime(str_temp_end_date,'%Y-%m-%d %H:%M:%S') + timedelta(hours=-7)
            str_end_date = temp_end_date.strftime('%Y-%m-%d %H:%M:%S')

            vals = {
                'prc_no': rows['prc_no'],
                'fixed_price': rows['prc_sell'],
                'date_start': str_start_date,
                'date_end': str_end_date,
                'pricelist_id': pricelist_id.id,
                'product_tmpl_id':  product_id.product_tmpl_id.id, #Product Template
                'product_id':  product_id.id #Product ID
            }

            _logger.info("CREATE PRICELIST ITEMS")            
            self.env['product.pricelist.item'].create(vals)
            self.env.cr.commit()
            line.state = 'done'
            line.err_msg = 'Successfully'
            self.env.cr.commit()            
        except Exception as e:
            _logger.error("Error Create Pricelist Item")
            line.state = 'error'
            line.err_msg = str(e)
            self.env.cr.commit()            
            _logger.error(e)

    def update_product_pricelist_item_with_line(self, line, pricelist_item_id, rows):
        _logger.info("update_product_pricelist_item")
        try:
            # Start Date Time
            start_date = rows['prc_start_date']
            start_time = rows['prc_start_time']
            start_time = f"{start_time[:2]}:{start_time[2:]}:00"
            str_temp_start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2) + " " + start_time
            temp_start_date = datetime.strptime(str_temp_start_date,'%Y-%m-%d %H:%M:%S') + timedelta(hours=-7)
            str_start_date = temp_start_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # End Date Time
            end_date = rows['prc_end_date']
            end_time = rows['prc_end_time']
            end_time = f"{end_time[:2]}:{end_time[2:]}:00"
            str_temp_end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2) + " " + end_time
            temp_end_date = datetime.strptime(str_temp_end_date,'%Y-%m-%d %H:%M:%S') + timedelta(hours=-7)
            str_end_date = temp_end_date.strftime('%Y-%m-%d %H:%M:%S')
            
            product_pricelist_item_id = self.env['product.pricelist.item'].search([('id','=', pricelist_item_id.id)])
            if product_pricelist_item_id:
                vals = {
                    # 'prc_no': rows['prc_no'],
                    'fixed_price': rows['prc_sell'],
                    'date_start': str_start_date,
                    'date_end': str_end_date,
                }

                _logger.info("UPDATE PRICELIST ITEMS")
                _logger.info(vals)
                product_pricelist_item_id.write(vals)
                self.env.cr.commit()
                line.state = 'done'
                line.err_msg = 'Successfully'
                self.env.cr.commit()            
            else:
                line.state = 'error'
                line.err_msg = 'Product Pricelist Item not found'
                self.env.cr.commit()            
                
        except Exception as e:
            line.state = 'error'
            line.err_msg = str(e)
            self.env.cr.commit()            
            _logger.error(e)

    def delete_product_pricelist_item_with_line(self, line, pricelist_item_id, rows):
        pass

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
            self.env.cr.commit()
            # self.env['price.change.file'].generate_file(active_id)
            self.env['price.change.file']._import_data(active_id)
            self.env['price.change.file'].generate_data(active_id)

    def generate_file(self, id):
        # Example : P5C31990.001
        _logger.info("start generate file")
        price_change_file_id = self.env['price.change.file'].browse(id)            
        try:
            filename = price_change_file_id.filename
            filename = filename.replace(".","")
            store_code = filename[7:11]
            _logger.info(store_code)

            file_content = base64.b64decode(price_change_file_id.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")

            _logger.info("start_branch_id")
            res_branch_id = self.env['res.branch'].search([("code","=", store_code)], limit=1)        
            
            _logger.info("end_branch_id")

            for line in file_lines:
                _logger.info(str(len(line)))
                rows = self._rows(line)
                _logger.info(rows)

                if rows['rec_id'] == "A":
                    _logger.info("A")
                    # Check Product Item No for get branch_id
                    product_mes, product = self.check_product(rows['item_no'])
                    if product_mes:
                        _logger.info("product_found")
                        # Check Product Pricelist by branch_id & prc_type
                        pricelist_mes, pricelist = self.check_store_pricelist(res_branch_id, rows['prc_type'])
                        if pricelist_mes:
                            # Check Product Pricelist Items by pricelist_id & prc_no
                            check, pricelist_item = self.check_product_pricelist_item(pricelist, product, rows['prc_no'])
                            if check:
                                # UPDATE
                                self.update_product_pricelist_item(pricelist_item, rows)
                            else:
                                # CREATE                            
                                self.create_product_pricelist_item(pricelist, product, rows)

                if rows['rec_id'] == "D":
                    _logger.info("D")
                    product_pricelist_item = self.env['product.pricelist.item'].search([('base_pricelist_id','=', pricelist.id), ('prc_no','=', rows['prc_no'])])
                    #product_pricelist_item.write({'active': False})
                    #self.env.cr.commit()

            price_change_file_id.state = 'done'
            price_change_file_id.date_end = datetime.now()                                
            self.env.cr.commit()
            _logger.info("stop generate file")

        except Exception as e:
            _logger.error(e)
            price_change_file_id.state = 'error'
            price_change_file_id.date_end = datetime.now()                                
            self.env.cr.commit()

    def import_data(self):
        for row in self:
            row.message_post(body='Start Import')
            self._import_data(row.id)
            row.message_post(body='Finish Import')

    def _import_data(self, id):
        _logger.info("Start Import Data")
        try:
            price_change_file_id = self.env['price.change.file'].browse(id)
            # price_change_line_id.message_post(body='Start Import')
            file_content = base64.b64decode(price_change_file_id.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")
            for line in file_lines:
                if line[0] == 'A':
                    crud = 'add'
                else:
                    crud = 'del'

                vals = {
                    'price_change_file_id': price_change_file_id.id,
                    'crud': crud,
                    'name': line,
                }
                self.env['price.change.line'].create(vals)
            # price_change_line_id.message_post(body='Finish Import')
            _logger.info("Finish Import Data")
        except Exception as e:
            _logger.error(e)
    
    def generate_data(self,id):
        # Example : P5C31990.001
        _logger.info("start generate file")
        price_change_file_id = self.env['price.change.file'].browse(id)            
        try:
            filename = price_change_file_id.filename
            filename = filename.replace(".","")
            store_code = filename[7:11]
            _logger.info(store_code)

            _logger.info("start_branch_id")
            res_branch_id = self.env['res.branch'].search([("code","=", store_code)], limit=1)                                

            for line in price_change_file_id.price_change_line_ids:
                _logger.info(str(len(line)))
                rows = self._rows(line.name)
                _logger.info(rows)

                if rows['rec_id'] == "A":
                    _logger.info("A")
                    # Check Product Item No for get branch_id
                    product_mes, product = self.check_product(rows['item_no'])
                    if product_mes:
                        _logger.info("product_found")
                        # Check Product Pricelist by branch_id & prc_type
                        pricelist_mes, pricelist = self.check_store_pricelist(res_branch_id, rows['prc_type'])
                        if pricelist_mes:
                            # Check Product Pricelist Items by pricelist_id & prc_no
                            check, pricelist_item = self.check_product_pricelist_item(pricelist, product, rows['prc_no'])
                            if check:
                                # UPDATE
                                self.update_product_pricelist_item_with_line(line, pricelist_item, rows)
                            else:
                                # CREATE                            
                                self.create_product_pricelist_item_with_line(line, pricelist, product, rows)
                        else:
                            line.state = "error"
                            line.err_msg = "Pricelist not found"
                    else:
                        line.state="error"
                        line.err_msg = "Product not found"

                if rows['rec_id'] == "D":
                    _logger.info("D")
                    pricelist_mes, pricelist = self.check_store_pricelist(res_branch_id, rows['prc_type'])
                    if pricelist_mes:
                        product_pricelist_item = self.env['product.pricelist.item'].search([('base_pricelist_id','=', pricelist.id), ('prc_no','=', rows['prc_no'])])
                        product_pricelist_item.remove_product_pricelist_item()
                    #product_pricelist_item.write({'active': False})
                    #self.env.cr.commit()

            price_change_file_id.state = 'done'
            price_change_file_id.date_end = datetime.now()                                
            self.env.cr.commit()
            _logger.info("stop generate file")

        except Exception as e:
            _logger.error(e)
            price_change_file_id.state = 'error'
            price_change_file_id.date_end = datetime.now()                                
            self.env.cr.commit()

    def cron_process_download(self):     
        #Running Thread
        if self.is_use_thread:
            _logger.info("running thread")
            threaded_download = threading.Thread(target=self._process_download, args=())
            threaded_download.start()
        else:
            self._process_download()            

    def process_download(self):     
        #Running Thread
        if self.is_use_thread:
            _logger.info("running thread")
            threaded_download = threading.Thread(target=self._process_download, args=())
            threaded_download.start()           
            #threaded_download.join()
            return {'type': 'ir.actions.client', 'tag': 'reload'}                     
        else:
            self._process_download()

    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)
    date_start = fields.Datetime('Start Date', default=datetime.now(), readonly=1)
    date_end = fields.Datetime('End Date', readonly=1)
    is_use_thread = fields.Boolean('Use Threading', default=True)
    download_id = fields.Many2one('pos.interface.download','Download #', ondelete='set null')
    price_change_line_ids = fields.One2many('price.change.line','price_change_file_id', 'Item Lines')
    items_line_count = fields.Integer('Line Count', compute="get_price_change_line_count")
    state = fields.Selection([('draft','New'),('in_progress','In Progress'),('done','Finished'),('cancel','Cancel')], 'Status', default='draft')


class PriceChangeLine(models.Model):
    _name = 'price.change.line'

    def action_reprocess(self): 
        pass
            
    price_change_file_id = fields.Many2one('price.change.file', 'Price Change File')
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
