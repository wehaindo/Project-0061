import logging
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _
import threading
import base64

_logger = logging.getLogger(__name__)


class mix_and_match_partial_file(models.Model):
    _name= "mix.and.match.partial.file"
    _rec_name="filename"

    def _rows(self, line):
        data = {
            'mm_type': line[0:1].strip(),
            'promo_no' : line[1:13].strip(),
            'sku_no' : line[13:26].strip(),
            'mm_qty' : line[26:34].strip(),
            'mm_start_date' : line[34:42].strip(),
            'mm_end_date' : line[42:50].strip(),
            'mm_start_time' : line[50:54].strip(),
            'mm_end_time' : line[54:58].strip(),
            'mm_fix_foc_qty' : line[58:60].strip(),
            'promo_price' : line[60:77].strip(),
            'promo_disc_name' : line[77:90].strip(),
            'record_flag': line[90:92].strip(),
            'end_of_record': line[92:94].strip()
        }
        return data
    
    def check_mix_and_match_partial(self, mm_partial_code):
        res = self.env['pos.promotion'].search([('promotion_code','=', mm_partial_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res
    
    def check_mix_and_match_partial_line(self, promotion_type, promotion_id, product_id):
        
        if promotion_type == "buy_x_partial_quantity_get_special_price":
            # mes = False
            # res  = False
            # return mes, res
            res = self.env['fixed.price.multi.products'].search([("promotion_id","=", promotion_id), ("product_ids", "in", product_id),], limit=1)
            if res:
                mes = True
                return mes, res
            else:
                mes = False
                return mes, res
            
        if promotion_type == "buy_x_quantity_get_special_price":
            res = self.env['quantity.fixed.price'].search([('pos_promotion_id','=', promotion_id), ('product_id','=', product_id),], limit=1)
            if res:
                mes = True
                return mes, res
            else:
                mes = False
                return mes, res
        
        if promotion_type == "buy_x_get_y":
            res = self.env['pos.conditions'].search([('pos_promotion_rel','=', promotion_id), ('product_x_id','=', product_id),], limit=1)
            if res:
                mes = True
                return mes, res
            else:
                mes = False
                return mes, res

    def check_product(self, sku_no):
        products = self.env['product.template'].search([('default_code','=', sku_no)], limit=1)
        _logger.info('check_product')
        _logger.info(sku_no)
        _logger.info(products)
        _logger.info(products.name)
        if products:
            product_product_id = self.env['product.product'].search([('product_tmpl_id','=', products.id)], limit=1)
            if product_product_id:
                mes = True
                return mes, product_product_id
            else:
                mes = False
                return mes, products
        else:
            mes = False
            return mes, products
    
    def check_branch(self, store_no):
        store = self.env['res.branch'].search([('code','=', store_no)], limit=1)
        if store:
            mes = True
            return mes, store
        else:
            mes = False
            return mes, store
    
    def check_promotion_store(self, promotion_id, store_id):
        promo = self.env['pos.promotion'].search([('id','=', promotion_id), ('branch_ids','in', store_id)], limit=1)
        if promo:
            mes = True
            return mes
        else:
            mes = False
            return mes
    
    def create_mix_and_match_partial(self, rows, store_id):
        if rows['mm_type']:
            products_mes, products = self.check_product(rows['sku_no'])
            if products_mes:
                start_date = rows['mm_start_date']
                start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2)
                end_date = rows['mm_end_date'].replace(" ","")
                end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2)
                from_time = int(rows['mm_start_time'][:2])
                to_time = int(rows['mm_end_time'][:2])
                promo_no = "{}{}".format(rows['mm_type'], rows['promo_no'])
                vals = {
                    'active': True,
                    'promotion_code': promo_no,
                    'branch_ids': [store_id],
                    'from_date': start_date,
                    'to_date': end_date,
                    'from_time': "{}".format(from_time),
                    'to_time': "{}".format(to_time),
                }

                # BUY 1 GET PRICE
                if rows['mm_type'] == "Q":
                    if int(rows['mm_fix_foc_qty']) == 0:
                        vals.update({
                            'promotion_type': "buy_x_quantity_get_special_price",
                            'pos_quantity_fixed_price_ids': [(0,0, {
                                            'product_id': products.id,
                                            'quantity_amt': int(rows['mm_qty']),
                                            'fixed_price': rows['promo_price'],
                                        })]
                        })
                    else:
                        # BUY 1 GET 1
                        vals.update({
                            'promotion_type': "buy_x_get_y",
                            'pos_condition_ids': [(0,0, {
                                            'product_x_id': products.id,
                                            'operator': "greater_than_or_eql",
                                            'quantity': int(rows['mm_qty']),
                                            'product_y_id': products.id,
                                            'quantity_y': int(rows['mm_fix_foc_qty']),
                                        })]
                        })

                if rows['mm_type'] == "P":

                    if int(rows['mm_fix_foc_qty']) == 0:
                        vals.update({
                            'promotion_type': "buy_x_partial_quantity_get_special_price",
                            'pos_partial_quantity_fixed_price_ids': [(0,0, {
                                'product_ids': [products.id],
                                'quantity': int(rows['mm_qty']),
                                'quantity_amt': int(rows['mm_fix_foc_qty']),
                                'fixed_price': rows['promo_price'],
                            })]
                        })
                    else:
                        vals.update({
                            'promotion_type': "buy_x_partial_quantity_get_special_price",
                            'pos_partial_quantity_fixed_price_ids': [(0,0, {
                                'product_ids': [products.id],
                                'quantity': int(rows['mm_qty']),
                                'quantity_amt': int(rows['mm_fix_foc_qty']),
                                'fixed_price': rows['promo_price'],
                            })]
                        })

                _logger.info("CREATE PROMOTION")
                _logger.info(vals)
                self.env['pos.promotion'].create(vals)

    def update_mix_and_match_partial(self, rows, mm_partial_id, promotion_type, product_id, store_id):
        products_mes, products = self.check_product(rows['sku_no'])
        if products_mes:
            res = self.env['pos.promotion'].search([('id','=', mm_partial_id)], limit=1)
            promo_store_mes = self.check_promotion_store(mm_partial_id, store_id)
            vals = {}
            if promo_store_mes != True:
                vals.update({'branch_ids': [(4, store_id)]})

            if rows['mm_type'] == "Q":
                if int(rows['mm_fix_foc_qty']) == 0:
                    # 'promotion_type': "buy_x_quantity_get_special_price",
                    vals.update({
                        'pos_quantity_fixed_price_ids': [(0,0, {
                                        'product_id': products.id,
                                        'quantity_amt': int(rows['mm_qty']),
                                        'fixed_price': rows['promo_price'],
                                    })]
                    })
                else:
                    # 'promotion_type': "buy_x_get_y",
                    vals.update({
                        'pos_condition_ids': [(0,0, {
                                        'product_x_id': products.id,
                                        'operator': "greater_than_or_eql",
                                        'quantity': int(rows['mm_qty']),
                                        'product_y_id': products.id,
                                        'quantity_y': int(rows['mm_fix_foc_qty']),
                                    })]
                    })

            _logger.info("UPDATE PROMOTION")
            # _logger.info(vals)
            res.write(vals)
            if rows['mm_type'] == "P":
                # buy_x_partial_quantity_get_special_price
                for line in res.pos_partial_quantity_fixed_price_ids:
                    line.product_ids = [(4, products.id)]

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
            self.env['mix.and.match.partial.file'].generate_file(active_id)
            # new_cr.commit()

    def generate_file(self, id):
        # Example : M5C31990.001
        try:
            mix_and_match_partial_file_id = self.env['mix.and.match.partial.file'].browse(id)
            filename = mix_and_match_partial_file_id.filename
            filename = filename.replace(".","")        
            store_code = filename[7:11]
            _logger.info(store_code)

            file_content = base64.b64decode(mix_and_match_partial_file_id.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")

            for line in file_lines:
                _logger.info(str(len(line)))
                rows = self._rows(line)
                _logger.info(rows)
                
                # Check Store is ready?
                store_mes, store = self.check_branch(store_code)
                if store_mes:
                    # Check Product is ready?
                    products_mes, products = self.check_product(rows['sku_no'])
                    if products_mes:
                        # Check Promotion is ready?
                        promo_no = "{}{}".format(rows['mm_type'], rows['promo_no'])
                        promotion_mes, promotion = self.check_mix_and_match_partial(promo_no)
                        if promotion_mes:
                            self.update_mix_and_match_partial(rows, promotion.id, promotion.promotion_type, products.id, store.id)
                        else:
                            self.create_mix_and_match_partial(rows, store.id)
        except Exception as e:
            _logger.error(e)
            
    def cron_process_download(self):     
        #Running Thread
        if self.is_use_thread:
            _logger.info("running thread")
            threaded_download = threading.Thread(target=self._process_download, args=())
            threaded_download.start()   
            #threaded_download.join()        
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
    is_use_thread = fields.Boolean('Use Threading', default=True)
    download_id = fields.Many2one('pos.interface.download','Download #', ondelete='set null')
    state = fields.Selection([('draft','New'),('in_progress','In Progress'),('done','Finished'),('cancel','Cancel')], 'Status', default='draft')